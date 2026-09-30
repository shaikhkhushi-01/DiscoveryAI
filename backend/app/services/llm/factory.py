from app.core.config import settings
from app.services.llm.base import LLMProvider
from app.services.llm.ollama import OllamaProvider
from app.services.llm.openai import OpenAIProvider

def get_llm_provider(provider: str | None = None) -> LLMProvider:
    selected = (provider or settings.llm_provider).lower()
    if selected == "ollama": return OllamaProvider()
    if selected == "openai": return OpenAIProvider()
    raise ValueError(f"Unsupported LLM provider: {selected}")
