from __future__ import annotations

from typing import Any
import hashlib

from app.services.gap_detection.research_critic import critique_research_gap
from app.services.graph_rag.pipeline import retrieve_graph_rag
from app.services.llm.factory import get_llm_provider


SYSTEM = """You are DiscoveryAI, a cautious NLP and scientific-literature research analyst.
Use only the supplied retrieved paper excerpts. Never invent papers, authors, results,
datasets, methods, citations, or numerical findings. Separate reported evidence from
interpretation. A possible gap is only a candidate within this retrieved indexed corpus;
absence from retrieved evidence is not proof that no research exists. Hypotheses and
experiments are proposals, never findings. Cite every substantive item with exact supplied
EVIDENCE IDs. Return one JSON object only."""


def _prepare_sources(hits: list[dict[str, Any]], limit: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Create a bounded, paper-diverse evidence set with stable request-local IDs."""
    sources: list[dict[str, Any]] = []
    selected_hits: list[dict[str, Any]] = []
    per_paper: dict[str, int] = {}
    seen_chunks: set[tuple[str, str]] = set()

    for hit in hits:
        if not isinstance(hit, dict):
            continue
        text = str(hit.get("text") or "").strip()
        paper_id = hit.get("paper_id")
        document_id = hit.get("document_id")
        chunk_id = hit.get("chunk_id")
        if not text or (paper_id is None and document_id is None):
            continue
        source_key = ("paper", str(paper_id)) if paper_id is not None else ("document", str(document_id))
        chunk_identity = (
            str(chunk_id) if chunk_id is not None
            else hashlib.sha256(text.encode("utf-8")).hexdigest()
        )
        chunk_key = (str(document_id or paper_id or ""), chunk_identity)
        if chunk_key in seen_chunks:
            continue
        if per_paper.get(source_key[1], 0) >= 2:
            continue

        evidence_id = f"EVIDENCE {len(sources) + 1}"
        sources.append({
            "evidence_id": evidence_id,
            "paper_id": paper_id,
            "document_id": document_id,
            "chunk_id": chunk_id,
            "title": hit.get("title") or hit.get("paper_title"),
            "section": hit.get("section"),
            "excerpt": text[:1600],
        })
        selected_hits.append(hit)
        seen_chunks.add(chunk_key)
        per_paper[source_key[1]] = per_paper.get(source_key[1], 0) + 1
        if len(sources) >= limit:
            break
    return sources, selected_hits


def _valid_evidence_ids(value: Any, allowed: set[str]) -> list[str]:
    if not isinstance(value, list):
        return []
    return list(dict.fromkeys(
        str(item).strip() for item in value
        if isinstance(item, (str, int)) and str(item).strip() in allowed
    ))


def _distinct_papers(ids: list[str], source_by_id: dict[str, dict[str, Any]]) -> set[str]:
    result = set()
    for evidence_id in ids:
        source = source_by_id[evidence_id]
        key = source.get("paper_id")
        if key is None:
            key = f"document:{source.get('document_id')}"
        result.add(str(key))
    return result


def _clean_cited_items(
    values: Any,
    *,
    allowed: set[str],
    source_by_id: dict[str, dict[str, Any]],
    fields: tuple[str, ...],
    min_distinct_papers: int,
    maximum: int,
) -> list[dict[str, Any]]:
    if not isinstance(values, list):
        return []
    cleaned = []
    for value in values[:maximum]:
        if not isinstance(value, dict):
            continue
        evidence_ids = _valid_evidence_ids(value.get("evidence_ids"), allowed)
        if len(_distinct_papers(evidence_ids, source_by_id)) < min_distinct_papers:
            continue
        item = {field: str(value.get(field) or "").strip() for field in fields}
        if not any(item.values()):
            continue
        item["evidence_ids"] = evidence_ids
        cleaned.append(item)
    return cleaned


async def analyze_research_query(
    query: str,
    *,
    limit: int = 12,
    max_candidates: int = 3,
) -> dict[str, Any]:
    """Run a query-scoped, evidence-bounded research analysis over the indexed corpus."""
    normalized_query = query.strip()
    if not normalized_query:
        raise ValueError("Research query must not be empty")

    retrieval = retrieve_graph_rag(normalized_query, limit=max(4, min(limit, 30)))
    hits = retrieval.get("items", []) if isinstance(retrieval, dict) else []
    sources, selected_hits = _prepare_sources(hits, max(4, min(limit, 30)))
    source_by_id = {item["evidence_id"]: item for item in sources}
    distinct_papers = _distinct_papers(list(source_by_id), source_by_id)

    base = {
        "query": normalized_query,
        "scope": "indexed_corpus",
        "retrieved_source_count": len(sources),
        "distinct_paper_count": len(distinct_papers),
        "sources": sources,
        "limitations": [
            "Analysis is limited to the papers and excerpts retrieved from the currently indexed corpus.",
            "A candidate gap is not proof of global novelty or absence of prior work.",
            "Generated hypotheses and experiment plans are proposals, not validated findings.",
        ],
    }
    if len(distinct_papers) < 2:
        return {
            **base,
            "status": "insufficient_evidence",
            "executive_summary": "At least two distinct indexed papers are required for a cross-paper research analysis.",
            "themes": [],
            "research_gaps": [],
            "hypotheses": [],
            "warning": "No gap or hypothesis was generated from insufficient independent paper coverage.",
        }

    evidence_text = "\n\n".join(
        f"[{item['evidence_id']}] paper_id={item.get('paper_id')} "
        f"document_id={item.get('document_id')} title={item.get('title')} "
        f"section={item.get('section')}\n{item['excerpt']}"
        for item in sources
    )
    prompt = f"""Research question: {normalized_query}

Retrieved source excerpts (the exclusive basis for factual claims):
{evidence_text}

Return this JSON shape:
{{
  "executive_summary": "Cautious cross-paper summary",
  "themes": [{{"theme": "name", "synthesis": "reported pattern", "evidence_ids": ["EVIDENCE 1"]}}],
  "research_gaps": [{{"title": "specific candidate opportunity", "rationale": "what this retrieved corpus suggests and why", "evidence_ids": ["EVIDENCE 1", "EVIDENCE 2"]}}],
  "hypotheses": [{{"statement": "falsifiable proposed hypothesis", "rationale": "evidence-grounded motivation", "experiment": "controlled experiment proposal", "possible_measurements": ["metric"], "evidence_ids": ["EVIDENCE 1", "EVIDENCE 2"]}}],
  "disagreements": [{{"claim": "specific disagreement", "explanation": "what differs", "evidence_ids": ["EVIDENCE 1", "EVIDENCE 2"]}}],
  "limitations": ["what the retrieved excerpts cannot establish"]
}}

Rules:
- Every theme, gap, hypothesis, and disagreement must cite exact evidence IDs.
- Every research gap and hypothesis must cite at least two distinct papers.
- Prefer explicit limitations, future-work statements, conflicting results, or untested settings.
- Do not call a topic unexplored just because it is absent from these excerpts.
- Hypotheses must be falsifiable; experiments must include a comparison or control.
- If evidence does not support a section, return an empty array rather than inventing content.
"""
    try:
        result = await get_llm_provider().structured(prompt, system=SYSTEM, temperature=0.0)
        if not isinstance(result, dict):
            raise ValueError("Research engine provider returned a non-object response")
        summary = str(result.get("executive_summary") or "").strip()
        if not summary:
            raise ValueError("Research engine response omitted executive_summary")
    except Exception as exc:
        return {
            **base,
            "status": "generation_failed",
            "executive_summary": "Evidence was retrieved, but the language-model analysis could not be completed.",
            "themes": [],
            "research_gaps": [],
            "hypotheses": [],
            "disagreements": [],
            "limitations": base["limitations"] + [f"Generation failure: {str(exc)[:240]}"],
        }

    allowed = set(source_by_id)
    themes = _clean_cited_items(
        result.get("themes"), allowed=allowed, source_by_id=source_by_id,
        fields=("theme", "synthesis"), min_distinct_papers=1, maximum=8,
    )
    gaps = _clean_cited_items(
        result.get("research_gaps"), allowed=allowed, source_by_id=source_by_id,
        fields=("title", "rationale"), min_distinct_papers=2, maximum=max_candidates,
    )
    hypotheses = _clean_cited_items(
        result.get("hypotheses"), allowed=allowed, source_by_id=source_by_id,
        fields=("statement", "rationale", "experiment"), min_distinct_papers=2, maximum=max_candidates,
    )
    raw_hypotheses = result.get("hypotheses", [])
    for item in hypotheses:
        raw = next((x for x in raw_hypotheses if isinstance(x, dict)
                    and str(x.get("statement") or "").strip() == item["statement"]), {})
        measurements = raw.get("possible_measurements", [])
        item["possible_measurements"] = (
            list(dict.fromkeys(str(x).strip() for x in measurements if str(x).strip()))[:10]
            if isinstance(measurements, list) else []
        )
        if not item["possible_measurements"]:
            item["experiment"] = ""

    disagreements = _clean_cited_items(
        result.get("disagreements"), allowed=allowed, source_by_id=source_by_id,
        fields=("claim", "explanation"), min_distinct_papers=2, maximum=8,
    )

    for candidate in gaps:
        critique = await critique_research_gap(
            candidate["title"], candidate["rationale"], limit=min(8, len(selected_hits)),
            retrieved_hits=selected_hits,
        )
        critic_evidence_ids = []
        original_by_provenance = {
            (str(item.get("paper_id")), str(item.get("document_id")), str(item.get("chunk_id"))): item["evidence_id"]
            for item in sources
        }
        for critic_source in critique.get("sources", []) if isinstance(critique.get("sources"), list) else []:
            if not isinstance(critic_source, dict):
                continue
            key = (
                str(critic_source.get("paper_id")),
                str(critic_source.get("document_id")),
                str(critic_source.get("chunk_id")),
            )
            mapped = original_by_provenance.get(key)
            if mapped and mapped not in critic_evidence_ids:
                critic_evidence_ids.append(mapped)
        critic_papers = _distinct_papers(critic_evidence_ids, source_by_id)
        candidate["critic"] = {
            "verdict": critique.get("verdict", "review"),
            "rationale": critique.get("rationale", "Critic did not return a rationale."),
            "evidence_ids": critic_evidence_ids,
            "distinct_paper_count": len(critic_papers),
        }
        candidate["status"] = (
            "critic_supported_candidate"
            if candidate["critic"]["verdict"] == "accept" and len(critic_papers) >= 2
            else "needs_review"
        )

    return {
        **base,
        "status": "completed",
        "executive_summary": summary,
        "themes": themes,
        "research_gaps": gaps,
        "hypotheses": hypotheses,
        "disagreements": disagreements,
        "limitations": list(dict.fromkeys(
            base["limitations"] + [
                str(x) for x in result.get("limitations", []) if str(x).strip()
            ]
        )),
        "proposal_disclaimer": "AI-generated hypotheses and experiments are proposals requiring validation; they are not established findings.",
    }
