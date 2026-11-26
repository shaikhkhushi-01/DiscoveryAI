#!/usr/bin/env python3
"""Evaluate ranked QASPER evidence retrieval using standard IR metrics."""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON at {path}, line {line_number}: {exc}"
                ) from exc
    return rows


def load_gold(path: Path) -> dict[str, dict[str, Any]]:
    gold = {}

    for row in load_jsonl(path):
        qid = str(row["query_id"])
        if qid in gold:
            raise ValueError(f"Duplicate gold query_id: {qid}")

        evidence = set()
        total_text_evidence = 0
        total_figure_evidence = 0

        for answer in row.get("answers") or []:
            for item in answer.get("evidence") or []:
                text = str(item).strip()

                if not text:
                    continue

                if text.startswith("FLOAT SELECTED"):
                    total_figure_evidence += 1
                else:
                    total_text_evidence += 1
                    evidence.add(text)

        gold[qid] = {
            "paper_id": str(row["paper_id"]),
            "evidence": evidence,
            "text_evidence_count": total_text_evidence,
            "figure_evidence_count": total_figure_evidence,
        }

    if not gold:
        raise ValueError("No gold references found.")

    return gold


def load_chunks(path: Path) -> dict[str, set[str]]:
    chunks = defaultdict(set)

    for row in load_jsonl(path):
        paper_id = str(row.get("paper_id", ""))
        text = row.get("text")

        if paper_id and isinstance(text, str) and text.strip():
            chunks[paper_id].add(text.strip())

    return chunks


def load_predictions(path: Path) -> dict[str, list[str]]:
    predictions = {}

    for row in load_jsonl(path):
        qid = str(row.get("question_id", "")).strip()
        evidence = row.get("predicted_evidence")

        if not qid or not isinstance(evidence, list):
            raise ValueError("Every prediction requires question_id and predicted_evidence list.")

        if qid in predictions:
            raise ValueError(f"Duplicate prediction question_id: {qid}")

        if any(not isinstance(item, str) for item in evidence):
            raise ValueError(f"Invalid evidence item for question {qid}")

        predictions[qid] = evidence

    return predictions


def calculate_metrics(
    ranked: list[str],
    relevant: set[str],
    k: int,
) -> dict[str, float]:
    retrieved = ranked[:k]

    if not relevant:
        return {
            "recall": 0.0,
            "precision": 0.0,
            "mrr": 0.0,
            "ndcg": 0.0,
        }

    hits = [1 if item in relevant else 0 for item in retrieved]

    recall = sum(hits) / len(relevant)
    precision = sum(hits) / k

    reciprocal_rank = 0.0
    for index, hit in enumerate(hits, 1):
        if hit:
            reciprocal_rank = 1.0 / index
            break

    dcg = sum(
        hit / math.log2(index + 1)
        for index, hit in enumerate(hits, 1)
    )

    ideal_hits = min(len(relevant), k)
    ideal_dcg = sum(
        1.0 / math.log2(index + 1)
        for index in range(1, ideal_hits + 1)
    )

    ndcg = dcg / ideal_dcg if ideal_dcg else 0.0

    return {
        "recall": recall,
        "precision": precision,
        "mrr": reciprocal_rank,
        "ndcg": ndcg,
    }


def evaluate(
    gold: dict[str, dict[str, Any]],
    predictions: dict[str, list[str]],
    chunks: dict[str, set[str]],
    k: int,
) -> dict[str, Any]:

    metric_values = defaultdict(list)

    total_gold = 0
    matched_gold = 0
    figure_evidence = 0
    unmatched_gold = 0
    missing_predictions = 0
    zero_evidence_predictions = 0
    questions_evaluated = 0
    questions_with_relevant_evidence = 0
    questions_with_retrievable_gold = 0
    retrieved_count = 0
    exact_prediction_matches = 0

    for qid, reference in gold.items():
        paper_id = reference["paper_id"]

        original_gold = reference["evidence"]
        available_chunks = chunks.get(paper_id, set())

        relevant = original_gold.intersection(available_chunks)

        total_gold += len(original_gold)
        matched_gold += len(relevant)
        unmatched_gold += len(original_gold - available_chunks)
        figure_evidence += reference["figure_evidence_count"]

        if qid not in predictions:
            missing_predictions += 1
            ranked = []
        else:
            ranked = predictions[qid]

        retrieved_count += len(ranked)

        exact_prediction_matches += sum(
            1 for item in ranked if item.strip() in available_chunks
        )

        if not ranked:
            zero_evidence_predictions += 1

        if not relevant:
            continue

        questions_with_relevant_evidence += 1

        if qid in predictions:
            questions_with_retrievable_gold += 1

        questions_evaluated += 1

        scores = calculate_metrics(ranked, relevant, k)

        for name, value in scores.items():
            metric_values[name].append(value)

    mean = lambda values: (
        sum(values) / len(values) if values else 0.0
    )

    extra_predictions = len(set(predictions) - set(gold))

    return {
        "dataset": "QASPER",
        "evaluation_type": "text_evidence_retrieval",
        "k": k,
        "questions_in_gold": len(gold),
        "predictions_received": len(predictions),
        "questions_evaluated": questions_evaluated,
        "questions_with_retrievable_gold": questions_with_retrievable_gold,
        "missing_predictions": missing_predictions,
        "extra_predictions_ignored": extra_predictions,
        "questions_with_zero_retrieved_evidence": zero_evidence_predictions,
        "retrieved_paragraphs": retrieved_count,
        "retrieved_paragraph_exact_chunk_matches": exact_prediction_matches,
        "retrieved_paragraph_chunk_match_rate": (
            exact_prediction_matches / retrieved_count
            if retrieved_count else 0.0
        ),
        "gold_text_evidence_total": total_gold,
        "gold_text_evidence_matched_to_chunks": matched_gold,
        "gold_text_evidence_unmatched": unmatched_gold,
        "gold_text_evidence_chunk_coverage": (
            matched_gold / total_gold if total_gold else 0.0
        ),
        "figure_table_evidence_excluded": figure_evidence,
        "metrics": {
            "recall_at_k": mean(metric_values["recall"]),
            "precision_at_k": mean(metric_values["precision"]),
            "mrr_at_k": mean(metric_values["mrr"]),
            "ndcg_at_k": mean(metric_values["ndcg"]),
        },
        "metric_notes": {
            "relevance": "Exact paragraph text match within the same paper.",
            "aggregation": "Macro average over questions with at least one gold text paragraph matching an available chunk.",
            "precision_denominator": "Fixed k, even when fewer than k paragraphs were retrieved.",
            "unmatched_gold": "Reported separately and excluded from the retrievable relevance set.",
            "figure_table": "FLOAT SELECTED evidence excluded from text retrieval metrics.",
            "limitations": "Exact matching does not measure semantic relevance. Metrics are conditional on gold evidence being represented in normalized text chunks.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--chunks", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--k", type=int, default=5)

    args = parser.parse_args()

    if args.k < 1:
        parser.error("--k must be at least 1")

    try:
        gold = load_gold(args.gold)
        chunks = load_chunks(args.chunks)
        predictions = load_predictions(args.predictions)

        report = evaluate(gold, predictions, chunks, args.k)

        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        print(json.dumps(report, indent=2, ensure_ascii=False))
        print(f"\nReport saved: {args.output}")

        return 0

    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())