from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services.evaluation.runner import _bootstrap_mean_ci, evaluate_benchmark

BASELINE_SYSTEMS = (
    "llm_only",
    "vector_rag",
    "graph_rag",
    "hybrid_retrieval",
    "discoveryai_full",
)
HIGHER_IS_BETTER = (
    "gap_status_accuracy",
    "evidence_precision",
    "evidence_recall",
    "evidence_f1",
    "evidence_stance_accuracy",
)
LOWER_IS_BETTER = ("rating_mae",)


def _read_prediction(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("predictions"), list):
        raise ValueError(f"{path}: prediction file must contain a predictions array")
    return payload


def compare_baselines(
    benchmark_path: str | Path,
    prediction_files: dict[str, str | Path],
    *,
    split: str = "test",
    evidence_budget: int = 8,
) -> dict[str, Any]:
    """Compare all five systems on one gold split with a shared evidence budget."""
    if set(prediction_files) != set(BASELINE_SYSTEMS):
        missing = sorted(set(BASELINE_SYSTEMS) - set(prediction_files))
        extra = sorted(set(prediction_files) - set(BASELINE_SYSTEMS))
        raise ValueError(f"provide exactly the five baseline systems; missing={missing}, extra={extra}")
    if not isinstance(evidence_budget, int) or isinstance(evidence_budget, bool) or evidence_budget < 1:
        raise ValueError("evidence_budget must be a positive integer")

    reports: dict[str, dict[str, Any]] = {}
    record_metrics: dict[str, dict[str, dict[str, float]]] = {}
    reference_signature: tuple[Any, ...] | None = None
    for system in BASELINE_SYSTEMS:
        payload = _read_prediction(prediction_files[system])
        metadata = payload.get("run_metadata") or {}
        if metadata.get("system_id") != system:
            raise ValueError(f"{system}: run_metadata.system_id must equal {system!r}")
        for prediction in payload["predictions"]:
            evidence = prediction.get("evidence")
            if not isinstance(evidence, list):
                raise ValueError(f"{system}: every prediction must contain an evidence array")
            if len(evidence) > evidence_budget:
                raise ValueError(
                    f"{system}: record {prediction.get('record_id')!r} uses {len(evidence)} evidence items; "
                    f"shared evidence budget is {evidence_budget}"
                )

        report = evaluate_benchmark(benchmark_path, prediction_files[system], split=split)
        benchmark = report["benchmark"]
        signature = (
            benchmark["benchmark_id"],
            benchmark["benchmark_version"],
            benchmark["annotation_rubric_version"],
            tuple(benchmark["corpus_ids"]),
            benchmark["split"],
            tuple(sorted(row["record_id"] for row in report["per_record"])),
            benchmark["evaluated_record_count"],
        )
        if reference_signature is None:
            reference_signature = signature
        elif signature != reference_signature:
            raise ValueError("baseline runs do not share the same benchmark, corpus snapshot, split, and record IDs")
        reports[system] = report
        record_metrics[system] = {
            row["record_id"]: row["metrics"] for row in report["per_record"]
        }

    summaries: dict[str, Any] = {}
    for system, report in reports.items():
        aggregate = report["metrics"]["aggregate"]
        summaries[system] = {
            "run_metadata": report["run_metadata"],
            "gap_status_accuracy": report["metrics"]["gap_status"]["accuracy"],
            "gap_status_macro_f1": report["metrics"]["gap_status"]["macro_f1"],
            **{name: aggregate[name]["mean"] for name in aggregate},
        }

    full = record_metrics["discoveryai_full"]
    paired: dict[str, Any] = {}
    for system in BASELINE_SYSTEMS:
        if system == "discoveryai_full":
            continue
        paired[system] = {}
        for metric in (*HIGHER_IS_BETTER, *LOWER_IS_BETTER):
            deltas = []
            wins = 0
            for record_id, full_metrics in full.items():
                difference = full_metrics[metric] - record_metrics[system][record_id][metric]
                if metric in LOWER_IS_BETTER:
                    difference *= -1
                deltas.append(difference)
                if difference > 0:
                    wins += 1
            paired[system][metric] = {
                "mean_full_system_advantage": sum(deltas) / len(deltas),
                "full_system_win_rate": wins / len(deltas),
                "paired_delta_ci_95": _bootstrap_mean_ci(deltas),
                "n": len(deltas),
            }

    return {
        "comparison_schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": {
            "benchmark_id": reference_signature[0],
            "benchmark_version": reference_signature[1],
            "annotation_rubric_version": reference_signature[2],
            "corpus_ids": list(reference_signature[3]),
            "split": split,
            "record_count": reference_signature[6],
            "shared_max_evidence_items_per_record": evidence_budget,
            "systems": list(BASELINE_SYSTEMS),
        },
        "systems": summaries,
        "paired_full_system_comparisons": paired,
        "per_system_reports": reports,
        "limitations": [
            "Comparison is valid only for this adjudicated split and frozen corpus snapshot.",
            "The evidence budget caps returned evidence items; it does not equalize token cost or model compute.",
            "Baseline quality depends on externally generated predictions and recorded configurations.",
            "LLM-only may return no evidence; evidence metrics therefore reflect its lack of traceable citations.",
            "Paired bootstrap intervals are descriptive and are not a substitute for a pre-registered significance test.",
            "No system is declared superior without a sufficiently sized expert-annotated benchmark.",
        ],
    }


def write_comparison(report: dict[str, Any], output_path: str | Path) -> None:
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
