from __future__ import annotations

"""Common prediction-generation adapters for the five Day 4 systems.

This module generates *model predictions*, never gold labels. It is intentionally
fail-closed: every output is tied to retrieved corpus evidence and run metadata.
"""

import asyncio
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Awaitable, Callable

from app.services.embeddings.factory import get_embedding_provider
from app.services.graph_rag.pipeline import retrieve_graph_rag
from app.services.llm.factory import get_llm_provider
from app.services.rag import answer_question
from app.services.research_synthesis import synthesize_research
from app.services.retrieval.hybrid import hybrid_search
from app.services.retrieval.reranker import rerank
from app.services.vector_store import search_vectors

SYSTEMS = ("llm_only", "vector_rag", "graph_rag", "hybrid_retrieval", "discoveryai_full")
RATING_FIELDS = ("novelty_within_corpus", "relevance", "feasibility", "evidence_quality")
VALID_STATUSES = {"supported", "contradicted", "inconclusive"}
MAX_EVIDENCE = 8

SYSTEM_PROMPT = """You are producing a research benchmark prediction, NOT a gold annotation.
Use only supplied evidence. Do not invent citations, papers, document IDs, chunk IDs,
methods, results, or claims. If evidence is insufficient, choose inconclusive.
Return one JSON object with gap_status (supported|contradicted|inconclusive),
ratings (four integer scores 0..3), and evidence (array of objects with evidence_index
(integer referring to supplied evidence index, 0-based), stance (supporting|contradictory)).
Do not return paper/document/chunk IDs; the caller attaches verified IDs.
Ratings are model estimates, not expert judgments.
"""

Retriever = Callable[[str, int], Awaitable[list[dict[str, Any]]]]


async def _vector(query: str, limit: int) -> list[dict[str, Any]]:
    vector = get_embedding_provider().embed([query])[0]
    return search_vectors(vector, limit=limit)


async def _graph(query: str, limit: int) -> list[dict[str, Any]]:
    result = retrieve_graph_rag(query, limit=limit)
    return result.get("items", [])


async def _hybrid(query: str, limit: int) -> list[dict[str, Any]]:
    return rerank(query, hybrid_search(query, limit=max(limit * 3, 12)), limit=limit)


async def _full(query: str, limit: int) -> list[dict[str, Any]]:
    result = await synthesize_research(query, mode="literature_review", limit=limit)
    sources = result.get("sources", [])
    # Synthesis sources retain the original evidence identifiers.
    return sources


async def _llm_only(query: str, limit: int) -> list[dict[str, Any]]:
    del query, limit
    return []


RETRIEVERS: dict[str, Retriever] = {
    "llm_only": _llm_only,
    "vector_rag": _vector,
    "graph_rag": _graph,
    "hybrid_retrieval": _hybrid,
    "discoveryai_full": _full,
}


def _evidence_identity(item: dict[str, Any]) -> dict[str, str] | None:
    paper_id = item.get("paper_id")
    document_id = item.get("document_id")
    chunk_id = item.get("chunk_id")
    if any(value is None or not str(value).strip() for value in (paper_id, document_id, chunk_id)):
        return None
    return {
        "paper_id": str(paper_id),
        "document_id": str(document_id),
        "chunk_id": str(chunk_id),
    }


