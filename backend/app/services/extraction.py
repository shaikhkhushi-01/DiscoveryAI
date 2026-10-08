from typing import Any
from app.services.llm.base import LLMProvider
from app.services.llm.prompts import SCIENTIFIC_EXTRACTION_SYSTEM, scientific_extraction_prompt


EXTRACTION_KEYS = (
    "topics",
    "keywords",
    "methods",
    "algorithms",
    "datasets",
    "problems",
    "applications",
    "domains",
    "metrics",
    "baselines",
    "limitations",
    "future_work",
)

MAX_CHUNK_CHARS = 12000


class ScientificExtractor:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def extract(self, text: str) -> dict[str, Any]:
        text = text.strip()
        if not text:
            raise ValueError("No scientific text supplied for extraction")

        chunks = [
            text[start : start + MAX_CHUNK_CHARS]
            for start in range(0, len(text), MAX_CHUNK_CHARS)
        ]

        merged: dict[str, Any] = {key: [] for key in EXTRACTION_KEYS}

        for index, chunk in enumerate(chunks, start=1):
            prompt = scientific_extraction_prompt(
                chunk,
                chunk_number=index,
                total_chunks=len(chunks),
            )
            result = await self.provider.structured(
                prompt,
                system=SCIENTIFIC_EXTRACTION_SYSTEM,
            )
            for key in EXTRACTION_KEYS:
                values = result.get(key, [])
                if isinstance(values, list):
                    merged[key].extend(values)

        for key in EXTRACTION_KEYS:
            seen: set[str] = set()
            unique: list[Any] = []
            for value in merged[key]:
                marker = str(value).strip().lower()
                if marker and marker not in seen:
                    seen.add(marker)
                    unique.append(value)
            merged[key] = unique

        return merged
