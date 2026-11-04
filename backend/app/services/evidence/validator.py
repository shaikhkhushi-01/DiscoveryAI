from __future__ import annotations

from typing import Any

from app.services.evidence.scoring import compute_discovery_score
from app.services.graph_rag.pipeline import retrieve_graph_rag


def validate_evidence(candidate: dict[str, Any]) -> dict[str, Any]:
    query = " ".join(filter(None, [candidate.get("title"), candidate.get("description")]))
    result = retrieve_graph_rag(query, limit=8)
    sources = result.get("items", [])
    papers = sorted({int(x["paper_id"]) for x in sources if x.get("paper_id") is not None})
    supporting = sum(1 for x in sources if float(x.get("rerank_score", 0) or 0) >= 0.5)

    validated = dict(candidate)
    validated["retrieval_evidence_count"] = len(sources)
    validated["distinct_paper_count"] = len(papers)
    validated["supporting_papers"] = papers
    validated["supporting_signal"] = supporting
    # A high relevance score indicates related material, not a contradiction.
    validated["contradictory_signal"] = any(
        bool(x.get("contradiction_detected")) for x in sources
    )
    validated["evidence_status"] = (
        "contradicted_or_needs_review"
        if validated["contradictory_signal"]
        else "evidence_supported"
        if supporting > 0
        else "insufficient_evidence"
    )
    validated.update(compute_discovery_score(validated))
    validated["evidence"] = [
        {
            "paper_id": x.get("paper_id"),
            "document_id": x.get("document_id"),
            "title": x.get("title"),
            "excerpt": (x.get("text") or "")[:1200],
            "semantic_score": x.get("semantic_score", 0),
            "rerank_score": x.get("rerank_score", 0),
            "graph_score": x.get("graph_score", 0),
        }
        for x in sources
    ]
    validated["scope"] = "indexed_corpus"
    return validated
