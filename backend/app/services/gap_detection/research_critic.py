from __future__ import annotations

import logging
import re
from typing import Any
from sqlalchemy import func

from app.db.session import SessionLocal
from app.models.paper import Paper
from app.services.graph_rag.pipeline import retrieve_graph_rag
from app.services.llm.factory import get_llm_provider

logger = logging.getLogger(__name__)

SYSTEM = """Review research-gap claims skeptically using only supplied indexed-corpus evidence.
Accept means the candidate is a plausible, specifically supported research opportunity in this corpus;
it does NOT mean the gap is proven globally novel. Accept only when evidence directly engages with
the candidate's specific task, setting, and claimed limitation or opportunity. General descriptions
of an architecture, broad claims such as modelling dependencies regardless of distance, and evidence
about an adjacent task are not enough to accept a narrowly framed efficiency or long-context gap.
Reject only when direct evidence demonstrates that this specific gap is already addressed.
Use review when evidence is related but does not establish the specific claim either way.
Never invent citations. Prefer scientific body content over references, bibliographies, acknowledgements,
and author-contribution statements. Output JSON only."""


def _valid_ids(value: Any, allowed: set[str]) -> list[str]:
    if not isinstance(value, list):
        return []
    return list(dict.fromkeys(str(x).strip() for x in value if str(x).strip() in allowed))


def _reference_penalty(hit: dict[str, Any]) -> float:
    section = str(hit.get("section") or "").lower().strip()
    if section in {"references", "bibliography", "works cited", "acknowledgements", "author contributions"}:
        return 1.0
    text = str(hit.get("text") or "")
    lines = text.splitlines()
    citation_lines = sum(
        1 for line in lines
        if re.search(r"\b(19|20)\d{2}\b", line) and ("," in line or ";" in line)
    )
    if text and citation_lines >= 3 and citation_lines / max(1, len(lines)) > 0.5:
        return 0.35
    return 0.0


def _indexed_corpus_count() -> int:
    db = SessionLocal()
    try:
        return int(db.query(func.count(Paper.id)).scalar() or 0)
    except Exception:
        logger.exception("Could not count indexed paper records")
        return 0
    finally:
        db.close()


def _canonical_paper_titles(paper_ids: set[int]) -> dict[int, str]:
    if not paper_ids:
        return {}
    db = SessionLocal()
    try:
        rows = db.query(Paper.id, Paper.title).filter(Paper.id.in_(paper_ids)).all()
        return {int(pid): str(title) for pid, title in rows if title}
    except Exception:
        logger.exception("Could not hydrate canonical paper titles for research critic")
        return {}
    finally:
        db.close()


async def critique_research_gap(title: str, description: str = "", limit: int = 8) -> dict[str, Any]:
    query = " ".join(x for x in (title.strip(), description.strip()) if x)
    # Retrieve a wider candidate pool, then diversify by paper so one paper's
    # many chunks cannot crowd out independent literature.
    retrieval_limit = max(24, min(limit * 4, 48))
    hits = retrieve_graph_rag(query, limit=retrieval_limit).get("items", [])
    ranked = sorted(
        hits,
        key=lambda hit: float(hit.get("graph_rag_score", hit.get("rerank_score", 0)) or 0) - _reference_penalty(hit),
        reverse=True,
    )
    body_hits = [hit for hit in ranked if _reference_penalty(hit) < 0.5]
    pool = body_hits or ranked
    selected = []
    seen_papers: set[int] = set()
    max_papers = max(1, min(limit, 12))
    for hit in pool:
        pid = hit.get("paper_id")
        if pid is None:
            continue
        try:
            pid = int(pid)
        except (TypeError, ValueError):
            continue
        if pid in seen_papers:
            continue
        seen_papers.add(pid)
        selected.append(hit)
        if len(selected) >= max_papers:
            break
    paper_ids = {int(hit["paper_id"]) for hit in selected if hit.get("paper_id") is not None}
    canonical_titles = _canonical_paper_titles(paper_ids)
    sources, blocks = [], []
    for i, hit in enumerate(selected, 1):
        eid = f"EVIDENCE {i}"
        excerpt = str(hit.get("text") or "")[:1200]
        paper_id = hit.get("paper_id")
        paper_title = canonical_titles.get(int(paper_id)) if paper_id is not None else None
        paper_title = paper_title or hit.get("title") or hit.get("paper_title")
        sources.append({
            "evidence_id": eid, "paper_id": paper_id,
            "document_id": hit.get("document_id"), "chunk_id": hit.get("chunk_id"),
            "title": paper_title, "section": hit.get("section"), "excerpt": excerpt,
            "rerank_score": hit.get("rerank_score", 0),
            "semantic_score": hit.get("semantic_score", 0),
            "graph_score": hit.get("graph_score", 0),
        })
        blocks.append(f"[{eid}] {paper_title} (paper_id={paper_id}, section={hit.get('section')})\n{excerpt}")

    indexed_count = _indexed_corpus_count()
    base = {
        "mode": "research_critic", "candidate": {"title": title, "description": description},
        "scope": "indexed_corpus", "distinct_paper_count": len(paper_ids),
        "coverage": {
            "registered_paper_count": indexed_count,
            "retrieved_distinct_paper_count": len(paper_ids),
            "retrieval_candidate_pool": retrieval_limit,
            "coverage_is_global": False,
        },
        "sources": sources,
    }
    limits = [
        "Assessment is limited to papers indexed in DiscoveryAI.",
        "Sparse corpus coverage cannot establish global research novelty.",
        f"Retrieved {len(paper_ids)} distinct papers; {indexed_count} paper records are registered (not all are necessarily indexed).",
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
For accept, the evidence must directly engage with this candidate's specific task, setting, and claimed
limitation/opportunity. A general architecture capability or adjacent task is insufficient; choose review.
For reject, direct evidence must demonstrate this exact gap is already addressed.
If the evidence is merely related, choose review. Cite only exact EVIDENCE IDs supplied above.'''
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
