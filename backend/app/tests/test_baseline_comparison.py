import json

import pytest

from app.services.evaluation.baselines import BASELINE_SYSTEMS, compare_baselines
from app.tests.test_discovery_gap_bench import valid_benchmark, valid_record


def _write_baseline_inputs(tmp_path, *, evidence_count=2):
    benchmark = tmp_path / "gold.json"
    benchmark.write_text(json.dumps(valid_benchmark([valid_record()])), encoding="utf-8")
    paths = {}
    evidence = [
        {"paper_id": "paper-1", "document_id": "doc-1", "chunk_id": "chunk-1", "stance": "supporting"},
        {"paper_id": "paper-2", "document_id": "doc-2", "chunk_id": "chunk-2", "stance": "contradictory"},
    ][:evidence_count]
    for system in BASELINE_SYSTEMS:
        path = tmp_path / f"{system}.json"
        payload = {
            "run_metadata": {
                "run_id": f"run-{system}", "system_id": system, "system_version": "1.0",
                "code_revision": "abc123", "corpus_id": "corpus-v1",
                "benchmark_version": "0.1.0", "model_provider": "test-provider",
                "model_name": "test-model", "prompt_version": "prompt-v1",
                "embedding_model": "embedding-v1", "retrieval_config": "shared-budget-2",
            },
            "predictions": [{
                "record_id": "record-1", "gap_status": "inconclusive",
                "ratings": {
                    "novelty_within_corpus": 2, "relevance": 3,
                    "feasibility": 2, "evidence_quality": 3,
                },
                "evidence": evidence,
            }],
        }
        path.write_text(json.dumps(payload), encoding="utf-8")
        paths[system] = path
    return benchmark, paths


def test_comparison_runs_all_five_systems_on_same_records(tmp_path):
    benchmark, paths = _write_baseline_inputs(tmp_path)
    report = compare_baselines(benchmark, paths, evidence_budget=2)
    assert set(report["systems"]) == set(BASELINE_SYSTEMS)
    assert report["protocol"]["record_count"] == 1
    assert report["protocol"]["shared_max_evidence_items_per_record"] == 2
    assert report["systems"]["discoveryai_full"]["gap_status_accuracy"] == 1.0
    assert set(report["paired_full_system_comparisons"]) == set(BASELINE_SYSTEMS) - {"discoveryai_full"}


def test_comparison_requires_exact_five_baselines(tmp_path):
    benchmark, paths = _write_baseline_inputs(tmp_path)
    paths.pop("graph_rag")
    with pytest.raises(ValueError, match="exactly the five"):
        compare_baselines(benchmark, paths)


def test_comparison_rejects_system_identity_mismatch(tmp_path):
    benchmark, paths = _write_baseline_inputs(tmp_path)
    payload = json.loads(paths["llm_only"].read_text(encoding="utf-8"))
    payload["run_metadata"]["system_id"] = "vector_rag"
    paths["llm_only"].write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="system_id"):
        compare_baselines(benchmark, paths)


def test_comparison_enforces_shared_evidence_budget(tmp_path):
    benchmark, paths = _write_baseline_inputs(tmp_path, evidence_count=2)
    with pytest.raises(ValueError, match="shared evidence budget"):
        compare_baselines(benchmark, paths, evidence_budget=1)


def test_comparison_rejects_different_corpus_metadata(tmp_path):
    benchmark, paths = _write_baseline_inputs(tmp_path)
    payload = json.loads(paths["graph_rag"].read_text(encoding="utf-8"))
    payload["run_metadata"]["corpus_id"] = "other-corpus"
    paths["graph_rag"].write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="corpus_id does not match"):
        compare_baselines(benchmark, paths)
