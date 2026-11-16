from __future__ import annotations

from typing import Any

from app.services.evidence.engine import score_opportunities
from app.services.experiments.planner import generate_hypothesis


def _distinct_source_count(evidence: list[dict[str, Any]]) -> int:
    """Count independent papers, falling back to document IDs when paper IDs are absent."""
    sources: set[tuple[str, str]] = set()
    for item in evidence:
        if not isinstance(item, dict):
            continue
        paper_id = item.get("paper_id")
        document_id = item.get("document_id")
        if paper_id is not None:
            sources.add(("paper", str(paper_id)))
        elif document_id is not None:
            sources.add(("document", str(document_id)))
    return len(sources)


async def generate_opportunity_plan(question: str, limit: int = 5) -> dict[str, Any]:
    scored = score_opportunities(limit=limit)
    plans = []
    skipped = []
    for gap in scored.get("items", []):
        if gap.get("evidence_status") == "contradicted_or_needs_review":
            skipped.append({
                "candidate": gap.get("title", "Untitled candidate"),
                "reason": "Evidence is contradicted or requires manual review.",
            })
            continue

        evidence = gap.get("evidence", [])
        if not isinstance(evidence, list):
            evidence = []
        distinct_sources = _distinct_source_count(evidence)
        if distinct_sources < 2:
            skipped.append({
                "candidate": gap.get("title", "Untitled candidate"),
                "reason": (
                    "At least two distinct source papers are required before generating "
                    "an evidence-linked hypothesis."
                ),
                "distinct_source_count": distinct_sources,
            })
            continue

        plan = await generate_hypothesis(question, gap, evidence)
        plan["supporting_distinct_paper_count"] = distinct_sources
        plans.append(plan)

    return {
        "question": question,
        "scope": "indexed_corpus",
        "plans": plans,
        "count": len(plans),
        "skipped_candidates": skipped,
        "skipped_count": len(skipped),
        "warning": (
            "Hypotheses and experiment plans are proposals, not experimental results. "
            "Candidates with fewer than two distinct supporting papers are not promoted "
            "to hypothesis generation."
        ),
    }
