import asyncio
import logging
import random

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import httpx

from app.core.config import settings
from app.services.llm.base import LLMProvider


logger = logging.getLogger(__name__)

RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}


class GeminiUpstreamError(RuntimeError):
    """Sanitized Gemini API failure; excludes URLs and secrets."""

    def __init__(
        self,
        status_code: int | None,
        message: str = "Gemini service is temporarily unavailable",
    ):
        self.status_code = status_code
        self.retryable = (
            status_code in RETRYABLE_STATUS_CODES
            or status_code is None
        )
        super().__init__(message)


class GeminiProvider(LLMProvider):

    def __init__(self, model: str | None = None):
        self.model = model or settings.gemini_model

        configured_fallback = getattr(
            settings,
            "gemini_fallback_model",
            None,
        )

        self.fallback_model = (
            configured_fallback
            if configured_fallback
            and configured_fallback != self.model
            else None
        )

        key = (
            settings.gemini_api_key.get_secret_value()
            if settings.gemini_api_key
            else None
        )

        if not key:
            raise ValueError(
                "GEMINI_API_KEY is required for GeminiProvider"
            )

        self.api_key = key
        self.base_url = settings.gemini_base_url.rstrip("/")

        self.max_attempts = 4
        self.max_retry_delay = 8.0

    def _get_retry_delay(
        self,
        retry_after: str | None,
        attempt: int,
    ) -> float:
        """Calculate retry delay from Retry-After or exponential backoff."""

        delay = 0.0

        if retry_after:
            try:
                delay = max(0.0, float(retry_after))

            except (ValueError, TypeError):
                try:
                    retry_date = parsedate_to_datetime(retry_after)

                    if retry_date.tzinfo is None:
                        retry_date = retry_date.replace(
                            tzinfo=timezone.utc
                        )

                    delay = max(
                        0.0,
                        (
                            retry_date - datetime.now(timezone.utc)
                        ).total_seconds(),
                    )

                except (
                    ValueError,
                    TypeError,
                    OverflowError,
                ):
                    delay = 0.0

        if delay <= 0.0:
            delay = (
                min(
                    self.max_retry_delay,
                    0.75 * (2 ** attempt),
                )
                + random.uniform(0.0, 0.25)
            )

        return min(30.0, delay)

    async def _generate_with_model(
        self,
        client: httpx.AsyncClient,
        model: str,
        payload: dict,
    ) -> dict:

        url = f"{self.base_url}/models/{model}:generateContent"

        for attempt in range(self.max_attempts):

            try:
                response = await client.post(
                    url,
                    headers={
                        "x-goog-api-key": self.api_key,
                    },
                    json=payload,
                )

                status = response.status_code

                if status in RETRYABLE_STATUS_CODES:

                    if attempt == self.max_attempts - 1:
                        logger.error(
                            "Gemini failed after %s attempts. HTTP status=%s",
                            self.max_attempts,
                            status,
                        )
                        raise GeminiUpstreamError(status)

                    retry_after = response.headers.get("Retry-After")

                    delay = self._get_retry_delay(
                        retry_after,
                        attempt,
                    )

                    logger.warning(
                        "Gemini HTTP %s. Retry %s/%s in %.2f seconds.",
                        status,
                        attempt + 1,
                        self.max_attempts - 1,
                        delay,
                    )

                    await asyncio.sleep(delay)
                    continue

                if response.is_error:
                    logger.error(
                        "Gemini rejected request. HTTP status=%s",
                        status,
                    )

                    raise GeminiUpstreamError(
                        status,
                        "Gemini API rejected the request",
                    )

                try:
                    data = response.json()

                except ValueError:
                    logger.error(
                        "Gemini returned invalid JSON. HTTP status=%s",
                        status,
                    )

                    raise GeminiUpstreamError(
                        status,
                        "Gemini returned an invalid JSON response",
                    ) from None

                if not isinstance(data, dict):
                    raise GeminiUpstreamError(
                        status,
                        "Gemini returned an unexpected response",
                    )

                return data

            except (
                httpx.TimeoutException,
                httpx.TransportError,
            ):

                if attempt == self.max_attempts - 1:
                    logger.error(
                        "Gemini network failure after %s attempts.",
                        self.max_attempts,
                    )

                    raise GeminiUpstreamError(None) from None

                delay = (
                    min(
                        self.max_retry_delay,
                        0.75 * (2 ** attempt),
                    )
                    + random.uniform(0.0, 0.25)
                )

                logger.warning(
                    "Gemini network failure. Retry %s/%s in %.2f seconds.",
                    attempt + 1,
                    self.max_attempts - 1,
                    delay,
                )

                await asyncio.sleep(delay)

        raise GeminiUpstreamError(None)

    async def generate(
        self,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float = 0.0,
    ) -> str:

        contents = []

        if system:
            contents.append({
                "role": "user",
                "parts": [{"text": system}],
            })

        contents.append({
            "role": "user",
            "parts": [{"text": prompt}],
        })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json",
            },
        }

        # Configurable request pacing.
        request_interval = getattr(
    settings,
    "gemini_request_interval_seconds",
    0.0,
)

        if request_interval > 0:
            await asyncio.sleep(request_interval)

        async with httpx.AsyncClient(
            timeout=120.0
        ) as client:

            try:
                data = await self._generate_with_model(
                    client,
                    self.model,
                    payload,
                )

            except GeminiUpstreamError as primary_error:

                if (
                    not primary_error.retryable
                    or not self.fallback_model
                ):
                    raise

                logger.warning(
                    "Primary Gemini model failed. "
                    "Status code=%s. Trying fallback model=%s",
                    primary_error.status_code,
                    self.fallback_model,
                )

                try:
                    data = await self._generate_with_model(
                        client,
                        self.fallback_model,
                        payload,
                    )

                except GeminiUpstreamError as fallback_error:
                    logger.error(
                        "Gemini fallback model also failed. "
                        "Status code=%s",
                        fallback_error.status_code,
                    )
                    raise

        candidates = data.get("candidates")

        if not isinstance(candidates, list) or not candidates:
            raise ValueError(
                "Gemini returned no candidates"
            )

        candidate = candidates[0]

        if not isinstance(candidate, dict):
            raise ValueError(
                "Gemini returned an unexpected candidate structure"
            )

        content = candidate.get("content")

        if not isinstance(content, dict):
            raise ValueError(
                "Gemini returned an unexpected content structure"
            )

        parts = content.get("parts")

        if not isinstance(parts, list):
            raise ValueError(
                "Gemini returned an unexpected parts structure"
            )

        text_parts = []

        for part in parts:

            if not isinstance(part, dict):
                raise ValueError(
                    "Gemini returned an unexpected response part"
                )

            part_text = part.get("text")

            if part_text is not None:

                if not isinstance(part_text, str):
                    raise ValueError(
                        "Gemini returned invalid response text"
                    )

                text_parts.append(part_text)

        text = "".join(text_parts)

        if not text.strip():
            raise ValueError(
                "Gemini returned an empty response"
            )

        return text