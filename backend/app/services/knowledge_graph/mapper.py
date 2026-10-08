from __future__ import annotations

import hashlib
import re
from typing import Any


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def key(value: str) -> str:
    return hashlib.sha256(normalize(value).lower().encode("utf-8")).hexdigest()[:32]


def _strings(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return [normalize(x) for x in values if isinstance(x, str) and normalize(x)]


def entity_rows(extraction: dict[str, Any]) -> dict[str, list[str]]:
    nested = extraction.get("entities") if isinstance(extraction.get("entities"), dict) else {}

    def values(name: str) -> list[str]:
        return _strings(extraction.get(name) or nested.get(name) or [])

    return {name: values(name) for name in ("topics", "methods", "datasets", "problems", "applications", "metrics")}


def build_graph_payload(document_id: int, extraction: dict[str, Any]) -> dict[str, Any]:
    return {
        "document_id": document_id,
        "title": normalize(extraction.get("title") or f"Document {document_id}"),
        "year": extraction.get("year"),
        "doi": extraction.get("doi"),
        "authors": _strings(extraction.get("authors", [])),
        "institutions": _strings(extraction.get("institutions", [])),
        **entity_rows(extraction),
    }
