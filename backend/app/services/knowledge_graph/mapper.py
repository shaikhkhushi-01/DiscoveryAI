from __future__ import annotations

import hashlib
import re
from typing import Any


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def key(value: str) -> str:
    return hashlib.sha256(normalize(value).lower().encode("utf-8")).hexdigest()[:32]


def entity_rows(extraction: dict[str, Any]) -> dict[str, list[str]]:
    entities = extraction.get("entities") or {}
    return {
        name: [normalize(x) for x in (entities.get(name) or []) if isinstance(x, str) and normalize(x)]
        for name in ("topics", "methods", "datasets", "problems", "applications", "metrics")
    }


def build_graph_payload(document_id: int, extraction: dict[str, Any]) -> dict[str, Any]:
    return {
        "document_id": document_id,
        "title": normalize(extraction.get("title") or f"Document {document_id}"),
        "year": extraction.get("year"),
        "doi": extraction.get("doi"),
        "authors": [normalize(x) for x in extraction.get("authors", []) if isinstance(x, str)],
        "institutions": [normalize(x) for x in extraction.get("institutions", []) if isinstance(x, str)],
        **entity_rows(extraction),
    }
