from __future__ import annotations

import ast
import logging
from typing import Any

from app.services.gap_detection.research_critic import _valid_ids, critique_research_gap
from app.services.llm.factory import get_llm_provider

logger = logging.getLogger(__name__)

SYSTEM = """Write a cautious research-opportunity report using only supplied indexed-corpus evidence.
Never claim global novelty or invent findings, citations, datasets, or results.
Label proposed directions and experiments as hypotheses, not established facts.
Represent possible_measurements as a JSON array of concise strings, never as a serialized Python list.
Cite only supplied EVIDENCE IDs. Return JSON only."""


def _measurement_list(value: Any) -> list[str]:
    if isinstance(value, list):
        values = value
    elif isinstance(value, str):
        text = value.strip()
        try:
            parsed = ast.literal_eval(text)
            values = parsed if isinstance(parsed, list) else [text]
        except (ValueError, SyntaxError):
            values = [text] if text else []
    else:
        values = []
    return list(dict.fromkeys(str(item).strip() for item in values if str(item).strip()))[:12]


async def build_research_opportunity_report(title: str, description: str = "", limit: int = 8) -> dict[str, Any]:
    critic = await critique_research_gap(title, description, limit)
    sources = critic.get("sources", [])
    allowed = {x["evidence_id"] for x in sources if x.get("evidence_id")}
    base = {
        "mode": "research_opportunity_report", "scope": "indexed_corpus",
        "candidate": {"title": title, "description": description},
        "critic": critic, "sources": sources, "score": None,
        "score_note": "No calibrated candidate-specific score is inferred from sparse retrieval.",
    }
    if not sources:
        return {**base, "executive_summary": "Insufficient indexed evidence for a defensible report.",
                "evidence_synthesis": [], "research_directions": [], "proposed_experiments": [],
                "confidence": "low", "limitations": critic.get("limitations", []) + ["No source excerpts were retrieved."]}
    prompt = f'''Candidate: {title}
Description: {description}
Critic verdict: {critic.get("verdict")}
Rationale: {critic.get("rationale")}
Evidence records: {sources}
Return JSON: executive_summary; evidence_synthesis [{{claim, interpretation, evidence_ids}}];
research_directions [{{direction, rationale, evidence_ids}}];
proposed_experiments [{{hypothesis, method, possible_measurements (JSON array of strings), evidence_ids}}];
confidence (low|moderate|high); limitations (array).
Directions and experiments are proposals, not findings. Cite only supplied evidence IDs.
Do not use high confidence when fewer than three distinct papers support the report.'''
    generation_error = None
    result: dict[str, Any] = {}
    provider = get_llm_provider()
    required_lists = ("evidence_synthesis", "research_directions", "proposed_experiments")
    for attempt in range(2):
        try:
            result = await provider.structured(
                prompt if attempt == 0 else (
                    prompt + "\\nYour previous response omitted required report sections. "
                    "Return at least one evidence-grounded item in each list where evidence permits; "
                    "if evidence truly does not support a section, explain that in limitations."
                ),
                system=SYSTEM,
                temperature=0.0 if attempt else 0.1,
            )
            if not isinstance(result, dict):
                raise ValueError("Report generator returned a non-object JSON response")
            if not str(result.get("executive_summary") or "").strip():
                raise ValueError("Report generator omitted executive_summary")
            if any(not isinstance(result.get(key), list) for key in required_lists):
                raise ValueError("Report generator omitted one or more required report arrays")
            if not any(result.get(key) for key in required_lists) and attempt == 0:
                raise ValueError("Report generator returned empty report sections")
            generation_error = None
            break
        except Exception as exc:
            generation_error = str(exc)
            logger.exception("Research opportunity report generation failed (attempt %s)", attempt + 1)
            result = {}
    if generation_error:
        logger.error("Research opportunity report generation exhausted retries: %s", generation_error)

    def clean(key: str, fields: tuple[str, ...]) -> list[dict[str, Any]]:
        values = result.get(key)
        if not isinstance(values, list):
            return []
        output = []
        for value in values[:8]:
            if not isinstance(value, dict):
                continue
            record: dict[str, Any] = {}
            for field in fields:
                if field == "possible_measurements":
                    record[field] = _measurement_list(value.get(field))
                else:
                    record[field] = str(value.get(field) or "").strip()
            record["evidence_ids"] = _valid_ids(value.get("evidence_ids"), allowed)
            if any(record[field] for field in fields):
                output.append(record)
        return output

    confidence = str(result.get("confidence") or "low").lower()
    if confidence not in {"low", "moderate", "high"}:
        confidence = "low"
    if critic.get("distinct_paper_count", 0) < 3 and confidence == "high":
        confidence = "moderate"
    limitations = result.get("limitations") if isinstance(result.get("limitations"), list) else []
    return {
        **base,
        "executive_summary": str(result.get("executive_summary") or critic.get("rationale") or "Evidence is inconclusive."),
        "evidence_synthesis": clean("evidence_synthesis", ("claim", "interpretation")),
        "research_directions": clean("research_directions", ("direction", "rationale")),
        "proposed_experiments": clean("proposed_experiments", ("hypothesis", "method", "possible_measurements")),
        "confidence": confidence,
        "report_generation_status": "completed" if not generation_error else "incomplete",
        "report_generation_note": (
            "Report sections were generated from retrieved evidence."
            if not generation_error else
            "The report model did not return a valid complete structure after one retry; no unsupported sections were fabricated."
        ),
        "limitations": list(dict.fromkeys(
            [str(x) for x in limitations] + critic.get("limitations", []) +
            ([f"Report generation incomplete: {generation_error[:240]}"] if generation_error else [])
        )),
        "proposal_disclaimer": "AI-generated directions and experiments are proposals requiring expert review, not findings established by cited papers.",
    }
