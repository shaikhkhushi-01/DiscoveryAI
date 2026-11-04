from __future__ import annotations

import json
import re
from typing import Any

from app.services.llm.factory import get_llm_provider
from app.services.retrieval.hybrid import hybrid_search
from app.services.retrieval.reranker import rerank

SYSTEM = """You are DiscoveryAI, an evidence-grounded scientific research assistant.
Use only the supplied retrieved evidence. Do not claim that nobody has researched something.
If evidence is insufficient, say that no relevant evidence was identified within the indexed corpus and search scope.
Every factual claim about the literature must be traceable to a supplied evidence ID.
Never invent a source, section, quotation, number, or citation.
When sources disagree, do not silently choose one: explain the disagreement and cite every conflicting source.
Return a JSON object matching the requested schema, with no markdown fences."""


def _valid_evidence_ids(value: Any, allowed: set[str]) -> list[str]:
    if not isinstance(value, list):
        return []
    result = []
    for item in value:
        evidence_id = str(item).strip()
        if evidence_id in allowed and evidence_id not in result:
            result.append(evidence_id)
    return result


def _source_payload(item: dict[str, Any], evidence_id: str) -> dict[str, Any]:
    text = str(item.get("text") or "")
    return {
        **item,
        "evidence_id": evidence_id,
        "excerpt": text[:1200],
    }


async def answer_question(query: str, *, limit: int = 8, filters: dict[str, Any] | None = None) -> dict[str, Any]:
    retrieved = hybrid_search(query, limit=max(limit * 3, 12), filters=filters)
    ranked = rerank(query, retrieved, limit=limit)
    if not ranked:
        return {
            "answer": "No relevant evidence was identified within the indexed corpus and search scope.",
            "sources": [],
            "citations": [],
            "conflicts": [],
        }

    evidence = []
    sources = []
    allowed_ids: set[str] = set()
    for index, item in enumerate(ranked, start=1):
        evidence_id = f"EVIDENCE {index}"
        allowed_ids.add(evidence_id)
        evidence.append(
            f"[{evidence_id}] document_id={item.get('document_id')} "
            f"paper_id={item.get('paper_id')} chunk_id={item.get('chunk_id')} "
            f"section={item.get('section')}\n{item.get('text', '')}"
        )
        sources.append(_source_payload(item, evidence_id))

    prompt = f"""Research question:
{query}

Retrieved evidence (the only sources you may use):
{chr(10).join(evidence)}

Return exactly this JSON shape:
{{
  "answer": "A concise evidence-grounded answer. Put [EVIDENCE N] markers next to the claims they support.",
  "citations": ["EVIDENCE 1"],
  "conflicts": [
    {{
      "claim": "The point on which sources disagree",
      "values": [
        {{"value": "value or statement", "evidence_id": "EVIDENCE 1"}},
        {{"value": "different value or statement", "evidence_id": "EVIDENCE 2"}}
      ],
      "explanation": "Briefly describe the discrepancy without guessing which is correct."
    }}
  ],
  "limitations": ["Any important evidence gap or ambiguity; otherwise an empty list."]
}}

Rules:
- Every evidence_id must exactly match one of the supplied IDs.
- Include all retrieved evidence IDs that materially support the answer in citations.
- Detect materially conflicting values/statements across the supplied excerpts, including different numbers for the same metric and task.
- Do not label compatible values as conflicts (for example, scores for different model variants).
- Do not resolve a conflict using outside knowledge. If no conflict exists, return an empty conflicts array.
- If evidence is insufficient for part of the question, say so in answer and limitations.
"""
    provider = get_llm_provider()
    try:
        result = await provider.structured(prompt, system=SYSTEM, temperature=0.0)
        answer = str(result.get("answer") or "").strip()
        citations = _valid_evidence_ids(result.get("citations"), allowed_ids)
        conflicts = result.get("conflicts") if isinstance(result.get("conflicts"), list) else []
        limitations = result.get("limitations") if isinstance(result.get("limitations"), list) else []
        clean_conflicts = []
        for conflict in conflicts:
            if not isinstance(conflict, dict):
                continue
            values = conflict.get("values") if isinstance(conflict.get("values"), list) else []
            clean_values = [
                value for value in values
                if isinstance(value, dict) and value.get("evidence_id") in allowed_ids
            ]
            if len(clean_values) >= 2:
                clean_conflicts.append({
                    "claim": str(conflict.get("claim") or ""),
                    "values": clean_values,
                    "explanation": str(conflict.get("explanation") or ""),
                })
        if not answer:
            raise ValueError("Structured RAG response did not include an answer")
        # Ensure the returned citation list also covers any valid inline markers.
        inline_ids = re.findall(r"\[?(EVIDENCE \d+)\]?", answer)
        citations = list(dict.fromkeys(citations + [item for item in inline_ids if item in allowed_ids]))
        return {
            "answer": answer,
            "sources": sources,
            "citations": citations,
            "conflicts": clean_conflicts,
            "limitations": [str(item) for item in limitations],
        }
    except Exception:
        # Keep RAG usable if a provider cannot return valid structured output.
        fallback_prompt = f"""Research question:
{query}

Retrieved evidence:
{chr(10).join(evidence)}

Answer concisely using only this evidence. Cite factual claims with the exact [EVIDENCE N] markers.
If evidence conflicts, explicitly state the conflicting values and cite both. Do not guess."""
        answer = await provider.generate(fallback_prompt, system=SYSTEM, temperature=0.0)
        inline_ids = re.findall(r"\[?(EVIDENCE \d+)\]?", answer)
        citations = list(dict.fromkeys(item for item in inline_ids if item in allowed_ids))
        return {
            "answer": answer,
            "sources": sources,
            "citations": citations,
            "conflicts": [],
            "limitations": ["Structured conflict extraction was unavailable for this response."],
        }
