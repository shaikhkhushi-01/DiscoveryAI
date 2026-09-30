import httpx
from app.core.config import settings
from app.services.llm.base import LLMProvider

class OllamaProvider(LLMProvider):
    def __init__(self, model: str = "llama3.2"):
        self.model = model
        self.base_url = settings.ollama_base_url.rstrip("/")

    async def generate(self, prompt: str, *, system: str | None = None, temperature: float = 0.0) -> str:
        payload = {"model": self.model, "prompt": prompt, "stream": False, "options": {"temperature": temperature}}
        if system:
            payload["system"] = system
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return str(data.get("response", ""))
