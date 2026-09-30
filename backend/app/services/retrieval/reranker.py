from __future__ import annotations

from functools import lru_cache
from typing import Any

from app.core.config import settings

@lru_cache
def _model():
    from sentence_transformers import CrossEncoder
    return CrossEncoder(settings.reranker_model)

def rerank(query: str, items: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    if not items:
        return []
    try:
        scores = _model().predict([(query, item.get("text", "")) for item in items])
        ranked = [{**item, "rerank_score": float(score)} for item, score in zip(items, scores)]
    except Exception:
        ranked = [{**item, "rerank_score": item.get("hybrid_score", item.get("score", 0.0))} for item in items]
    return sorted(ranked, key=lambda x: x["rerank_score"], reverse=True)[:limit]
