import json

import pytest

from app.services.evaluation.runner import evaluate_benchmark, write_report
from app.tests.test_discovery_gap_bench import valid_benchmark, valid_record


def _write_inputs(tmp_path):
    benchmark_path = tmp_path / "gold.json"
    predictions_path = tmp_path / "predictions.json"
    record = valid_record()
    benchmark_path.write_text(json.dumps(valid_benchmark([record])), encoding="utf-8")
    predictions = {
        "run_metadata": {
            "run_id": "run-001", "system_id": "discoveryai", "system_version": "1.0",
            "code_revision": "abc123", "corpus_id": "corpus-v1",
            "benchmark_version": "0.1.0", "model_provider": "gemini",
            "model_name": "test-model", "prompt_version": "critic-v1",
            "embedding_model": "embedding-v1", "retrieval_config": "top-k=8",
        },
        "predictions": [{
            "record_id": "record-1", "gap_status": "inconclusive",
            "ratings": {
                "novelty_within_corpus": 2, "relevance": 3,
                "feasibility": 2, "evidence_quality": 3,
            },
            "evidence": [
                {"paper_id": "paper-1", "document_id": "doc-1", "chunk_id": "chunk-1", "stance": "supporting"},
                {"paper_id": "paper-2", "document_id": "doc-2", "chunk_id": "chunk-2", "stance": "contradictory"},
            ],
        }],
    }
    predictions_path.write_text(json.dumps(predictions), encoding="utf-8")
    return benchmark_path, predictions_path, predictions


def test_runner_reports_perfect_match_and_provenance(tmp_path):
    benchmark, predictions, _ = _write_inputs(tmp_path)
    report = evaluate_benchmark(benchmark, predictions)
    assert report["benchmark"]["evaluated_record_count"] == 1
    assert report["metrics"]["gap_status"]["accuracy"] == 1.0
    assert report["metrics"]["aggregate"]["evidence_f1"]["mean"] == 1.0
    assert report["metrics"]["aggregate"]["rating_mae"]["mean"] == 0.0
    assert report["run_metadata"]["code_revision"] == "abc123"


def test_runner_rejects_missing_predictions(tmp_path):
    benchmark, predictions, payload = _write_inputs(tmp_path)
    payload["predictions"] = []
    predictions.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="missing predictions"):
        evaluate_benchmark(benchmark, predictions)


def test_runner_rejects_untracked_or_duplicate_prediction_ids(tmp_path):
    benchmark, predictions, payload = _write_inputs(tmp_path)
    payload["predictions"][0]["record_id"] = "not-in-gold"
    predictions.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="not in the selected gold split"):
        evaluate_benchmark(benchmark, predictions)


def test_runner_rejects_benchmark_version_mismatch(tmp_path):
    benchmark, predictions, payload = _write_inputs(tmp_path)
    payload["run_metadata"]["benchmark_version"] = "wrong-version"
    predictions.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="does not match"):
        evaluate_benchmark(benchmark, predictions)


def test_runner_refuses_pending_or_empty_test_split(tmp_path):
    benchmark, predictions, payload = _write_inputs(tmp_path)
    gold = json.loads(benchmark.read_text(encoding="utf-8"))
    gold["records"][0]["annotations"]["adjudication_status"] = "pending"
    gold["records"][0]["annotations"]["adjudication_notes"] = None
    benchmark.write_text(json.dumps(gold), encoding="utf-8")
    with pytest.raises(ValueError, match="no adjudicated records"):
        evaluate_benchmark(benchmark, predictions)


def test_report_writer_creates_parent_directory(tmp_path):
    benchmark, predictions, _ = _write_inputs(tmp_path)
    report = evaluate_benchmark(benchmark, predictions)
    output = tmp_path / "reports" / "run.json"
    write_report(report, output)
    assert json.loads(output.read_text(encoding="utf-8"))["report_schema_version"] == "1.0"
