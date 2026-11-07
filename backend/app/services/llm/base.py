from abc import ABC, abstractmethod
from typing import Any
import json
import re


def _parse_object(raw: str) -> dict[str, Any]:
    text = raw.strip().lstrip(chr(65279))
    fence = chr(96) * 3
    if text.startswith(fence):
        text = text[len(fence):]
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()
        if text.endswith(fence):
            text = text[:-len(fence)].strip()

    candidates = [text]
    start = text.find("{")
    if start >= 0:
        depth = 0
        quoted = False
        escaped = False
        for index in range(start, len(text)):
            char = text[index]
            if quoted:
                if escaped:
                    escaped = False
                elif ord(char) == 92:
                    escaped = True
                elif char == '"':
                    quoted = False
            elif char == '"':
                quoted = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    candidates.append(text[start:index + 1])
                    break

    for candidate in candidates:
        candidate = re.sub(r",\s*([}\]])", r"\1", candidate)
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, list) and len(value) == 1 and isinstance(value[0], dict):
            value = value[0]
        if isinstance(value, dict):
            return value
    raise ValueError("LLM structured response must be a JSON object")


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, *, system: str | None = None, temperature: float = 0.0) -> str:
        raise NotImplementedError

    async def structured(self, prompt: str, *, system: str | None = None, temperature: float = 0.0) -> dict[str, Any]:
        raw = await self.generate(prompt, system=system, temperature=temperature)
        try:
            return _parse_object(raw)
        except ValueError:
            # One bounded formatting repair; the model is told not to infer or add content.
            repaired = await self.generate(
                "Convert this response to one valid JSON object. Preserve only "
                "the information present. Return JSON only.\n\n" + raw[:12000],
                system="You are a strict JSON formatter. Do not add facts.",
                temperature=0.0,
            )
            return _parse_object(repaired)
