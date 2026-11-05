import asyncio
import random
import logging

import httpx

from app.core.config import settings
from app.services.llm.base import LLMProvider


logger = logging.getLogger(__name__)
RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}


class GeminiUpstreamError(RuntimeError):
    """Sanitized Gemini API failure; deliberately excludes request URLs and secrets."""

    def __init__(self, status_code: int | None, message: str = "Gemini service is temporarily unavailable"):
        self.status_code = status_code
        self.retryable = status_code in RETRYABLE_STATUS_CODES or status_code is None
        super().__init__(message)


class GeminiProvider(LLMProvider):
    def __init__(self, model: str | None = None):
        self.model = model or settings.gemini_model
        configured_fallback = getattr(settings, "gemini_fallback_model", None)
        self.fallback_model = configured_fallback if configured_fallback and configured_fallback != self.model else None
        key = settings.gemini_api_key.get_secret_value() if settings.gemini_api_key else None
        if not key:
            raise ValueError("GEMINI_API_KEY is required for GeminiProvider")
        self.api_key = key
        self.base_url = settings.gemini_base_url.rstrip("/")
        self.max_attempts = 4

    async def _generate_with_model(self, client: httpx.AsyncClient, model: str, payload: dict) -> dict:
        url = f"{self.base_url}/models/{model}:generateContent"
        for attempt in range(self.max_attempts):
            try:
                response = await client.post(
                    url,
                    headers={"x-goog-api-key": self.api_key},
                    json=payload,
                )
                if response.status_code in RETRYABLE_STATUS_CODES:
                    if attempt == self.max_attempts - 1:
                        raise GeminiUpstreamError(response.status_code)
                    retry_after = response.headers.get("Retry-After")
                    try:
                        delay = min(30.0, max(0.0, float(retry_after))) if retry_after else 0.0
                    except ValueError:
                        delay = 0.0
                    if delay == 0.0:
                        delay = min(8.0, 0.75 * (2 ** attempt)) + random.uniform(0.0, 0.25)
                    await asyncio.sleep(delay)
                    continue
                if response.is_error:
                    raise GeminiUpstreamError(response.status_code, "Gemini API rejected the request")
                return response.json()
            except (httpx.TimeoutException, httpx.TransportError):
                if attempt == self.max_attempts - 1:
                    raise GeminiUpstreamError(None) from None
                delay = min(8.0, 0.75 * (2 ** attempt)) + random.uniform(0.0, 0.25)
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
            contents.append({"role": "user", "parts": [{"text": system}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json",
            },
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                data = await self._generate_with_model(client, self.model, payload)
            except GeminiUpstreamError as primary_error:
                if not primary_error.retryable or not self.fallback_model:
                    raise
                logger.warning(
                    "Primary Gemini model unavailable after retries; trying configured fallback model=%s",
                    self.fallback_model,
                )
                try:
                    data = await self._generate_with_model(client, self.fallback_model, payload)
                except GeminiUpstreamError:
                    raise

        candidates = data.get("candidates") or []
        if not candidates:
            raise ValueError("Gemini returned no candidates")
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts if part.get("text"))
        if not text:
            raise ValueError("Gemini returned an empty response")
        return text
