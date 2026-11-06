from __future__ import annotations

import json
import math
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services.evaluation.discovery_gap_bench import (
    RATING_FIELDS,
    evaluable_records,
    load_benchmark,
)

REQUIRED_METADATA = (
    "run_id", "system_id", "system_version", "code_revision", "corpus_id",
    "benchmark_version", "model_provider", "model_name", "prompt_version",
    "embedding_model", "retrieval_config",
)
VALID_STANCES = {"supporting", "contradictory"}
VALID_STATUSES = {"supported", "contradicted", "inconclusive"}


def evidence_key(item: dict[str, Any]) -> tuple[str, str, str]:
    return (str(item["paper_id"]), str(item["document_id"]), str(item["chunk_id"]))


def _validate_predictions(payload: Any, expected_ids: set[str], benchmark_version: str, corpus_id: str, allowed_paper_ids: set[str]) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    if not isinstance(payload, dict):
        raise ValueError("prediction file root must be an object")
    metadata = payload.get("run_metadata")
    if not isinstance(metadata, dict):
        raise ValueError("run_metadata must be an object")
    for key in REQUIRED_METADATA:
        value = metadata.get(key)
        if not isinstance(value, str) or not value.strip() or value.strip().lower().startswith("replace-with"):
            raise ValueError(f"run_metadata.{key} is required and cannot be a placeholder")
    if metadata["benchmark_version"] != benchmark_version:
        raise ValueError("prediction benchmark_version does not match the gold benchmark")
    if metadata["corpus_id"] != corpus_id:
        raise ValueError("prediction corpus_id does not match the selected gold corpus snapshot")
    predictions = payload.get("predictions")
    if not isinstance(predictions, list):
        raise ValueError("predictions must be an array")

    by_id: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(predictions):
        path = f"predictions[{index}]"
        if not isinstance(item, dict):
            raise ValueError(f"{path} must be an object")
        record_id = item.get("record_id")
        if not isinstance(record_id, str) or not record_id:
            raise ValueError(f"{path}.record_id is required")
        if record_id not in expected_ids:
            raise ValueError(f"{path}.record_id {record_id!r} is not in the selected gold split")
        if record_id in by_id:
            raise ValueError(f"duplicate prediction for record_id {record_id!r}")
        if item.get("gap_status") not in VALID_STATUSES:
            raise ValueError(f"{path}.gap_status must be one of {sorted(VALID_STATUSES)}")
        ratings = item.get("ratings")
        if not isinstance(ratings, dict):
            raise ValueError(f"{path}.ratings must be an object")
        for field in RATING_FIELDS:
            value = ratings.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 3:
                raise ValueError(f"{path}.ratings.{field} must be an integer from 0 to 3")
        evidence = item.get("evidence")
        if not isinstance(evidence, list):
            raise ValueError(f"{path}.evidence must be an array")
        seen: set[tuple[str, str, str]] = set()
        for evidence_index, entry in enumerate(evidence):
            ep = f"{path}.evidence[{evidence_index}]"
            if not isinstance(entry, dict) or entry.get("stance") not in VALID_STANCES:
                raise ValueError(f"{ep} requires stance supporting or contradictory")
            if not all(isinstance(entry.get(k), str) and entry[k].strip() for k in ("paper_id", "document_id", "chunk_id")):
                raise ValueError(f"{ep} requires paper_id, document_id, and chunk_id")
            if entry["paper_id"] not in allowed_paper_ids:
                raise ValueError(f"{ep}.paper_id is outside the selected frozen corpus snapshot")
            key = evidence_key(entry)
            if key in seen:
                raise ValueError(f"{ep} duplicates evidence {key!r}")
            seen.add(key)
        by_id[record_id] = item

    missing = sorted(expected_ids - set(by_id))
    if missing:
        raise ValueError(f"missing predictions for selected gold records: {missing}")
    return metadata, by_id


def _f1(precision: float, recall: float) -> float:
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def _record_metrics(gold: dict[str, Any], prediction: dict[str, Any]) -> dict[str, float]:
    gold_evidence: dict[tuple[str, str, str], str] = {}
    for stance in VALID_STANCES:
        for entry in gold["gold_evidence"][stance]:
            gold_evidence[evidence_key(entry)] = stance
    predicted = {evidence_key(entry): entry["stance"] for entry in prediction["evidence"]}
    true_positive = set(gold_evidence) & set(predicted)
    precision = len(true_positive) / len(predicted) if predicted else 0.0
    recall = len(true_positive) / len(gold_evidence) if gold_evidence else 0.0
    stance_accuracy = (
        sum(gold_evidence[key] == predicted[key] for key in true_positive) / len(true_positive)
        if true_positive else 0.0
    )
    rating_errors = [
        abs(gold["gold_assessment"][field] - prediction["ratings"][field])
        for field in RATING_FIELDS
    ]
    return {
        "gap_status_accuracy": float(gold["gold_assessment"]["gap_status"] == prediction["gap_status"]),
        "evidence_precision": precision,
        "evidence_recall": recall,
        "evidence_f1": _f1(precision, recall),
        "evidence_stance_accuracy": stance_accuracy,
        "rating_mae": sum(rating_errors) / len(rating_errors),
    }


