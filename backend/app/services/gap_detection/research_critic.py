from __future__ import annotations

import logging
from typing import Any

from app.services.graph_rag.pipeline import retrieve_graph_rag
from app.services.llm.factory import get_llm_provider

logger = logging.getLogger(__name__)

SYSTEM = """Review research-gap claims skeptically. Use only supplied indexed-corpus evidence.
Never invent citations. Related evidence is not proof that a gap is solved.
Reject only on direct evidence that this specific gap is already addressed.
Accept only as plausible within this corpus, never as globally novel.
Otherwise return review. Output JSON only."""


def _valid_ids(value: Any, allowed: set[str]) -> list[str]:
    if not isinstance(value, list):
        return []
    return list(dict.fromkeys(str(x).strip() for x in value if str(x).strip() in allowed))


async def critique_research_gap(title: str, description: str = "", limit: int = 8) -> dict[str, Any]:
    query = " ".join(x for x in (title.strip(), description.strip()) if x)
    hits = retrieve_graph_rag(query, limit=max(1, min(limit, 12))).get("items", [])
    sources, blocks = [], []
    for i, hit in enumerate(hits, 1):
        eid = f"EVIDENCE {i}"
        excerpt = str(hit.get("text") or "")[:1200]
        sources.append({
            "evidence_id": eid, "paper_id": hit.get("paper_id"),
            "document_id": hit.get("document_id"), "title": hit.get("title"),
            "excerpt": excerpt, "rerank_score": hit.get("rerank_score", 0),
            "semantic_score": hit.get("semantic_score", 0),
            "graph_score": hit.get("graph_score", 0),
        })
        blocks.append(f"[{eid}] {hit.get('title')} (paper_id={hit.get('paper_id')})\n{excerpt}")

    paper_ids = {x.get("paper_id") for x in hits if x.get("paper_id") is not None}
    base = {
        "mode": "research_critic",
        "candidate": {"title": title, "description": description},
        "scope": "indexed_corpus",
        "distinct_paper_count": len(paper_ids),
        "sources": sources,
    }
    limits = [
        "Assessment is limited to papers indexed in DiscoveryAI.",
        "Sparse corpus coverage cannot establish global research novelty.",
    ]
    if len(paper_ids) < 2:
        return {
            **base, "verdict": "review",
            "rationale": "Fewer than two distinct papers were retrieved; evidence is insufficient.",
            "evidence_ids": [], "checks": ["Independent paper coverage is insufficient."],
            "limitations": limits,
        }

    prompt = f'''Candidate: {title}
Description: {description}
Evidence:
{chr(10).join(blocks)}
Return JSON with keys verdict (accept|reject|review), rationale, evidence_ids, checks, limitations.
Reject only if direct evidence shows this specific gap is already addressed.
Accept only as plausible within this corpus. Review ambiguous cases.
Cite only the exact EVIDENCE IDs supplied above.'''
    try:
        result = await get_llm_provider().structured(prompt, system=SYSTEM, temperature=0.0)
    except Exception:
        logger.exception("Research critic LLM assessment failed")
        return {
            **base, "verdict": "review",
            "rationale": "Critic unavailable or returned invalid output; manual review is required.",
            "evidence_ids": [], "checks": ["No reliable automated verdict was produced."],
            "limitations": limits,
        }

    if not isinstance(result, dict):
        logger.error("Research critic returned non-object structured result: %s", type(result).__name__)
        result = {}
    verdict = str(result.get("verdict") or "review").lower().strip()
    if verdict not in {"accept", "reject", "review"}:
        verdict = "review"
    cited = _valid_ids(result.get("evidence_ids"), {x["evidence_id"] for x in sources})
    if verdict in {"accept", "reject"} and not cited:
        verdict = "review"
    return {
        **base, "verdict": verdict,
        "rationale": str(result.get("rationale") or "Evidence is inconclusive."),
        "evidence_ids": cited,
        "checks": result.get("checks", []) if isinstance(result.get("checks"), list) else [],
        "limitations": (result.get("limitations", []) if isinstance(result.get("limitations"), list) else []) + limits,
    }
