from __future__ import annotations

from typing import Any

from app.services.evidence.scoring import compute_discovery_score
from app.services.graph_rag.pipeline import retrieve_graph_rag

def validate_evidence(candidate: dict[str, Any]) -> dict[str, Any]:
    result = retrieve_graph_rag(candidate["title"], limit=8)
    sources = result.get("items", [])
    validated = dict(candidate)
    validated["retrieval_evidence_count"] = len(sources)
    validated["supporting_papers"] = [x.get("paper_id") for x in sources if x.get("paper_id") is not None]
    validated["supporting_signal"] = sum(1 for x in sources if x.get("rerank_score", 0) >= 0.5)
    validated["contradictory_signal"] = any(
        x.get("rerank_score", 0) > 0.8 and x.get("graph_score", 0) > 0.4
        for x in sources
    )
    validated["evidence_status"] = (
        "contradicted_or_needs_review"
        if validated["contradictory_signal"]
        else "evidence_supported"
        if validated["supporting_signal"] > 0
        else "insufficient_evidence"
    )
    validated.update(compute_discovery_score(validated))
    validated["evidence"] = [
        {
            "paper_id": x.get("paper_id"),
            "document_id": x.get("document_id"),
            "semantic_score": x.get("semantic_score", 0),
            "rerank_score": x.get("rerank_score", 0),
            "graph_score": x.get("graph_score", 0),
        }
        for x in sources
    ]
    return validated
