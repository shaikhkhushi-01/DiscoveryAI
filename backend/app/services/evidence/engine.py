from __future__ import annotations

from typing import Any

from app.services.evidence.validator import validate_evidence
from app.services.gap_detection.candidates import generate_graph_candidates

def score_opportunities(limit: int = 20) -> dict[str, Any]:
    candidates = generate_graph_candidates(max(limit * 2, 20))
    results = [validate_evidence(candidate) for candidate in candidates]
    results.sort(key=lambda x: x.get("discovery_score", 0), reverse=True)
    return {
        "scope": "indexed_corpus",
        "score_version": "v1",
        "items": results[:limit],
        "count": len(results[:limit]),
        "warning": "Discovery Score is an evidence-based opportunity signal, not proof of global novelty."
    }
