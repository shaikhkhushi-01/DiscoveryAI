from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.evaluation.package_evaluation_run import build_run_manifest


def _write(path: Path, value: dict) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def _fixtures(tmp_path: Path):
    benchmark = _write(tmp_path / "benchmark.json", {
        "benchmark_id": "bench-1", "benchmark_version": "1.0",
        "annotation_rubric_version": "1.0",
    })
    metadata = {
        "run_id": "run-1", "system_id": "discoveryai_full",
        "system_version": "1.2", "model_provider": "provider",
        "model_name": "model", "prompt_version": "prompt-v1",
        "embedding_model": "embed-v1", "retrieval_config": "top-k=8",
        "corpus_id": "corpus-1",
    }
    predictions = _write(tmp_path / "predictions.json", {
        "run_metadata": metadata,
        "predictions": [{"record_id": "r1"}, {"record_id": "r2"}],
    })
    report = _write(tmp_path / "report.json", {
        "run_metadata": metadata,
        "benchmark": {
            "benchmark_id": "bench-1", "benchmark_version": "1.0",
            "annotation_rubric_version": "1.0", "corpus_ids": ["corpus-1"],
            "split": "test", "evaluated_record_count": 2,
        },
    })
    return benchmark, predictions, report


def test_manifest_hashes_artifacts_and_records_provenance(tmp_path):
    benchmark, predictions, report = _fixtures(tmp_path)
    protocol = _write(tmp_path / "protocol.md", {"protocol": "v1"})
    manifest = build_run_manifest(
        benchmark_path=benchmark, predictions_path=predictions, report_path=report,
        protocol_path=protocol, code_revision="abc123",
    )
    assert manifest["run_id"] == "run-1"
    assert manifest["benchmark"]["prediction_record_count"] == 2
    assert len(manifest["artifacts"]["predictions"]["sha256"]) == 64
    assert manifest["code_revision"] == "abc123"


def test_manifest_rejects_metadata_drift(tmp_path):
    benchmark, predictions, report = _fixtures(tmp_path)
    payload = json.loads(report.read_text())
    payload["run_metadata"]["model_name"] = "different-model"
    report.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="run_metadata differs"):
        build_run_manifest(
            benchmark_path=benchmark, predictions_path=predictions, report_path=report,
            code_revision="abc123",
        )


def test_manifest_rejects_benchmark_mismatch(tmp_path):
    benchmark, predictions, report = _fixtures(tmp_path)
    payload = json.loads(report.read_text())
    payload["benchmark"]["benchmark_version"] = "wrong"
    report.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="benchmark_version"):
        build_run_manifest(
            benchmark_path=benchmark, predictions_path=predictions, report_path=report,
            code_revision="abc123",
        )


def test_manifest_requires_unique_prediction_ids(tmp_path):
    benchmark, predictions, report = _fixtures(tmp_path)
    payload = json.loads(predictions.read_text())
    payload["predictions"][1]["record_id"] = "r1"
    predictions.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="duplicate record IDs"):
        build_run_manifest(
            benchmark_path=benchmark, predictions_path=predictions, report_path=report,
            code_revision="abc123",
        )


def test_manifest_requires_code_revision(tmp_path, monkeypatch):
    benchmark, predictions, report = _fixtures(tmp_path)
    monkeypatch.delenv("GITHUB_SHA", raising=False)
    with pytest.raises(ValueError, match="code revision is required"):
        build_run_manifest(
            benchmark_path=benchmark, predictions_path=predictions, report_path=report,
        )
