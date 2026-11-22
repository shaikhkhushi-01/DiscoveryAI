from __future__ import annotations

"""Controlled, independently generated DiscoveryAI ablation predictions.

Each variant changes executable component switches. Metadata alone is never used
to simulate a component removal. These are model predictions, not gold labels.
"""

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services.evaluation.prediction_adapters import (
    MAX_EVIDENCE, RATING_FIELDS, SYSTEM_PROMPT, VALID_STATUSES, _evidence_identity,
)
from app.services.evidence.scoring import compute_discovery_score
from app.services.graph_rag.pipeline import retrieve_graph_rag
from app.services.graph_rag.retrieval import graph_expand, graph_search
from app.services.llm.factory import get_llm_provider
from app.services.gap_detection.research_critic import critique_research_gap
from app.services.retrieval.hybrid import hybrid_search
from app.services.retrieval.reranker import rerank
from app.services.trends.temporal import topic_timeline

ABLATION_CONFIGS: dict[str, dict[str, bool]] = {
    "full": {
        "vector_retrieval": True, "graph_retrieval": True,
        "research_critic": True, "temporal_signals": True, "discovery_score": True,
    },
    "without_vector_retrieval": {
        "vector_retrieval": False, "graph_retrieval": True,
        "research_critic": True, "temporal_signals": True, "discovery_score": True,
    },
    "without_graph_retrieval": {
        "vector_retrieval": True, "graph_retrieval": False,
        "research_critic": True, "temporal_signals": True, "discovery_score": True,
    },
    "without_research_critic": {
        "vector_retrieval": True, "graph_retrieval": True,
        "research_critic": False, "temporal_signals": True, "discovery_score": True,
    },
    "without_temporal_signals": {
        "vector_retrieval": True, "graph_retrieval": True,
        "research_critic": True, "temporal_signals": False, "discovery_score": True,
    },
    "without_discovery_score": {
        "vector_retrieval": True, "graph_retrieval": True,
        "research_critic": True, "temporal_signals": True, "discovery_score": False,
    },
}
COMPONENT_NAMES = tuple(ABLATION_CONFIGS["full"])


@dataclass(frozen=True)
class AblationConfig:
    ablation_id: str
    vector_retrieval: bool
    graph_retrieval: bool
    research_critic: bool
    temporal_signals: bool
    discovery_score: bool

    @classmethod
    def from_id(cls, ablation_id: str) -> "AblationConfig":
        if ablation_id not in ABLATION_CONFIGS:
            raise ValueError(f"unsupported ablation_id: {ablation_id}")
        return cls(ablation_id=ablation_id, **ABLATION_CONFIGS[ablation_id])

    @property
    def disabled_components(self) -> list[str]:
        return [name for name in COMPONENT_NAMES if not getattr(self, name)]


def _retrieve(query: str, config: AblationConfig, limit: int) -> list[dict[str, Any]]:
    if config.vector_retrieval and config.graph_retrieval:
        result = retrieve_graph_rag(query, limit=limit)
        return result.get("items", [])
    if config.vector_retrieval:
        candidates = hybrid_search(query, limit=max(limit * 3, 12))
        return rerank(query, candidates, limit=limit)
    if config.graph_retrieval:
        # Graph-only retrieval intentionally returns graph records, not fabricated
        # document chunks. Without traceable document/chunk IDs these cannot be
        # cited as text evidence by the prediction schema.
        graph_hits = graph_search(query, limit=max(limit * 3, 20))
        paper_ids = []
        for hit in graph_hits:
            try:
                if hit.get("paper_id") is not None:
                    paper_ids.append(int(hit["paper_id"]))
            except (TypeError, ValueError):
                continue
        expanded = graph_expand(sorted(set(paper_ids)), limit=max(limit * 5, 30))
        return graph_hits + expanded
    raise ValueError("at least one retrieval component must remain enabled")


