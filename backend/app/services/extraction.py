import json
from typing import Any
from app.services.llm.base import LLMProvider
from app.services.llm.prompts import SCIENTIFIC_EXTRACTION_SYSTEM, scientific_extraction_prompt

class ScientificExtractor:
    def __init__(self, provider: LLMProvider): self.provider = provider
    async def extract(self, text: str) -> dict[str, Any]:
        result = await self.provider.structured(scientific_extraction_prompt(text), system=SCIENTIFIC_EXTRACTION_SYSTEM)
        return result
