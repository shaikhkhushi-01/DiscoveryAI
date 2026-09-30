import json
from openai import AsyncOpenAI
from app.core.config import settings
from app.services.llm.base import LLMProvider

class OpenAIProvider(LLMProvider):
    def __init__(self, model: str | None = None):
        self.model = model or settings.openai_model
        key = settings.openai_api_key.get_secret_value() if settings.openai_api_key else None
        if not key:
            raise ValueError("OPENAI_API_KEY is required for OpenAIProvider")
        self.client = AsyncOpenAI(api_key=key)

    async def generate(self, prompt: str, *, system: str | None = None, temperature: float = 0.0) -> str:
        messages = []
        if system: messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = await self.client.chat.completions.create(model=self.model, messages=messages, temperature=temperature)
        return response.choices[0].message.content or ""