async def generate_prediction(system_id: str, record: dict[str, Any], *, evidence_budget: int = MAX_EVIDENCE) -> dict[str, Any]:
    if system_id not in RETRIEVERS:
        raise ValueError(f"unsupported system_id: {system_id}")
    if not isinstance(record, dict) or not isinstance(record.get("record_id"), str):
        raise ValueError("benchmark record must contain a string record_id")
    query = record.get("research_question")
    if not isinstance(query, str) or not query.strip():
        raise ValueError(f"{record['record_id']}: research_question is required")
    if not isinstance(evidence_budget, int) or isinstance(evidence_budget, bool) or not 1 <= evidence_budget <= 8:
        raise ValueError("evidence_budget must be an integer from 1 to 8")

    retrieved = await RETRIEVERS[system_id](query, evidence_budget)
    evidence_items: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in retrieved:
        if not isinstance(item, dict):
            continue
        identity = _evidence_identity(item)
        if identity is None:
            continue
        key = (identity["paper_id"], identity["document_id"], identity["chunk_id"])
        if key in seen:
            continue
        seen.add(key)
        text = str(item.get("text") or item.get("excerpt") or "").strip()
        if not text:
            continue
        evidence_items.append({**identity, "text": text[:1800]})
        if len(evidence_items) >= evidence_budget:
            break

    prompt = f"""Research question: {query}

Available corpus evidence (retrieval systems: exclusive source; llm_only: empty by design, use pretrained knowledge cautiously):
{json.dumps(evidence_items, ensure_ascii=False)}

Return exactly:
{{"gap_status":"inconclusive","ratings":{{"novelty_within_corpus":0,"relevance":0,"feasibility":0,"evidence_quality":0}},"evidence":[]}}

Evidence array entries must cite evidence_index values from the supplied list. Use an empty
array when there is no traceable evidence. A model-only answer with no retrieval must not
invent citations. Ratings are coarse model estimates and must not be represented as expert
annotations. Do not output narrative prose.
"""
    system_prompt = SYSTEM_PROMPT
    if system_id == "llm_only":
        system_prompt = """You are the closed-book baseline for a corpus-grounded research benchmark.\nNo corpus evidence is supplied. Do not claim that a gap is supported or contradicted within a corpus, do not infer that a paper exists, and do not invent citations. Return gap_status=inconclusive, all four ratings as 0, and an empty evidence array. This baseline intentionally has no retrieval access."""
    result = await get_llm_provider().structured(prompt, system=system_prompt, temperature=0.0)
    if not isinstance(result, dict):
        raise ValueError(f"{system_id}/{record['record_id']}: structured model response must be an object")
    status = result.get("gap_status")
    if status not in VALID_STATUSES:
        raise ValueError(f"{system_id}/{record['record_id']}: invalid gap_status")
    ratings = result.get("ratings")
    if not isinstance(ratings, dict):
        raise ValueError(f"{system_id}/{record['record_id']}: ratings must be an object")
    clean_ratings: dict[str, int] = {}
    for field in RATING_FIELDS:
        value = ratings.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 3:
            raise ValueError(f"{system_id}/{record['record_id']}: {field} must be integer 0..3")
        clean_ratings[field] = value

    cited = result.get("evidence")
    if not isinstance(cited, list):
        raise ValueError(f"{system_id}/{record['record_id']}: evidence must be an array")
    output_evidence = []
    used: set[int] = set()
    for citation in cited:
        if not isinstance(citation, dict):
            raise ValueError("model evidence entries must be objects")
        index = citation.get("evidence_index")
        stance = citation.get("stance")
        if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < len(evidence_items):
            raise ValueError("model cited an evidence index outside supplied evidence")
        if stance not in {"supporting", "contradictory"}:
            raise ValueError("model evidence stance must be supporting or contradictory")
        if index in used:
            continue
        used.add(index)
        output_evidence.append({k: evidence_items[index][k] for k in ("paper_id", "document_id", "chunk_id")} | {"stance": stance})
    if system_id == "llm_only" or not evidence_items:
        # A closed-book or empty-retrieval run cannot establish support/contradiction
        # within the indexed corpus. Never let a free-form model verdict replace evidence.
        status = "inconclusive"
        clean_ratings = {field: 0 for field in RATING_FIELDS}
        output_evidence = []
    return {"record_id": record["record_id"], "gap_status": status, "ratings": clean_ratings, "evidence": output_evidence}


def _run_metadata(system_id: str, benchmark: dict[str, Any], *, code_revision: str, model_provider: str, model_name: str, prompt_version: str, embedding_model: str, retrieval_config: str) -> dict[str, str]:
    records = benchmark.get("records", [])
    snapshots = {row.get("corpus_snapshot", {}).get("corpus_id") for row in records if isinstance(row, dict)}
    if len(snapshots) != 1 or not next(iter(snapshots)):
        raise ValueError("benchmark must reference exactly one non-empty corpus snapshot ID")
    return {
        "run_id": str(uuid.uuid4()),
        "system_id": system_id,
        "system_version": "adapter-v1",
        "code_revision": code_revision,
        "corpus_id": str(next(iter(snapshots))),
        "benchmark_version": str(benchmark.get("benchmark_version") or ""),
        "model_provider": model_provider,
        "model_name": model_name,
        "prompt_version": prompt_version,
        "embedding_model": embedding_model,
        "retrieval_config": retrieval_config,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }


async def generate_system_predictions(benchmark_path: str | Path, output_dir: str | Path, *, split: str = "test", evidence_budget: int = MAX_EVIDENCE, code_revision: str, model_provider: str, model_name: str, prompt_version: str = "baseline-prompt-v1", embedding_model: str = "configured-embedding-provider", retrieval_config: str = "top_k=8;reranker=repository-default") -> dict[str, str]:
    benchmark = json.loads(Path(benchmark_path).read_text(encoding="utf-8"))
    if not isinstance(benchmark, dict) or not isinstance(benchmark.get("records"), list):
        raise ValueError("benchmark JSON must contain records array")
    selected = [r for r in benchmark["records"] if isinstance(r, dict) and r.get("split") == split and (r.get("annotations") or {}).get("adjudication_status") == "adjudicated"]
    if not selected:
        raise ValueError(f"no adjudicated records in split {split!r}; no predictions generated")
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, str] = {}
    staged_payloads: dict[str, dict[str, Any]] = {}
    selected_benchmark = {**benchmark, "records": selected}
    # Generate every system before replacing any prior artifact. A failed arm therefore
    # cannot leave a misleading partial five-system result set in the output directory.
    for system_id in SYSTEMS:
        metadata = _run_metadata(system_id, selected_benchmark, code_revision=code_revision, model_provider=model_provider, model_name=model_name, prompt_version=prompt_version, embedding_model=embedding_model, retrieval_config=retrieval_config)
        predictions = []
        for record in selected:
            predictions.append(await generate_prediction(system_id, record, evidence_budget=evidence_budget))
        staged_payloads[system_id] = {"run_metadata": metadata, "predictions": predictions}
    for system_id, payload in staged_payloads.items():
        path = target / f"{system_id}.predictions.json"
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        temporary.replace(path)
        outputs[system_id] = str(path)
    return outputs
