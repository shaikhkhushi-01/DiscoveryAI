#!/usr/bin/env python3
"""Score QASPER JSONL predictions with the official Answer-F1/Evidence-F1 rules.

Input predictions: one JSON object per line with question_id,
predicted_answer (string), and predicted_evidence (list of exact paragraph strings).
Gold references are loaded only by this evaluator and must never be given to a model.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import re
import string
from pathlib import Path
from typing import Any


def normalize_answer(text: str) -> str:
    text = text.lower()
    text = "".join(char for char in text if char not in set(string.punctuation))
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    return " ".join(text.split())


def token_f1_score(prediction: str, reference: str) -> float:
    predicted_tokens = normalize_answer(prediction).split()
    reference_tokens = normalize_answer(reference).split()
    common = Counter(predicted_tokens) & Counter(reference_tokens)
    overlap = sum(common.values())
    if overlap == 0:
        return 1.0 if not predicted_tokens and not reference_tokens else 0.0
    precision = overlap / len(predicted_tokens)
    recall = overlap / len(reference_tokens)
    return 2 * precision * recall / (precision + recall)


def paragraph_f1_score(prediction: list[str], reference: list[str]) -> float:
    if not reference and not prediction:
        return 1.0
    overlap = len(set(reference).intersection(set(prediction)))
    if overlap == 0:
        return 0.0
    precision = overlap / len(prediction)
    recall = overlap / len(reference)
    return 2 * precision * recall / (precision + recall)


def answer_text_and_type(answer: dict[str, Any]) -> tuple[str, str]:
    if answer.get("unanswerable", False):
        return "Unanswerable", "none"
    spans = answer.get("extractive_spans") or []
    if spans:
        return ", ".join(str(item) for item in spans), "extractive"
    free_form = answer.get("free_form_answer") or ""
    if free_form:
        return str(free_form), "abstractive"
    yes_no = answer.get("yes_no")
    if yes_no is not None:
        return ("Yes" if yes_no else "No"), "boolean"
    raise ValueError(f"Gold annotation has no recognized answer: {answer.get('annotation_id')}")


def load_gold(path: Path, *, text_evidence_only: bool = False) -> dict[str, list[dict[str, Any]]]:
    gold: dict[str, list[dict[str, Any]]] = {}
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            qid = str(row["query_id"])
            if qid in gold:
                raise ValueError(f"Duplicate gold query_id at line {line_number}: {qid}")
            references = []
            for answer in row.get("answers") or []:
                answer_text, answer_type = answer_text_and_type(answer)
                evidence = [str(item) for item in (answer.get("evidence") or [])]
                if text_evidence_only:
                    evidence = [item for item in evidence if "FLOAT SELECTED" not in item]
                references.append({"answer": answer_text, "type": answer_type, "evidence": evidence})
            if references:
                gold[qid] = references
    if not gold:
        raise ValueError(f"No gold references with annotations found in {path}")
    return gold


def load_predictions(path: Path) -> dict[str, dict[str, Any]]:
    predictions: dict[str, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            qid = str(row.get("question_id") or "").strip()
            answer = row.get("predicted_answer")
            evidence = row.get("predicted_evidence")
            if not qid or not isinstance(answer, str) or not isinstance(evidence, list):
                raise ValueError(
                    f"Prediction line {line_number} requires question_id, string predicted_answer, "
                    "and list predicted_evidence"
                )
            if any(not isinstance(item, str) for item in evidence):
                raise ValueError(f"Prediction line {line_number}: every evidence item must be a string")
                    if qid in predictions:
                raise ValueError(f"Duplicate prediction question_id at line {line_number}: {qid}")
            predictions[qid] = {"answer": answer, "evidence": evidence}
    return predictions


def evaluate(gold: dict[str, list[dict[str, Any]]],
             predicted: dict[str, dict[str, Any]]) -> dict[str, Any]:
    answer_scores: list[float] = []
    evidence_scores: list[float] = []
    answer_by_type: dict[str, list[float]] = {
        "extractive": [], "abstractive": [], "boolean": [], "none": []
    }
    missing = 0
    for qid, references in gold.items():
        if qid not in predicted:
            missing += 1
            answer_scores.append(0.0)
            evidence_scores.append(0.0)
            continue
        prediction = predicted[qid]
        answer_options = [
            (token_f1_score(prediction["answer"], reference["answer"]), reference["type"])
            for reference in references
        ]
        best_answer_score, best_answer_type = max(answer_options, key=lambda item: item[0])
        answer_scores.append(best_answer_score)
        answer_by_type[best_answer_type].append(best_answer_score)
        evidence_options = [
            paragraph_f1_score(prediction["evidence"], reference["evidence"])
            for reference in references
        ]
        evidence_scores.append(max(evidence_options))

    mean = lambda values: sum(values) / len(values) if values else 0.0
    extra_predictions = sorted(set(predicted) - set(gold))
    return {
        "metric_implementation": "Adapted from allenai/qasper-led-baseline scripts/evaluator.py (pinned source revision afd0fb96bf78ce8cd8157639c6f6a6995e4f9089)",
        "questions_scored": len(gold),
        "predictions_received": len(predicted),
        "missing_predictions": missing,
        "extra_predictions_ignored": len(extra_predictions),
        "answer_f1": mean(answer_scores),
        "answer_f1_by_type": {key: mean(value) for key, value in answer_by_type.items()},
        "evidence_f1": mean(evidence_scores),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold", type=Path, required=True,
                        help="normalized/references/<split>.jsonl from prepare_qasper.py")
    parser.add_argument("--predictions", type=Path, required=True,
                        help="JSONL: question_id, predicted_answer, predicted_evidence")
    parser.add_argument("--output", type=Path, default=None, help="Optional JSON report path")
    parser.add_argument("--text-evidence-only", "--text_evidence_only", action="store_true",
                        help="Exclude FLOAT SELECTED figure/table evidence, matching official option")
    args = parser.parse_args()
    try:
        gold = load_gold(args.gold, text_evidence_only=args.text_evidence_only)
        predicted = load_predictions(args.predictions)
        report = evaluate(gold, predicted)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
