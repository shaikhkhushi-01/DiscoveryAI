from abc import ABC, abstractmethod
from typing import Any
import json
import re

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, *, system: str | None = None, temperature: float = 0.0) -> str:
        raise NotImplementedError

    async def structured(self, prompt: str, *, system: str | None = None, temperature: float = 0.0) -> dict[str, Any]:
        raw = await self.generate(prompt, system=system, temperature=temperature)
        text = raw.strip()
        # Tolerate markdown fences or harmless surrounding text from providers.
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\s*```$", "", text).strip()

        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start < 0 or end <= start:
                raise ValueError("LLM did not return valid JSON")
            try:
                value = json.loads(text[start : end + 1])
            except json.JSONDecodeError as exc:
                raise ValueError("LLM did not return valid JSON") from exc

        if not isinstance(value, dict):
            raise ValueError("LLM structured response must be a JSON object")
        return value
