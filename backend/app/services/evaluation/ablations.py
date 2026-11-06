from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services.evaluation.runner import _bootstrap_mean_ci, evaluate_benchmark

ABLATION_VARIANTS = (
    "full", "without_vector_retrieval", "without_graph_retrieval",
    "without_research_critic", "without_temporal_signals", "without_discovery_score",
)
METRICS = (
    "gap_status_accuracy", "evidence_precision", "evidence_recall",
    "evidence_f1", "evidence_stance_accuracy", "rating_mae",
)


def compare_ablations(benchmark_path: str | Path, prediction_files: dict[str, str | Path], *, split: str = "test") -> dict[str, Any]:
    """Compare full DiscoveryAI with predeclared component-removal variants."""
    if set(prediction_files) != set(ABLATION_VARIANTS):
        missing = sorted(set(ABLATION_VARIANTS) - set(prediction_files))
        extra = sorted(set(prediction_files) - set(ABLATION_VARIANTS))
        raise ValueError(f"provide exactly the full run and five ablations; missing={missing}, extra={extra}")

    reports: dict[str, dict[str, Any]] = {}
    signature: tuple[Any, ...] | None = None
    records: dict[str, dict[str, dict[str, float]]] = {}
    for variant in ABLATION_VARIANTS:
        report = evaluate_benchmark(benchmark_path, prediction_files[variant], split=split)
        metadata = report["run_metadata"]
        if metadata.get("ablation_id") != variant:
            raise ValueError(f"{variant}: run_metadata.ablation_id must equal {variant!r}")
        disabled = metadata.get("disabled_components")
        if not isinstance(disabled, list) or any(not isinstance(x, str) or not x.strip() for x in disabled):
            raise ValueError(f"{variant}: run_metadata.disabled_components must be an array of component names")
        expected = [] if variant == "full" else [variant.removeprefix("without_")]
        if sorted(disabled) != sorted(expected):
            raise ValueError(f"{variant}: disabled_components must be {expected!r}")

        bench = report["benchmark"]
        current = (bench["benchmark_id"], bench["benchmark_version"], bench["annotation_rubric_version"],
                   tuple(bench["corpus_ids"]), bench["split"],
                   tuple(sorted(row["record_id"] for row in report["per_record"])))
        if signature is None:
            signature = current
        elif current != signature:
            raise ValueError("ablation runs must use identical benchmark, corpus snapshot, split, and record IDs")
        reports[variant] = report
        records[variant] = {row["record_id"]: row["metrics"] for row in report["per_record"]}

    full = records["full"]
    effects: dict[str, Any] = {}
    for variant in ABLATION_VARIANTS:
        if variant == "full":
            continue
        effects[variant] = {}
        for metric in METRICS:
            deltas = []
            for record_id, values in full.items():
                delta = values[metric] - records[variant][record_id][metric]
                if metric == "rating_mae":
                    delta *= -1
                deltas.append(delta)
            effects[variant][metric] = {
                "mean_full_minus_ablation_advantage": sum(deltas) / len(deltas),
                "paired_delta_ci_95": _bootstrap_mean_ci(deltas),
                "n": len(deltas),
                "interpretation": "positive favors full system; negative favors ablation",
            }

    return {
        "ablation_schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": {
            "benchmark_id": signature[0], "benchmark_version": signature[1],
            "annotation_rubric_version": signature[2], "corpus_ids": list(signature[3]),
            "split": split, "record_count": len(signature[5]),
            "variants": list(ABLATION_VARIANTS),
            "design": "paired, same-record component-removal comparison",
        },
        "variants": {key: {"run_metadata": value["run_metadata"], "metrics": value["metrics"]}
                     for key, value in reports.items()},
        "paired_component_effects": effects,
        "per_variant_reports": reports,
        "limitations": [
            "Effects are conditional on the exact corpus, prompts, model, and component configuration.",
            "Removing a component can change downstream inputs; effects are not additive or proof of causal independence.",
            "Bootstrap intervals are descriptive and do not establish statistical significance.",
            "No component benefit is claimed without adjudicated expert-labelled records and independently executed variants.",
        ],
    }


def write_ablation_report(report: dict[str, Any], output_path: str | Path) -> None:
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
