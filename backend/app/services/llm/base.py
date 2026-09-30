from abc import ABC, abstractmethod
from typing import Any

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, *, system: str | None = None, temperature: float = 0.0) -> str:
        raise NotImplementedError

    async def structured(self, prompt: str, *, system: str | None = None, temperature: float = 0.0) -> dict[str, Any]:
        import json
        raw = await self.generate(prompt, system=system, temperature=temperature)
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError("LLM did not return valid JSON") from exc
