from __future__ import annotations

from typing import Any

from app.services.evidence.engine import score_opportunities
from app.services.experiments.planner import generate_hypothesis

async def generate_opportunity_plan(question: str, limit: int = 5) -> dict[str, Any]:
    scored = score_opportunities(limit=limit)
    plans = []
    for gap in scored.get("items", []):
        if gap.get("evidence_status") == "contradicted_or_needs_review":
            continue
        plans.append(await generate_hypothesis(
            question,
            gap,
            gap.get("evidence", []),
        ))
    return {
        "question": question,
        "scope": "indexed_corpus",
        "plans": plans,
        "count": len(plans),
        "warning": "Hypotheses and experiment plans are proposals; they contain no experimental results."
    }
