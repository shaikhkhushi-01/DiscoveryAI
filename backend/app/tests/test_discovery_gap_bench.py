import json
from pathlib import Path

import pytest

from app.services.evaluation.discovery_gap_bench import (
    evaluable_records,
    load_benchmark,
    validate_benchmark,
)


def valid_record(record_id="record-1", status="adjudicated"):
    return {
        "record_id": record_id,
        "research_question": "Does method A improve robust reasoning?",
        "corpus_snapshot": {
            "corpus_id": "corpus-v1",
            "snapshot_date": "2026-01-01",
            "paper_ids": ["paper-1", "paper-2"],
            "scope_statement": "Papers indexed in the project corpus through 2025.",
        },
        "candidate_gap": {
            "candidate_id": "gap-1",
            "title": "Robust reasoning under long contexts",
            "description": "Evaluate method A on held-out long-context tasks.",
            "gap_type": "evaluation",
        },
        "gold_evidence": {
            "supporting": [{
                "paper_id": "paper-1", "document_id": "doc-1", "chunk_id": "chunk-1",
                "relevance": 3, "rationale": "Directly supports the stated limitation.",
            }],
            "contradictory": [{
                "paper_id": "paper-2", "document_id": "doc-2", "chunk_id": "chunk-2",
                "relevance": 2, "rationale": "Reports a related evaluation that narrows the gap.",
            }],
        },
        "gold_assessment": {
            "gap_status": "inconclusive",
            "novelty_within_corpus": 2,
            "relevance": 3,
            "feasibility": 2,
            "evidence_quality": 3,
        },
        "annotations": {
            "annotator_ids": ["annotator-a", "annotator-b"],
            "annotated_at": "2026-01-03",
            "adjudication_status": status,
            "adjudication_notes": "Independent ratings reconciled against the rubric." if status == "adjudicated" else None,
        },
        "split": "test",
        "notes": "",
    }


def valid_benchmark(records=None):
    return {
        "schema_version": "1.0",
        "benchmark_id": "discovery-gap-bench",
        "benchmark_version": "0.1.0",
        "annotation_rubric_version": "rubric-1.0",
        "records": records if records is not None else [valid_record()],
    }


def test_valid_adjudicated_record_is_score_eligible():
    data = valid_benchmark()
    report = validate_benchmark(data)
    assert report.valid
    assert report.evaluable_count == 1
    assert evaluable_records(data, report) == data["records"]


def test_pending_annotation_is_valid_but_not_score_eligible():
    report = validate_benchmark(valid_benchmark([valid_record(status="pending")]))
    assert report.valid
    assert report.evaluable_count == 0
    assert report.pending_record_ids == ["record-1"]


def test_evidence_must_reference_a_paper_in_corpus():
    data = valid_benchmark()
    data["records"][0]["gold_evidence"]["supporting"][0]["paper_id"] = "not-in-corpus"
    report = validate_benchmark(data)
    assert not report.valid
    assert any("not in corpus_snapshot.paper_ids" in error for error in report.errors)


def test_duplicate_record_ids_are_rejected():
    report = validate_benchmark(valid_benchmark([valid_record(), valid_record()]))
    assert not report.valid
    assert any("duplicated" in error for error in report.errors)


def test_placeholder_template_is_not_valid_gold_data():
    repo_root = Path(__file__).resolve().parents[3]
    template = json.loads(
        (repo_root / "data/evaluation/discovery_gap_bench_template.json").read_text(encoding="utf-8")
    )
    report = validate_benchmark(template)
    assert not report.valid


def test_loader_refuses_empty_adjudicated_gold_set(tmp_path):
    path = tmp_path / "bench.json"
    path.write_text(json.dumps(valid_benchmark([valid_record(status="pending")])), encoding="utf-8")
    with pytest.raises(ValueError, match="no adjudicated records"):
        load_benchmark(path, require_evaluable=True)


def test_loader_fails_closed_on_invalid_json_shape(tmp_path):
    path = tmp_path / "bench.json"
    path.write_text('{"schema_version":"1.0","records":"not-an-array"}', encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid DiscoveryGapBench"):
        load_benchmark(path)
