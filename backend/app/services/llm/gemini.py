import httpx
from app.core.config import settings
from app.services.llm.base import LLMProvider


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
            },
        }
        url = f"{self.base_url}/models/{self.model}:generateContent"
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, params={"key": self.api_key}, json=payload)
            response.raise_for_status()
            data = response.json()

        candidates = data.get("candidates") or []
        if not candidates:
            raise ValueError("Gemini returned no candidates")
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts if part.get("text"))
        if not text:
            raise ValueError("Gemini returned an empty response")
        return text
