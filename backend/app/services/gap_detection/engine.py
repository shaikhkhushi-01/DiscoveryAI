from __future__ import annotations

from typing import Any

from app.services.gap_detection.candidates import generate_graph_candidates
from app.services.gap_detection.validator import validate_candidates


def detect_gaps(limit: int = 20) -> dict[str, Any]:
    candidates = generate_graph_candidates(limit=max(limit * 2, 20))
    validated = validate_candidates(candidates)
    validated.sort(
        key=lambda x: (
            {"supported_candidate": 3, "weak_candidate": 2, "needs_review": 1}.get(x.get("status"), 0),
            x.get("confidence", 0),
            x.get("evidence_count", 0),
        ),
        reverse=True,
    )
    return {
        "source": "knowledge_graph_plus_graphrag",
        "scope": "indexed_corpus",
        "items": validated[:limit],
        "count": len(validated[:limit]),
    }
