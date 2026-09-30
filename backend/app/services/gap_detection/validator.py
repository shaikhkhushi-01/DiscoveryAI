from __future__ import annotations

from typing import Any

from app.services.graph_rag.pipeline import retrieve_graph_rag


def validate_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    result = retrieve_graph_rag(candidate["title"], limit=6)
    sources = result.get("items", [])
    candidate = dict(candidate)
    candidate["retrieval_evidence_count"] = len(sources)
    candidate["supporting_papers"] = [x.get("paper_id") for x in sources if x.get("paper_id") is not None]
    candidate["contradictory_signal"] = any(
        x.get("rerank_score", 0) > 0.8 and x.get("graph_score", 0) > 0.4
        for x in sources
    )
    candidate["supporting_signal"] = sum(
        1 for x in sources if x.get("rerank_score", 0) >= 0.5
    )
    if candidate["contradictory_signal"]:
        candidate["status"] = "needs_review"
        candidate["validation_note"] = "Strong related evidence was retrieved; the candidate should not be treated as an unverified absence."
    elif len(sources) >= 3:
        candidate["status"] = "supported_candidate"
        candidate["validation_note"] = "Related evidence exists within the indexed corpus; this is an opportunity signal, not proof of global absence."
    else:
        candidate["status"] = "weak_candidate"
        candidate["validation_note"] = "Limited related evidence was identified within the indexed corpus."
    candidate["confidence"] = round(min(0.95, 0.25 + 0.08 * len(sources)), 3)
    return candidate


def validate_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [validate_candidate(item) for item in candidates]
