from typing import Any
import re
from pathlib import Path
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



_PLACEHOLDER_TITLES = {
    "", "untitled", "unknown", "document", "paper", "research paper",
    "real scientific research pdf", "scientific research pdf",
}

# PDF text extractors sometimes put publisher permissions, licensing notices,
# and running headers before the actual title on page one. These are not titles.
_TITLE_BOILERPLATE = re.compile(
    r"(google hereby grants permission|provided proper attribution|"
    r"permission to reproduce|solely for use in|all rights reserved|"
    r"copyright\s*(?:©|\(c\))?|creative commons|licensed under|"
    r"arxiv vanity|downloaded from|personal use is permitted|"
    r"ieee.*copyright|acm.*copyright)",
    re.IGNORECASE,
)


def is_usable_paper_title(value: str | None, filename: str | None = None) -> bool:
    title = str(value or "").strip()
    normalized = re.sub(r"\s+", " ", title).strip().lower()
    if normalized in _PLACEHOLDER_TITLES or len(title) < 8 or len(title) > 300:
        return False
    if _TITLE_BOILERPLATE.search(normalized):
        return False
    if re.fullmatch(r"[0-9a-f]{40,64}", normalized):
        return False
    if filename and normalized in {
        Path(filename).stem.strip().lower(),
        Path(filename).name.strip().lower(),
    }:
        return False
    if normalized.endswith(".pdf") or re.search(r"\.(pdf|docx?)$", normalized):
        return False
    return True


def infer_paper_title(text: str, metadata_title: str | None = None, filename: str | None = None) -> str:
    """Prefer meaningful PDF metadata; otherwise infer a title from first-page text."""
    if is_usable_paper_title(metadata_title, filename):
        return re.sub(r"\s+", " ", str(metadata_title)).strip()

    first_page = (text or "").split("\f", 1)[0]
    lines = [re.sub(r"\s+", " ", line).strip() for line in first_page.splitlines()]
    lines = [line for line in lines if line]
    ignored = re.compile(
        r"(abstract|arxiv\.org|\bdoi\s*:|\bsubmitted\b|\bpublished\b|"
        r"university|department|institute|\bproceedings\b|\bvol\.?\s*\d|"
        r"\b(19|20)\d{2}\b|@|https?://)",
        re.IGNORECASE,
    )
    candidates: list[str] = []
    for line in lines[:40]:
        line = re.sub(r"^\s*(?:\d+\s*)$", "", line).strip()
        # A standalone sentence from extracted body text is not a plausible
        # title candidate; continue to the upload filename fallback instead.
        if line.endswith((".", "?", "!")) and len(line.split()) >= 4:
            continue
        if (
            not line
            or len(line) < 8
            or len(line) > 180
            or ignored.search(line)
            or _TITLE_BOILERPLATE.search(line)
        ):
            continue
        if re.fullmatch(r"[-_=*\W]+", line):
            continue
        # Author lists and affiliations generally contain commas or email-like tokens.
        if candidates and (
            line.count(",") >= 1
            or re.search(r"\b(author|authors)\b", line, re.I)
        ):
            break
        candidates.append(line)
        if len(candidates) >= 3 or line.endswith((".", "?", "!")):
            break

    inferred = re.sub(r"\s+", " ", " ".join(candidates)).strip(" -:")
    if is_usable_paper_title(inferred, filename):
        return inferred[:500]

    stem = Path(filename or "").stem.strip()
    # The filename is an explicit fallback source, so do not reject it merely
    # because it matches the filename argument passed to the general validator.
    # Preserve the original stem (including hyphens) for traceability.
    if stem and not re.fullmatch(r"[0-9a-f]{40,64}", stem.lower()):
        if is_usable_paper_title(stem):
            return stem[:500]
    return "Untitled research paper"
