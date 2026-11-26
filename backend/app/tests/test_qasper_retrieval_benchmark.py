import importlib.util
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[3]
EVALUATOR_PATH = PROJECT_ROOT / "scripts" / "benchmarks" / "evaluate_retrieval.py"

spec = importlib.util.spec_from_file_location(
    "evaluate_retrieval",
    EVALUATOR_PATH,
)
evaluator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluator)


def test_calculate_metrics_perfect_retrieval():
    scores = evaluator.calculate_metrics(
        ["a", "b", "c"],
        {"a", "b"},
        2,
    )

    assert scores["recall"] == 1.0
    assert scores["precision"] == 1.0
    assert scores["mrr"] == 1.0
    assert scores["ndcg"] == 1.0


def test_calculate_metrics_partial_retrieval():
    scores = evaluator.calculate_metrics(
        ["x", "a", "b"],
        {"a", "b"},
        2,
    )

    assert scores["recall"] == 0.5
    assert scores["precision"] == 0.5
    assert scores["mrr"] == 0.5
    assert 0.0 < scores["ndcg"] < 1.0


def test_calculate_metrics_no_relevant_results():
    scores = evaluator.calculate_metrics(
        ["x", "y"],
        {"a"},
        2,
    )

    assert scores == {
        "recall": 0.0,
        "precision": 0.0,
        "mrr": 0.0,
        "ndcg": 0.0,
    }


def test_calculate_metrics_empty_relevant_set():
    scores = evaluator.calculate_metrics(
        ["a", "b"],
        set(),
        2,
    )

    assert all(value == 0.0 for value in scores.values())


def test_calculate_metrics_precision_uses_fixed_k():
    scores = evaluator.calculate_metrics(
        ["a"],
        {"a", "b"},
        5,
    )

    assert scores["precision"] == 0.2
    assert scores["recall"] == 0.5


def test_evaluate_counts_missing_predictions_as_zero():
    gold = {
        "q1": {
            "paper_id": "p1",
            "evidence": {"gold paragraph"},
            "figure_evidence_count": 0,
        }
    }

    chunks = {"p1": {"gold paragraph"}}

    report = evaluator.evaluate(gold, {}, chunks, 5)

    assert report["missing_predictions"] == 1
    assert report["questions_evaluated"] == 1
    assert report["questions_with_retrievable_gold"] == 0
    assert report["metrics"]["recall_at_k"] == 0.0


def test_evaluate_reports_gold_chunk_coverage():
    gold = {
        "q1": {
            "paper_id": "p1",
            "evidence": {"available", "unavailable"},
            "figure_evidence_count": 2,
        }
    }

    predictions = {"q1": ["available", "unknown"]}
    chunks = {"p1": {"available"}}

    report = evaluator.evaluate(gold, predictions, chunks, 2)

    assert report["gold_text_evidence_total"] == 2
    assert report["gold_text_evidence_matched_to_chunks"] == 1
    assert report["gold_text_evidence_unmatched"] == 1
    assert report["gold_text_evidence_chunk_coverage"] == 0.5
    assert report["figure_table_evidence_excluded"] == 2


def test_evaluate_reports_exact_prediction_chunk_matches():
    gold = {
        "q1": {
            "paper_id": "p1",
            "evidence": {"gold paragraph"},
            "figure_evidence_count": 0,
        }
    }

    predictions = {
        "q1": ["gold paragraph", "not in chunks"]
    }

    chunks = {"p1": {"gold paragraph"}}

    report = evaluator.evaluate(gold, predictions, chunks, 2)

    assert report["retrieved_paragraphs"] == 2
    assert report["retrieved_paragraph_exact_chunk_matches"] == 1
    assert report["retrieved_paragraph_chunk_match_rate"] == 0.5


def test_load_predictions_rejects_duplicate_question_ids(tmp_path):
    path = tmp_path / "predictions.jsonl"
    path.write_text(
        '{"question_id":"q1","predicted_evidence":[]}\n'
        '{"question_id":"q1","predicted_evidence":[]}\n',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate prediction"):
        evaluator.load_predictions(path)


def test_load_gold_rejects_duplicate_query_ids(tmp_path):
    path = tmp_path / "gold.jsonl"
    row = (
        '{"query_id":"q1","paper_id":"p1","answers":[]}\n'
        '{"query_id":"q1","paper_id":"p1","answers":[]}\n'
    )
    path.write_text(row, encoding="utf-8")

    with pytest.raises(ValueError, match="Duplicate gold"):
        evaluator.load_gold(path)