def _classification_metrics(gold_records: list[dict[str, Any]], predictions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    labels = sorted(VALID_STATUSES)
    confusion = {label: {pred: 0 for pred in labels} for label in labels}
    for record in gold_records:
        actual = record["gold_assessment"]["gap_status"]
        predicted = predictions[record["record_id"]]["gap_status"]
        confusion[actual][predicted] += 1
    per_class: dict[str, dict[str, float]] = {}
    f1s = []
    for label in labels:
        tp = confusion[label][label]
        fp = sum(confusion[other][label] for other in labels if other != label)
        fn = sum(confusion[label][other] for other in labels if other != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = _f1(precision, recall)
        per_class[label] = {"precision": precision, "recall": recall, "f1": f1}
        f1s.append(f1)
    total = len(gold_records)
    accuracy = sum(confusion[label][label] for label in labels) / total if total else 0.0
    return {
        "accuracy": accuracy,
        "macro_f1": sum(f1s) / len(f1s),
        "labels": labels,
        "confusion_matrix": confusion,
        "per_class": per_class,
    }


def _bootstrap_mean_ci(values: list[float], *, seed: int = 42, samples: int = 2000) -> dict[str, float] | None:
    if len(values) < 2:
        return None
    rng = random.Random(seed)
    means = sorted(
        sum(rng.choices(values, k=len(values))) / len(values)
        for _ in range(samples)
    )
    low = means[int(0.025 * (samples - 1))]
    high = means[int(0.975 * (samples - 1))]
    return {"lower_95": low, "upper_95": high, "method": "percentile bootstrap over records"}


def evaluate_benchmark(
    benchmark_path: str | Path,
    predictions_path: str | Path,
    *,
    split: str = "test",
) -> dict[str, Any]:
    """Run deterministic offline evaluation against adjudicated gold records only."""
    benchmark, validation = load_benchmark(benchmark_path, require_evaluable=True)
    all_evaluable = evaluable_records(benchmark, validation)
    selected = [record for record in all_evaluable if record["split"] == split]
    if not selected:
        raise ValueError(f"no adjudicated records in split {split!r}; refusing to compute metrics")
    corpus_ids = {record["corpus_snapshot"]["corpus_id"] for record in selected}
    if len(corpus_ids) != 1:
        raise ValueError("selected split spans multiple corpus snapshots; evaluate each snapshot separately")
    selected_paper_ids = {paper_id for record in selected for paper_id in record["corpus_snapshot"]["paper_ids"]}
    metadata, predictions = _validate_predictions(
        json.loads(Path(predictions_path).read_text(encoding="utf-8")),
        {record["record_id"] for record in selected},
        benchmark["benchmark_version"],
        next(iter(corpus_ids)),
        selected_paper_ids,
    )
    per_record = []
    metric_rows: dict[str, list[float]] = {}
    for record in selected:
        metrics = _record_metrics(record, predictions[record["record_id"]])
        per_record.append({"record_id": record["record_id"], "metrics": metrics})
        for key, value in metrics.items():
            metric_rows.setdefault(key, []).append(value)

    aggregate = {}
    for key, values in metric_rows.items():
        aggregate[key] = {
            "mean": sum(values) / len(values),
            "n": len(values),
            "ci_95": _bootstrap_mean_ci(values),
        }
    return {
        "report_schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_metadata": metadata,
        "benchmark": {
            "benchmark_id": benchmark["benchmark_id"],
            "benchmark_version": benchmark["benchmark_version"],
            "annotation_rubric_version": benchmark["annotation_rubric_version"],
            "corpus_ids": sorted({r["corpus_snapshot"]["corpus_id"] for r in selected}),
            "split": split,
            "adjudicated_record_count": len(all_evaluable),
            "evaluated_record_count": len(selected),
        },
        "metrics": {
            "gap_status": _classification_metrics(selected, predictions),
            "aggregate": aggregate,
        },
        "per_record": per_record,
        "limitations": [
            "Scores describe only this adjudicated benchmark split and corpus scope.",
            "Novelty ratings are corpus-bounded, not claims of global research novelty.",
            "Bootstrap intervals resample records and may be unstable for small pilot sets.",
            "No metrics are produced for pending or non-adjudicated records.",
        ],
    }


def write_report(report: dict[str, Any], output_path: str | Path) -> None:
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
