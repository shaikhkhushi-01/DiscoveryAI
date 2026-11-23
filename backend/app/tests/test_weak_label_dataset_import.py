from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "evaluation" / "import_weak_label_research_gap_dataset.py"
SPEC = importlib.util.spec_from_file_location("weak_label_importer", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

HEADERS = [
    "Serial", "Paper ID", "Version", "Title", "Published", "Primary Category",
    "Categories", "Abstract", "Limitation", "Research Gap", "Importance",
    "Gap Refers To Own Work", "Generator Model", "Split",
]


def write_csv(path: Path, rows: list[list[str]]) -> None:
    import csv
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(HEADERS)
        writer.writerows(rows)


def row(paper_id="2601.00001", split="train"):
    return [
        "1", paper_id, "v1", "A research paper", "2026-03-16",
        "cs.CL", "cs.CL; cs.AI", "An abstract about language models.",
        "The evaluation is limited.", "Robust multilingual evaluation is missing.",
        "This matters for reliable deployment.", "false", "mistral-small-latest", split,
    ]


def test_importer_preserves_weak_label_provenance_and_never_marks_gold(tmp_path):
    source = tmp_path / "gaps.csv"
    write_csv(source, [row(), row("2601.00002", "test")])

    artifact = MODULE.import_weak_label_csv(source)

    assert artifact["artifact_type"] == "weak_label_research_gap_dataset"
    assert artifact["source"]["row_count"] == 2
    assert artifact["source"]["split_counts"] == {"test": 1, "train": 1}
    assert artifact["evaluation_eligibility"]["status"] == "not_gold_benchmark_compatible"
    assert artifact["evaluation_eligibility"]["allowed_use"] == [
        "descriptive_text_analysis", "weak_label_exploration"
    ]
    record = artifact["records"][0]
    assert record["research_gap_llm_inferred"].startswith("Robust multilingual")
    assert record["label_provenance"]["human_expert_validated"] is False
    assert record["label_provenance"]["adjudicated"] is False
    assert "gold_assessment" not in record
    assert len(artifact["source"]["sha256"]) == 64


def test_importer_rejects_duplicate_paper_ids(tmp_path):
    source = tmp_path / "duplicates.csv"
    write_csv(source, [row(), row()])
    with pytest.raises(ValueError, match="duplicate Paper ID"):
        MODULE.import_weak_label_csv(source)


def test_importer_rejects_unknown_split(tmp_path):
    source = tmp_path / "bad-split.csv"
    write_csv(source, [row(split="holdout")])
    with pytest.raises(ValueError, match="unsupported Split"):
        MODULE.import_weak_label_csv(source)


def test_importer_rejects_missing_required_column(tmp_path):
    source = tmp_path / "missing.csv"
    write_csv(source, [row()])
    text = source.read_text(encoding="utf-8").replace(",Importance,", ",", 1)
    source.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="CSV missing required columns"):
        MODULE.import_weak_label_csv(source)