async def generate_ablation_prediction(
    record: dict[str, Any], config: AblationConfig, *, evidence_budget: int = MAX_EVIDENCE,
) -> dict[str, Any]:
    if not isinstance(record, dict) or not isinstance(record.get("record_id"), str):
        raise ValueError("benchmark record must contain a string record_id")
    query = record.get("research_question")
    if not isinstance(query, str) or not query.strip():
        raise ValueError(f"{record.get('record_id')}: research_question is required")
    if not isinstance(evidence_budget, int) or isinstance(evidence_budget, bool) or not 1 <= evidence_budget <= MAX_EVIDENCE:
        raise ValueError(f"evidence_budget must be an integer from 1 to {MAX_EVIDENCE}")

    retrieved = _retrieve(query, config, evidence_budget)
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
        text = str(item.get("text") or item.get("excerpt") or "").strip()
        if not text:
            continue
        seen.add(key)
        evidence_items.append({**identity, "text": text[:1800]})
        if len(evidence_items) >= evidence_budget:
            break

    auxiliary: dict[str, Any] = {}
    if config.research_critic:
        # Critic receives exactly the current variant's retrieved records. In the
        # graph-only arm, metadata without text is not passed off as review evidence.
        critic_hits = [item for item in retrieved if item.get("text") or item.get("excerpt")]
        auxiliary["research_critic"] = await critique_research_gap(
            query, "", min(evidence_budget, 8), retrieved_hits=critic_hits,
        )
    if config.temporal_signals:
        # Exact topic lookup can legitimately return no rows; absence is recorded,
        # not replaced with guessed trend data.
        auxiliary["temporal_signals"] = topic_timeline(query, limit=20)
    if config.discovery_score:
        paper_ids = sorted({x["paper_id"] for x in evidence_items})
        score_input = {
            "retrieval_evidence_count": len(evidence_items),
            "supporting_signal": sum(
                1 for item in retrieved
                if float(item.get("rerank_score", 0) or 0) >= 0.5
            ),
            "supporting_papers": paper_ids,
            "contradictory_signal": any(bool(x.get("contradiction_detected")) for x in retrieved),
        }
        auxiliary["discovery_score"] = compute_discovery_score(score_input)

    prompt = f"""Research question: {query}

Traceable text evidence (exclusive source for paper claims):
{json.dumps(evidence_items, ensure_ascii=False)}

Enabled DiscoveryAI component outputs for this run:
{json.dumps(auxiliary, ensure_ascii=False, default=str)}

Use auxiliary outputs only as additional analysis of this same retrieved corpus.
Do not treat a critic verdict, temporal count, or heuristic score as expert gold truth.
If no traceable text evidence is supplied, gap_status MUST be inconclusive,
all ratings MUST be 0, and evidence MUST be an empty array.
Return exactly:
{{"gap_status":"inconclusive","ratings":{{"novelty_within_corpus":0,"relevance":0,"feasibility":0,"evidence_quality":0}},"evidence":[]}}
Evidence entries cite evidence_index (0-based) and stance (supporting|contradictory).
"""
    result = await get_llm_provider().structured(
        prompt, system=SYSTEM_PROMPT, temperature=0.0,
    )
    if not isinstance(result, dict):
        raise ValueError("ablation model response must be an object")
    status = result.get("gap_status")
    if status not in VALID_STATUSES:
        raise ValueError("model returned invalid gap_status")
    ratings = result.get("ratings")
    if not isinstance(ratings, dict):
        raise ValueError("model ratings must be an object")
    clean_ratings: dict[str, int] = {}
    for field in RATING_FIELDS:
        value = ratings.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 3:
            raise ValueError(f"{field} must be integer 0..3")
        clean_ratings[field] = value

    cited = result.get("evidence")
    if not isinstance(cited, list):
        raise ValueError("model evidence must be an array")
    output_evidence = []
    used: set[int] = set()
    for citation in cited:
        if not isinstance(citation, dict):
            raise ValueError("model evidence entries must be objects")
        index, stance = citation.get("evidence_index"), citation.get("stance")
        if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < len(evidence_items):
            raise ValueError("model cited evidence outside supplied evidence")
        if stance not in {"supporting", "contradictory"}:
            raise ValueError("invalid evidence stance")
        if index not in used:
            used.add(index)
            output_evidence.append({
                key: evidence_items[index][key]
                for key in ("paper_id", "document_id", "chunk_id")
            } | {"stance": stance})

    if not evidence_items:
        status = "inconclusive"
        clean_ratings = {field: 0 for field in RATING_FIELDS}
        output_evidence = []
    return {
        "record_id": record["record_id"], "gap_status": status,
        "ratings": clean_ratings, "evidence": output_evidence,
    }


