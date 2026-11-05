import asyncio
import logging
import random

import httpx
from app.core.config import settings
from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)

RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}
MAX_ATTEMPTS = 4


class GeminiUpstreamError(RuntimeError):
    """Sanitized Gemini API failure; deliberately never includes request URL or API key."""

    def __init__(self, status_code: int | None, message: str):
        self.status_code = status_code
        super().__init__(message)


def _retry_delay(response: httpx.Response | None, attempt: int) -> float:
    if response is not None:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return min(30.0, max(0.0, float(retry_after)))
            except ValueError:
                pass
    return min(8.0, 1.0 * (2 ** attempt)) + random.uniform(0.0, 0.25)


class GeminiProvider(LLMProvider):
    def __init__(self, model: str | None = None):
        self.model = model or settings.gemini_model
        key = settings.gemini_api_key.get_secret_value() if settings.gemini_api_key else None
        if not key:
            raise ValueError("GEMINI_API_KEY is required for GeminiProvider")
        self.api_key = key
        self.base_url = settings.gemini_base_url.rstrip("/")

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
        url = f"{self.base_url}/models/{self.model}:generateContent"
        data = None
        async with httpx.AsyncClient(timeout=120.0) as client:
            for attempt in range(MAX_ATTEMPTS):
                response = None
                try:
                    response = await client.post(url, params={"key": self.api_key}, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    break
                except httpx.HTTPStatusError as exc:
                    status = exc.response.status_code
                    if status not in RETRYABLE_STATUS_CODES:
                        logger.error("Gemini API returned non-retryable HTTP %s", status)
                        raise GeminiUpstreamError(status, f"Gemini API request failed (HTTP {status})") from None
                    if attempt == MAX_ATTEMPTS - 1:
                        logger.error("Gemini API remained unavailable after %s attempts (HTTP %s)", MAX_ATTEMPTS, status)
                        raise GeminiUpstreamError(status, f"Gemini API temporarily unavailable (HTTP {status}) after {MAX_ATTEMPTS} attempts") from None
                    delay = _retry_delay(response, attempt)
                    logger.warning("Gemini API returned HTTP %s; retrying attempt %s/%s in %.1fs", status, attempt + 2, MAX_ATTEMPTS, delay)
                    await asyncio.sleep(delay)
                except (httpx.TimeoutException, httpx.TransportError) as exc:
                    if attempt == MAX_ATTEMPTS - 1:
                        logger.error("Gemini transport failed after %s attempts (%s)", MAX_ATTEMPTS, type(exc).__name__)
                        raise GeminiUpstreamError(None, f"Gemini API connection failed after {MAX_ATTEMPTS} attempts") from None
                    delay = _retry_delay(None, attempt)
                    logger.warning("Gemini transport error %s; retrying attempt %s/%s in %.1fs", type(exc).__name__, attempt + 2, MAX_ATTEMPTS, delay)
                    await asyncio.sleep(delay)

        candidates = (data or {}).get("candidates") or []
        if not candidates:
            raise GeminiUpstreamError(None, "Gemini returned no candidates")
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts if part.get("text"))
        if not text:
            raise GeminiUpstreamError(None, "Gemini returned an empty response")
        return text
