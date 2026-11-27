from __future__ import annotations

import logging
from typing import Any

from app.services.graph_rag.fusion import fuse
from app.services.graph_rag.retrieval import graph_expand, graph_search
from app.services.retrieval.hybrid import hybrid_search
from app.services.retrieval.reranker import rerank

logger = logging.getLogger(__name__)


def retrieve_graph_rag(query: str, *, limit: int = 8, filters: dict[str, Any] | None = None) -> dict[str, Any]:
    # Vector/keyword retrieval is the primary evidence path. Neo4j enriches
    # results but must not take the entire Q&A endpoint down when unavailable.
    vector = hybrid_search(query, limit=max(limit * 3, 12), filters=filters)
    ranked = rerank(query, vector, limit=max(limit * 2, 12))

    graph_hits: list[dict[str, Any]] = []
    try:
        graph_hits = graph_search(query, limit=max(limit * 3, 20))
    except Exception:
        logger.exception("Neo4j graph search unavailable; continuing with document retrieval")

    paper_ids = [int(x["paper_id"]) for x in ranked if x.get("paper_id") is not None]
    expanded: list[dict[str, Any]] = []
    if paper_ids:
        try:
            expanded = graph_expand(paper_ids, limit=max(limit * 5, 30))
        except Exception:
            logger.exception("Neo4j graph expansion unavailable; continuing without graph expansion")

    fused = fuse(ranked, graph_hits + expanded, limit=limit)
    return {
        "items": fused,
        "graph_hits": graph_hits,
        "graph_expansion": expanded,
        "retrieval_mode": "hybrid_graph" if graph_hits or expanded else "hybrid_only",
    }
