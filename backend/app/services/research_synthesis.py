from __future__ import annotations

from typing import Any

from app.services.llm.factory import get_llm_provider
from app.services.retrieval.hybrid import hybrid_search
from app.services.retrieval.reranker import rerank


SYSTEM = """You are DiscoveryAI, a scientific literature analyst.
Use only the supplied indexed-paper evidence. Never invent papers, authors, methods,
results, limitations, or citations. Distinguish reported findings from interpretation.
If the evidence does not support a comparison point, say so. Do not claim a gap is
novel or that no research exists; describe only what is absent from this indexed corpus.
Return JSON only."""


def _clean_ids(value: Any, allowed: set[str]) -> list[str]:
    if not isinstance(value, list):
        return []
    return list(dict.fromkeys(str(x).strip() for x in value if str(x).strip() in allowed))


async def synthesize_research(
    query: str,
    *,
    mode: str = "literature_review",
    limit: int = 12,
    paper_ids: list[int] | None = None,
) -> dict[str, Any]:
    retrieved = hybrid_search(query, limit=max(limit * 5, 30))
    if paper_ids:
        wanted = set(paper_ids)
        retrieved = [item for item in retrieved if item.get("paper_id") in wanted]
    ranked = rerank(query, retrieved, limit=min(max(limit, 2), 30))

    # Prefer a spread of papers rather than allowing one paper's chunks to dominate.
    selected: list[dict[str, Any]] = []
    per_paper: dict[Any, int] = {}
    for item in ranked:
        paper_id = item.get("paper_id")
        if per_paper.get(paper_id, 0) >= 3:
            continue
        selected.append(item)
        per_paper[paper_id] = per_paper.get(paper_id, 0) + 1

    paper_count = len({item.get("paper_id") for item in selected if item.get("paper_id") is not None})
    if mode == "comparison" and paper_count < 2:
        return {
            "mode": mode,
            "query": query,
            "scope": "indexed_corpus",
            "answer": "A multi-paper comparison requires relevant evidence from at least two distinct papers.",
            "paper_count": paper_count,
            "sources": [],
            "citations": [],
            "limitations": ["Fewer than two distinct papers matched this query in the indexed corpus."],
        }
    if not selected:
        return {
            "mode": mode,
            "query": query,
            "scope": "indexed_corpus",
            "answer": "No relevant evidence was identified within the indexed corpus and search scope.",
            "sources": [],
            "citations": [],
            "limitations": ["No retrieved paper chunks were available for synthesis."],
        }

    sources = []
    evidence_blocks = []
    allowed: set[str] = set()
    for index, item in enumerate(selected, start=1):
        evidence_id = f"EVIDENCE {index}"
        allowed.add(evidence_id)
        text = str(item.get("text") or "")
        sources.append({
            "evidence_id": evidence_id,
            "paper_id": item.get("paper_id"),
            "document_id": item.get("document_id"),
            "chunk_id": item.get("chunk_id"),
            "title": item.get("title"),
            "section": item.get("section"),
            "excerpt": text[:1400],
        })
        evidence_blocks.append(
            f"[{evidence_id}] paper_id={item.get('paper_id')} "
            f"document_id={item.get('document_id')} title={item.get('title')} "
            f"section={item.get('section')}\n{text}"
        )

    if mode == "comparison":
        task = """Compare the papers across: research objective, methods, datasets/evaluation,
main findings, limitations, and points of agreement/disagreement. Use a comparison
array of objects with dimension, findings, and evidence_ids. Do not force a comparison
when a paper does not report a dimension."""
    else:
        task = """Write a structured evidence-backed literature review with: overview,
major themes, methods and datasets, reported findings, disagreements or inconsistencies,
limitations in the retrieved corpus, and open questions. Any proposed open question
must be labelled as a possible direction, not a proven research gap."""

    prompt = f"""Research question: {query}
Mode: {mode}
Task: {task}

Retrieved evidence (exclusive source of factual claims):
{chr(10).join(evidence_blocks)}

Return this JSON shape:
{{
  "answer": "Integrated synthesis with [EVIDENCE N] markers beside factual claims.",
  "sections": [{{"heading": "Theme or dimension", "content": "Evidence-based discussion", "evidence_ids": ["EVIDENCE 1"]}}],
  "comparisons": [{{"dimension": "Methods", "findings": "How papers differ or align", "evidence_ids": ["EVIDENCE 1", "EVIDENCE 2"]}}],
  "limitations": ["What the retrieved evidence cannot establish"],
  "citations": ["EVIDENCE 1"]
}}
Rules: use only supplied excerpts; cite every substantive claim; use only exact evidence IDs;
do not infer missing paper metadata; do not fabricate comparisons; if a requested detail
is not reported, state that it was not found in the retrieved excerpts.
"""
    result = await get_llm_provider().structured(prompt, system=SYSTEM, temperature=0.0)
    answer = str(result.get("answer") or "").strip()
    if not answer:
        raise ValueError("Research synthesis provider returned an empty answer")

    sections = []
    for section in result.get("sections", []) if isinstance(result.get("sections"), list) else []:
        if isinstance(section, dict):
            ids = _clean_ids(section.get("evidence_ids"), allowed)
            sections.append({
                "heading": str(section.get("heading") or ""),
                "content": str(section.get("content") or ""),
                "evidence_ids": ids,
            })
    comparisons = []
    for comparison in result.get("comparisons", []) if isinstance(result.get("comparisons"), list) else []:
        if isinstance(comparison, dict):
            ids = _clean_ids(comparison.get("evidence_ids"), allowed)
            comparisons.append({
                "dimension": str(comparison.get("dimension") or ""),
                "findings": str(comparison.get("findings") or ""),
                "evidence_ids": ids,
            })
    return {
        "mode": mode,
        "query": query,
        "scope": "indexed_corpus",
        "paper_count": paper_count,
        "answer": answer,
        "sections": sections,
        "comparisons": comparisons,
        "citations": _clean_ids(result.get("citations"), allowed),
        "limitations": [str(x) for x in result.get("limitations", [])] if isinstance(result.get("limitations"), list) else [],
        "sources": sources,
    }
