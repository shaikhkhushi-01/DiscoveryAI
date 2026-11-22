from __future__ import annotations

import unittest

from scripts.benchmarks.evaluate_qasper import (
    answer_text_and_type,
    evaluate,
    paragraph_f1_score,
    token_f1_score,
)


class QasperOfficialMetricParityTests(unittest.TestCase):
    def test_token_f1_matches_official_squad_behavior(self):
        self.assertEqual(token_f1_score("The cat, sat!", "cat sat"), 1.0)
        self.assertEqual(token_f1_score("cat", "dog"), 0.0)
        # Official QASPER evaluator returns zero when token overlap is zero,
        # including the empty/empty edge case.
        self.assertEqual(token_f1_score("", ""), 0.0)

    def test_paragraph_f1_unanswerable_empty_evidence(self):
        self.assertEqual(paragraph_f1_score([], []), 1.0)
        self.assertEqual(paragraph_f1_score(["p1"], []), 0.0)

    def test_answer_type_priority_and_false_boolean(self):
        self.assertEqual(answer_text_and_type({
            "unanswerable": False,
            "extractive_spans": ["span"],
            "free_form_answer": "free form",
            "yes_no": True,
        }), ("span", "extractive"))
        self.assertEqual(answer_text_and_type({
            "unanswerable": False,
            "extractive_spans": [],
            "free_form_answer": "",
            "yes_no": False,
        }), ("No", "boolean"))

    def test_max_over_multiple_human_references_and_missing_prediction(self):
        gold = {
            "q1": [
                {"answer": "wrong", "type": "abstractive", "evidence": ["other"]},
                {"answer": "the cat", "type": "extractive", "evidence": ["p1"]},
            ],
            "q2": [{"answer": "Unanswerable", "type": "none", "evidence": []}],
        }
        predictions = {"q1": {"answer": "cat", "evidence": ["p1"]}}
        report = evaluate(gold, predictions)
        self.assertEqual(report["answer_f1"], 0.5)
        self.assertEqual(report["evidence_f1"], 0.5)
        self.assertEqual(report["missing_predictions"], 1)


if __name__ == "__main__":
    unittest.main()
