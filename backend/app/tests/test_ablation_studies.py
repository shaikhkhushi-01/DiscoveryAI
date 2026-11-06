import json

import pytest

from app.services.evaluation.ablations import ABLATION_VARIANTS, compare_ablations
from app.tests.test_discovery_gap_bench import valid_benchmark, valid_record


def _inputs(tmp_path):
    benchmark = tmp_path / "gold.json"
    benchmark.write_text(json.dumps(valid_benchmark([valid_record()])), encoding="utf-8")
    paths = {}
    for variant in ABLATION_VARIANTS:
        disabled = [] if variant == "full" else [variant.removeprefix("without_")]
        payload = {
            "run_metadata": {
                "run_id": f"run-{variant}", "system_id": "discoveryai",
                "system_version": "1.0", "code_revision": "abc123",
                "corpus_id": "corpus-v1", "benchmark_version": "0.1.0",
                "model_provider": "test-provider", "model_name": "test-model",
                "prompt_version": "prompt-v1", "embedding_model": "embedding-v1",
                "retrieval_config": "fixed", "ablation_id": variant,
                "disabled_components": disabled,
            },
            "predictions": [{
                "record_id": "record-1", "gap_status": "inconclusive",
                "ratings": {"novelty_within_corpus": 2, "relevance": 3, "feasibility": 2, "evidence_quality": 3},
                "evidence": [
                    {"paper_id": "paper-1", "document_id": "doc-1", "chunk_id": "chunk-1", "stance": "supporting"},
                    {"paper_id": "paper-2", "document_id": "doc-2", "chunk_id": "chunk-2", "stance": "contradictory"},
                ],
            }],
        }
        path = tmp_path / f"{variant}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        paths[variant] = path
    return benchmark, paths


def test_ablation_comparison_uses_all_variants_and_paired_records(tmp_path):
    benchmark, paths = _inputs(tmp_path)
    report = compare_ablations(benchmark, paths)
    assert set(report["variants"]) == set(ABLATION_VARIANTS)
    assert report["protocol"]["record_count"] == 1
    assert set(report["paired_component_effects"]) == set(ABLATION_VARIANTS) - {"full"}


def test_ablation_comparison_requires_exact_variants(tmp_path):
    benchmark, paths = _inputs(tmp_path)
    paths.pop("without_graph_retrieval")
    with pytest.raises(ValueError, match="exactly the full run"):
        compare_ablations(benchmark, paths)


def test_ablation_comparison_rejects_wrong_disabled_component(tmp_path):
    benchmark, paths = _inputs(tmp_path)
    payload = json.loads(paths["without_research_critic"].read_text(encoding="utf-8"))
    payload["run_metadata"]["disabled_components"] = ["vector_retrieval"]
    paths["without_research_critic"].write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="disabled_components"):
        compare_ablations(benchmark, paths)


def test_ablation_comparison_rejects_different_corpus_snapshot(tmp_path):
    benchmark, paths = _inputs(tmp_path)
    payload = json.loads(paths["without_temporal_signals"].read_text(encoding="utf-8"))
    payload["run_metadata"]["corpus_id"] = "other-corpus"
    paths["without_temporal_signals"].write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="corpus_id does not match"):
        compare_ablations(benchmark, paths)
