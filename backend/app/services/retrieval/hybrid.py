from __future__ import annotations

import re
from typing import Any

from app.db.session import SessionLocal
from app.models.document import Document
from app.models.paper import Paper
from app.services.embeddings.factory import get_embedding_provider
from app.services.vector_store import search_vectors

def _tokens(text: str) -> set[str]:
    return {x for x in re.findall(r"[a-zA-Z0-9][a-zA-Z0-9_-]+", text.lower()) if len(x) > 2}

def keyword_search(query: str, limit: int = 20, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    filters = filters or {}
    tokens = _tokens(query)
    if not tokens:
        return []
    db = SessionLocal()
    try:
        rows = db.query(Paper).outerjoin(Document).limit(500).all()
        scored = []
        for paper in rows:
            if filters.get("year") is not None and (not paper.publication_date or paper.publication_date.year != filters["year"]):
                continue
            hay = " ".join([paper.title or "", paper.abstract or ""]).lower()
            overlap = len(tokens & _tokens(hay))
            if overlap:
                scored.append({"paper_id": paper.id, "title": paper.title, "keyword_score": overlap / len(tokens)})
        return sorted(scored, key=lambda x: x["keyword_score"], reverse=True)[:limit]
    finally:
        db.close()

def hybrid_search(query: str, *, limit: int = 10, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    filters = filters or {}
    vector = get_embedding_provider().embed([query])[0]
    semantic = search_vectors(vector, limit=min(50, limit * 5), filters=filters)
    keyword = keyword_search(query, limit=limit * 5, filters=filters)
    by_key: dict[tuple[Any, Any], dict[str, Any]] = {}
    for item in semantic:
        key = (item.get("document_id"), item.get("chunk_id"))
        by_key[key] = {**item, "semantic_score": float(item.get("score", 0.0))}
    for item in keyword:
        for key, existing in list(by_key.items()):
            if existing.get("paper_id") == item["paper_id"]:
                existing["keyword_score"] = item["keyword_score"]
                existing["paper_id"] = item["paper_id"]
    for item in by_key.values():
        item["hybrid_score"] = 0.75 * item.get("semantic_score", 0.0) + 0.25 * item.get("keyword_score", 0.0)
    return sorted(by_key.values(), key=lambda x: x["hybrid_score"], reverse=True)[:limit]
