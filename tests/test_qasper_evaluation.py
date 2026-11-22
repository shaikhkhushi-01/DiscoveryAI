from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.benchmarks.evaluate_qasper import (
    answer_text_and_type,
    evaluate,
    load_gold,
    load_predictions,
    paragraph_f1_score,
    token_f1_score,
)


class QasperEvaluatorTests(unittest.TestCase):
    def test_squad_normalization_and_token_f1(self):
        self.assertEqual(token_f1_score("The cat, sat!", "cat sat"), 1.0)
        self.assertEqual(token_f1_score("", ""), 1.0)
        self.assertEqual(token_f1_score("cat", "dog"), 0.0)

    def test_paragraph_f1_set_semantics(self):
        self.assertEqual(paragraph_f1_score(["p1", "p2"], ["p2", "p1"]), 1.0)
        self.assertEqual(paragraph_f1_score([], []), 1.0)
        self.assertEqual(paragraph_f1_score(["p1"], []), 0.0)

    def test_answer_type_precedence_matches_official(self):
        self.assertEqual(
            answer_text_and_type({
                "unanswerable": False,
                "extractive_spans": ["span"],
                "free_form_answer": "free",
                "yes_no": True,
            }),
            ("span", "extractive"),
        )
        self.assertEqual(
            answer_text_and_type({
                "unanswerable": False,
                "extractive_spans": [],
                "free_form_answer": "",
                "yes_no": False,
            }),
            ("No", "boolean"),
        )

    def test_missing_prediction_is_zero_and_extras_are_ignored(self):
        gold = {
            "q1": [{"answer": "cat", "type": "extractive", "evidence": ["p1"]}],
            "q2": [{"answer": "Unanswerable", "type": "none", "evidence": []}],
        }
        predicted = {
            "q1": {"answer": "cat", "evidence": ["p1"]},
            "extra": {"answer": "irrelevant", "evidence": []},
        }
        result = evaluate(gold, predicted)
        self.assertEqual(result["answer_f1"], 0.5)
        self.assertEqual(result["evidence_f1"], 0.5)
        self.assertEqual(result["missing_predictions"], 1)
        self.assertEqual(result["extra_predictions_ignored"], 1)

    def test_gold_and_prediction_jsonl_loading(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gold_path = root / "gold.jsonl"
            pred_path = root / "pred.jsonl"
            gold_path.write_text(json.dumps({
                "query_id": "q1",
                "answers": [{
                    "unanswerable": False,
                    "extractive_spans": ["a result"],
                    "free_form_answer": "",
                    "yes_no": None,
                    "evidence": ["paragraph"],
                }],
            }) + "\n", encoding="utf-8")
            pred_path.write_text(json.dumps({
                "question_id": "q1",
                "predicted_answer": "a result",
                "predicted_evidence": ["paragraph"],
            }) + "\n", encoding="utf-8")
            gold = load_gold(gold_path)
            predicted = load_predictions(pred_path)
            result = evaluate(gold, predicted)
            self.assertEqual(result["answer_f1"], 1.0)
            self.assertEqual(result["evidence_f1"], 1.0)

    def test_duplicate_prediction_ids_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pred.jsonl"
            row = {"question_id": "q1", "predicted_answer": "x", "predicted_evidence": []}
            path.write_text(json.dumps(row) + "\n" + json.dumps(row) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate prediction"):
                load_predictions(path)


if __name__ == "__main__":
    unittest.main()
