from __future__ import annotations

from typing import Any

from app.services.llm.factory import get_llm_provider

SYSTEM = """You are DiscoveryAI's scientific experiment planner.
Design testable, reproducible experiments from an evidence-backed research opportunity.
Never invent a result. Clearly separate proposed methodology from evidence.
Prefer controlled comparisons, explicit baselines, datasets, metrics, ablations, and statistical reporting."""

def build_experiment_plan(
    *,
    hypothesis: str,
    gap: dict[str, Any],
    evidence: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    evidence = evidence or []
    gap_type = gap.get("gap_type", "unspecified")
    datasets = gap.get("candidate_missing_datasets", [])
    return {
        "hypothesis": hypothesis,
        "gap_type": gap_type,
        "objective": f"Test whether the proposed intervention addresses the identified {gap_type} opportunity.",
        "datasets": datasets or ["Select a dataset justified by the research question and inclusion criteria."],
        "baselines": [
            "Current strongest published baseline identified from the indexed evidence.",
            "Simple/standard baseline appropriate to the task.",
            "Ablation without the proposed intervention.",
        ],
        "metrics": [
            "Primary task metric appropriate to the scientific problem.",
            "Robustness/generalization metric.",
            "Efficiency or resource metric when relevant.",
        ],
        "protocol": [
            "Pre-register inclusion/exclusion criteria and primary metric.",
            "Keep train/validation/test separation fixed.",
            "Compare proposed method against all baselines under matched settings.",
            "Run multiple seeds where stochastic training is used.",
            "Report confidence intervals or an appropriate statistical test.",
        ],
        "ablations": [
            "Remove the proposed component.",
            "Vary the key design choice.",
            "Evaluate across datasets/domains where feasible.",
        ],
        "evidence_scope": "indexed_corpus",
        "supporting_evidence_count": len(evidence),
        "result_status": "not_run",
    }

async def generate_hypothesis(question: str, gap: dict[str, Any], evidence: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    evidence = evidence or []
    context = "\n".join(
        f"- paper={x.get('paper_id')} score={x.get('rerank_score', 0)}"
        for x in evidence[:8]
    )
    prompt = f"""Research question:
{question}

Candidate research opportunity:
{gap}

Supporting evidence:
{context or "No supporting evidence supplied."}

Return JSON with:
statement, rationale, variables, expected_direction, falsification_condition.
The statement must be experimentally testable and must not claim an observed result."""
    provider = get_llm_provider()
    try:
        result = await provider.structured(prompt, system=SYSTEM, temperature=0.0)
    except (ValueError, Exception):
        result = {
            "statement": f"A controlled evaluation of the proposed intervention can improve evidence for the candidate {gap.get('gap_type', 'research')} opportunity.",
            "rationale": "Fallback hypothesis because structured generation was unavailable.",
            "variables": ["independent: proposed intervention", "dependent: primary task metric"],
            "expected_direction": "to be empirically determined",
            "falsification_condition": "No improvement over matched baselines under the preregistered protocol.",
        }
    plan = build_experiment_plan(hypothesis=result.get("statement", ""), gap=gap, evidence=evidence)
    plan["hypothesis_detail"] = result
    return plan
