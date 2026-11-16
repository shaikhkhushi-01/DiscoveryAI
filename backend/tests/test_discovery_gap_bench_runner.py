import json

import pytest

from app.services.evaluation.discovery_gap_bench import load_benchmark
from app.services.evaluation.runner import evaluate_benchmark


def _benchmark(status="adjudicated"):
    return {
        "schema_version": "1.0",
        "benchmark_id": "pilot",
        "benchmark_version": "1.0.0",
        "annotation_rubric_version": "rubric-1",
        "records": [
            {
                "record_id": "r1",
                "research_question": "Does method X address task Y?",
                "corpus_snapshot": {
                    "corpus_id": "corpus-1",
                    "snapshot_date": "2026-11-01",
                    "paper_ids": ["p1", "p2"],
                    "scope_statement": "Two-paper synthetic test corpus.",
                },
                "candidate_gap": {
                    "candidate_id": "g1",
                    "title": "Task Y",
                    "description": "Evaluate method X on task Y.",
                    "gap_type": "experiment",
                },
                "gold_evidence": {
                    "supporting": [{
                        "paper_id": "p1", "document_id": "d1", "chunk_id": "c1",
                        "relevance": 3, "rationale": "Directly addresses the task.",
                    }],
                    "contradictory": [],
                },
                "gold_assessment": {
                    "gap_status": "supported",
                    "novelty_within_corpus": 2,
                    "relevance": 3,
                    "feasibility": 2,
                    "evidence_quality": 3,
                },
                "annotations": {
                    "annotator_ids": ["reviewer-a", "reviewer-b"],
                    "annotated_at": "2026-11-02",
                    "adjudication_status": status,
                    "adjudication_notes": "Resolved in pilot." if status == "adjudicated" else None,
                },
                "split": "test",
            }
        ],
    }


def _predictions():
    return {
        "run_metadata": {
            "run_id": "run-1",
            "system_id": "discoveryai",
            "system_version": "0.1",
            "code_revision": "abc123",
            "corpus_id": "corpus-1",
            "benchmark_version": "1.0.0",
            "model_provider": "test",
            "model_name": "deterministic-fixture",
            "prompt_version": "prompt-1",
            "embedding_model": "fixture",
            "retrieval_config": "top-k=5",
        },
        "predictions": [{
            "record_id": "r1",
            "gap_status": "supported",
            "ratings": {
                "novelty_within_corpus": 2,
                "relevance": 3,
                "feasibility": 2,
                "evidence_quality": 3,
            },
            "evidence": [{
                "paper_id": "p1", "document_id": "d1", "chunk_id": "c1",
                "stance": "supporting",
            }],
        }],
    }


def test_pending_annotations_never_produce_official_metrics(tmp_path):
    benchmark = tmp_path / "gold.json"
    benchmark.write_text(json.dumps(_benchmark("pending")), encoding="utf-8")
    with pytest.raises(ValueError, match="no adjudicated records"):
        load_benchmark(benchmark, require_evaluable=True)


def test_runner_computes_metrics_only_for_complete_adjudicated_split(tmp_path):
    benchmark = tmp_path / "gold.json"
    predictions = tmp_path / "predictions.json"
    benchmark.write_text(json.dumps(_benchmark()), encoding="utf-8")
    predictions.write_text(json.dumps(_predictions()), encoding="utf-8")

    report = evaluate_benchmark(benchmark, predictions, split="test")

    assert report["benchmark"]["evaluated_record_count"] == 1
    assert report["metrics"]["gap_status"]["accuracy"] == 1.0
    assert report["metrics"]["aggregate"]["evidence_f1"]["mean"] == 1.0
    assert report["metrics"]["aggregate"]["rating_mae"]["mean"] == 0.0
    assert "not claims of global" in report["limitations"][1]


def test_runner_rejects_prediction_from_outside_frozen_corpus(tmp_path):
    benchmark = tmp_path / "gold.json"
    predictions = _predictions()
    predictions["predictions"][0]["evidence"][0]["paper_id"] = "unknown-paper"
    prediction_file = tmp_path / "predictions.json"
    benchmark.write_text(json.dumps(_benchmark()), encoding="utf-8")
    prediction_file.write_text(json.dumps(predictions), encoding="utf-8")

    with pytest.raises(ValueError, match="outside the selected frozen corpus"):
        evaluate_benchmark(benchmark, prediction_file, split="test")


def test_runner_refuses_to_score_when_test_split_is_empty(tmp_path):
    benchmark = _benchmark()
    benchmark["records"][0]["split"] = "train"
    benchmark_file = tmp_path / "gold.json"
    prediction_file = tmp_path / "predictions.json"
    benchmark_file.write_text(json.dumps(benchmark), encoding="utf-8")
    prediction_file.write_text(json.dumps(_predictions()), encoding="utf-8")

    with pytest.raises(ValueError, match="no adjudicated records in split"):
        evaluate_benchmark(benchmark_file, prediction_file, split="test")