def _benchmark_corpus_id(benchmark: dict[str, Any]) -> str:
    corpus_ids = {
        row.get("corpus_snapshot", {}).get("corpus_id")
        for row in benchmark["records"] if isinstance(row, dict)
    }
    if len(corpus_ids) != 1 or not next(iter(corpus_ids)):
        raise ValueError("benchmark must reference exactly one non-empty corpus snapshot ID")
    return str(next(iter(corpus_ids)))


async def generate_ablation_predictions(
    benchmark_path: str | Path, output_dir: str | Path, *,
    split: str = "test", evidence_budget: int = MAX_EVIDENCE,
    code_revision: str, model_provider: str, model_name: str,
    prompt_version: str = "ablation-prompt-v1",
    embedding_model: str = "configured-embedding-provider",
    retrieval_config: str = "top_k=8;reranker=repository-default",
) -> dict[str, str]:
    benchmark = json.loads(Path(benchmark_path).read_text(encoding="utf-8"))
    if not isinstance(benchmark, dict) or not isinstance(benchmark.get("records"), list):
        raise ValueError("benchmark JSON must contain a records array")
    selected = [
        row for row in benchmark["records"]
        if isinstance(row, dict) and row.get("split") == split
        and (row.get("annotations") or {}).get("adjudication_status") == "adjudicated"
    ]
    if not selected:
        raise ValueError(f"no adjudicated records in split {split!r}; no ablation outputs generated")
    corpus_id = _benchmark_corpus_id(benchmark)
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, str] = {}
    staged_payloads: dict[str, dict[str, Any]] = {}
    for ablation_id in ABLATION_CONFIGS:
        config = AblationConfig.from_id(ablation_id)
        predictions = [
            await generate_ablation_prediction(row, config, evidence_budget=evidence_budget)
            for row in selected
        ]
        metadata = {
            "run_id": str(uuid.uuid4()), "system_id": "discoveryai",
            "system_version": "ablation-adapter-v1", "code_revision": code_revision,
            "corpus_id": corpus_id,
            "benchmark_version": str(benchmark.get("benchmark_version") or ""),
            "model_provider": model_provider, "model_name": model_name,
            "prompt_version": prompt_version, "embedding_model": embedding_model,
            "retrieval_config": retrieval_config,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "ablation_id": ablation_id,
            "disabled_components": config.disabled_components,
            "enabled_components": [name for name in COMPONENT_NAMES if getattr(config, name)],
            "evidence_budget": evidence_budget,
        }
        staged_payloads[ablation_id] = {"run_metadata": metadata, "predictions": predictions}

    # Do not publish a partial six-arm result set if any variant fails. Stage every
    # artifact first, then atomically replace the corresponding files.
    staged_paths: dict[str, Path] = {}
    try:
        for ablation_id, payload in staged_payloads.items():
            path = target / f"{ablation_id}.predictions.json"
            temporary = path.with_suffix(path.suffix + ".tmp")
            temporary.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            staged_paths[ablation_id] = temporary
        for ablation_id, temporary in staged_paths.items():
            path = target / f"{ablation_id}.predictions.json"
            temporary.replace(path)
            outputs[ablation_id] = str(path)
    finally:
        for temporary in staged_paths.values():
            if temporary.exists():
                temporary.unlink()
    return outputs
