from __future__ import annotations

from typing import Any

from app.services.graph_rag.fusion import fuse
from app.services.graph_rag.retrieval import graph_expand, graph_search
from app.services.retrieval.hybrid import hybrid_search
from app.services.retrieval.reranker import rerank


def retrieve_graph_rag(query: str, *, limit: int = 8, filters: dict[str, Any] | None = None) -> dict[str, Any]:
    vector = hybrid_search(query, limit=max(limit * 3, 12), filters=filters)
    ranked = rerank(query, vector, limit=max(limit * 2, 12))
    graph_hits = graph_search(query, limit=max(limit * 3, 20))

    paper_ids = [int(x["paper_id"]) for x in ranked if x.get("paper_id") is not None]
    expanded = graph_expand(paper_ids, limit=max(limit * 5, 30))

    fused = fuse(ranked, graph_hits + expanded, limit=limit)
    return {
        "items": fused,
        "graph_hits": graph_hits,
        "graph_expansion": expanded,
    }
