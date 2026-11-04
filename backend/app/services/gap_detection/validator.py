from __future__ import annotations

from typing import Any

from app.services.graph_rag.pipeline import retrieve_graph_rag


def _paper_ids(sources: list[dict[str, Any]]) -> list[int]:
    return sorted({int(x["paper_id"]) for x in sources if x.get("paper_id") is not None})


def _evidence_records(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
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


def validate_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    # Search the candidate's explanation as well as its label to reduce title-only matches.
    query = " ".join(filter(None, [candidate.get("title"), candidate.get("description")]))
    result = retrieve_graph_rag(query, limit=8)
    sources = result.get("items", [])
    papers = _paper_ids(sources)
    supporting = sum(1 for x in sources if float(x.get("rerank_score", 0) or 0) >= 0.5)

    validated = dict(candidate)
    validated["retrieval_evidence_count"] = len(sources)
    validated["distinct_paper_count"] = len(papers)
    validated["supporting_papers"] = papers
    validated["supporting_signal"] = supporting
    # Relevance is not contradiction. Only an explicitly classified contradiction may set this.
    validated["contradictory_signal"] = any(
        bool(x.get("contradiction_detected")) for x in sources
    )
    validated["evidence"] = _evidence_records(sources)
    if validated["contradictory_signal"]:
        validated["status"] = "needs_review"
        validated["validation_note"] = (
            "A source was explicitly flagged as potentially contradictory; manual review is required."
        )
    elif len(papers) >= 3 and supporting >= 2:
        validated["status"] = "supported_candidate"
        validated["validation_note"] = (
            "Multiple distinct papers provide related context. This supports further investigation, "
            "not a claim that the topic is globally unexplored."
        )
    else:
        validated["status"] = "weak_candidate"
        validated["validation_note"] = (
            "The indexed corpus has limited independent evidence for this candidate. "
            "Sparse corpus coverage is not proof of a research gap."
        )
    # Confidence reflects evidence breadth, not certainty that a global gap exists.
    validated["confidence"] = round(min(0.75, 0.15 + 0.12 * min(len(papers), 5)), 3)
    validated["scope"] = "indexed_corpus"
    return validated


def validate_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [validate_candidate(item) for item in candidates]
