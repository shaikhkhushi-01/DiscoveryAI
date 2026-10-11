from __future__ import annotations

import os
from typing import Any

from app.core.config import settings


def rerank(query: str, items: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    """
    Keep RAG available on memory-constrained hosts.

    The CrossEncoder can consume substantial RAM and may cause a small Render
    instance to be killed. Enable it explicitly with ENABLE_CROSS_ENCODER_RERANKER=true.
    The default path uses the existing hybrid/vector score and does not download
    or load an additional ML model at request time.
    """
    if not items:
        return []

    if os.getenv("ENABLE_CROSS_ENCODER_RERANKER", "false").lower() in {"1", "true", "yes"}:
        try:
            from sentence_transformers import CrossEncoder

            model = CrossEncoder(settings.reranker_model)
            scores = model.predict([(query, item.get("text", "")) for item in items])
            ranked = [
                {**item, "rerank_score": float(score)}
                for item, score in zip(items, scores)
            ]
            return sorted(ranked, key=lambda x: x["rerank_score"], reverse=True)[:limit]
        except Exception:
            # Fall back to hybrid/vector ranking if the optional reranker is unavailable.
            pass

    ranked = [
        {
            **item,
            "rerank_score": float(
                item.get("hybrid_score", item.get("semantic_score", item.get("score", 0.0)))
            ),
        }
        for item in items
    ]
    return sorted(ranked, key=lambda x: x["rerank_score"], reverse=True)[:limit]
