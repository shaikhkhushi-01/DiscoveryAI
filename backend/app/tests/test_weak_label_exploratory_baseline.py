from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "evaluation" / "weak_label_exploratory_baseline.py"
SPEC = importlib.util.spec_from_file_location("weak_label_baseline", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def record(paper_id: str, split: str, abstract: str, gap: str) -> dict:
    return {
        "paper_id": paper_id,
        "split": split,
        "abstract": abstract,
        "research_gap_llm_inferred": gap,
        "generator_model": "mistral-small-latest",
        "primary_category": "cs.CL",
    }


def test_metrics_are_bounded_and_identical_text_scores_one():
    text = "Robust multilingual evaluation is missing."
    assert MODULE._token_f1(text, text) == pytest.approx(1.0)
    assert MODULE._rouge_l_f1(text, text) == pytest.approx(1.0)
    assert 0.0 <= MODULE._token_f1(text, "unrelated result") <= 1.0
    assert 0.0 <= MODULE._rouge_l_f1(text, "unrelated result") <= 1.0


def test_run_uses_train_only_and_writes_explicit_weak_label_report(tmp_path):
    artifact = {
        "artifact_type": "weak_label_research_gap_dataset",
        "evaluation_eligibility": {"status": "not_gold_benchmark_compatible"},
        "source": {"dataset_version": "2"},
        "records": [
            record("train-1", "train", "language model multilingual evaluation benchmark", "Robust multilingual evaluation is missing."),
            record("train-2", "train", "vision model image segmentation dataset", "Reliable segmentation under shift is missing."),
            record("val-1", "validation", "language model multilingual evaluation benchmark new task", "Robust multilingual evaluation is missing."),
        ],
    }
    source, output = tmp_path / "input.json", tmp_path / "report.json"
    source.write_text(json.dumps(artifact), encoding="utf-8")

    report = MODULE.run(source, output, "validation")

    assert report["counts"] == {"train": 2, "evaluation": 1}
    assert report["scientific_status"] == "exploratory_weak_label_only_not_gold_evaluation"
    assert report["predictions"][0]["nearest_train_paper_id"] == "train-1"
    assert json.loads(output.read_text(encoding="utf-8"))["overall"]["count"] == 1


def test_run_rejects_cross_split_exact_abstract_overlap(tmp_path):
    artifact = {
        "artifact_type": "weak_label_research_gap_dataset",
        "evaluation_eligibility": {"status": "not_gold_benchmark_compatible"},
        "records": [
            record("train-1", "train", "same abstract text", "gap one"),
            record("val-1", "validation", " same   abstract text ", "gap two"),
        ],
    }
    source = tmp_path / "input.json"
    source.write_text(json.dumps(artifact), encoding="utf-8")
    with pytest.raises(ValueError, match="abstract overlap"):
        MODULE.run(source, tmp_path / "report.json", "validation")


def test_run_rejects_non_weak_label_artifact(tmp_path):
    source = tmp_path / "input.json"
    source.write_text(json.dumps({"artifact_type": "gold_benchmark", "records": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="not the expected weak-label artifact"):
        MODULE.run(source, tmp_path / "report.json", "validation")
