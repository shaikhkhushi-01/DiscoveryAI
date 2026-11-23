#!/usr/bin/env python3
"""Run the complete Phase 4 live pipeline: preflight, 5 systems, 6 ablations, reports.

This command never manufactures labels. The benchmark adapters fail closed unless
the selected split contains records marked adjudicated. Keep all inputs/outputs
private when corpus or benchmark terms require it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable
BASELINES = (
    "llm_only", "vector_rag", "graph_rag", "hybrid_retrieval", "discoveryai_full",
)
ABLATIONS = (
    "full", "without_vector_retrieval", "without_graph_retrieval",
    "without_research_critic", "without_temporal_signals", "without_discovery_score",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: list[str], *, cwd: Path = ROOT) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if completed.returncode:
        # Preserve useful diagnostics while never printing environment variables.
        raise RuntimeError(
            f"Command failed ({completed.returncode}): {' '.join(command)}\n"
            f"stdout:\n{completed.stdout[-6000:]}\nstderr:\n{completed.stderr[-6000:]}"
        )
    return {"command": command, "stdout": completed.stdout.strip()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--split", choices=("train", "validation", "test"), default="test")
    parser.add_argument("--evidence-budget", type=int, default=8)
    parser.add_argument("--code-revision", default=os.getenv("GITHUB_SHA"))
    parser.add_argument("--model-provider", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--prompt-version", default="phase4-e2e-v1")
    parser.add_argument("--embedding-model", default="configured-embedding-provider")
    parser.add_argument("--retrieval-config", default="top_k=8;reranker=repository-default")
    args = parser.parse_args()

    benchmark = args.benchmark.resolve()
    output = args.output_dir.resolve()
    if not benchmark.is_file():
        parser.error(f"benchmark file does not exist: {benchmark}")
    if not args.code_revision:
        parser.error("--code-revision (or GITHUB_SHA) is required")
    if not 1 <= args.evidence_budget <= 8:
        parser.error("--evidence-budget must be from 1 to 8")
    if output == benchmark.parent or benchmark.is_relative_to(output):
        parser.error("output directory must not contain or overwrite the benchmark")
    output.mkdir(parents=True, exist_ok=True)

    summary: dict[str, Any] = {
        "schema_version": "1.0",
        "run_started_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "running",
        "benchmark": {"file_name": benchmark.name, "sha256": sha256(benchmark)},
        "protocol": {
            "split": args.split, "evidence_budget": args.evidence_budget,
            "code_revision": args.code_revision, "model_provider": args.model_provider,
            "model_name": args.model_name, "prompt_version": args.prompt_version,
            "embedding_model": args.embedding_model, "retrieval_config": args.retrieval_config,
            "baseline_systems": list(BASELINES), "ablation_variants": list(ABLATIONS),
        },
        "steps": {},
        "scientific_boundary": [
            "Model outputs are predictions, not gold labels.",
            "This run requires an input benchmark whose selected records are already adjudicated.",
            "Passing preflight does not prove the indexes match the benchmark corpus snapshot.",
            "Ablation deltas are conditional descriptive comparisons, not proof of causal independence.",
        ],
    }
    try:
        readiness_path = output / "readiness.json"
        readiness = run([PYTHON, str(ROOT / "scripts/evaluation/check_phase4_readiness.py"), "--allow-blocked"])
        readiness_payload = json.loads(readiness["stdout"])
        readiness_path.write_text(json.dumps(readiness_payload, indent=2) + "\n", encoding="utf-8")
        summary["steps"]["readiness"] = {
            "ready": readiness_payload.get("ready", False),
            "blocked_checks": readiness_payload.get("blocked_checks", []),
            "report": readiness_path.name, "sha256": sha256(readiness_path),
        }
        if not readiness_payload.get("ready"):
            raise RuntimeError(
                "Live dependency preflight is blocked: "
                + ", ".join(readiness_payload.get("blocked_checks", []))
                + ". Fix the backend environment and rerun; no model predictions were generated."
            )

        common = [
            "--benchmark", str(benchmark), "--output-dir", str(output / "baseline_predictions"),
            "--split", args.split, "--evidence-budget", str(args.evidence_budget),
            "--code-revision", args.code_revision, "--model-provider", args.model_provider,
            "--model-name", args.model_name, "--prompt-version", args.prompt_version,
            "--embedding-model", args.embedding_model, "--retrieval-config", args.retrieval_config,
        ]
        baseline_run = run([PYTHON, str(ROOT / "scripts/evaluation/generate_discovery_gap_baselines.py"), *common])
        baseline_result = json.loads(baseline_run["stdout"])
        if not baseline_result.get("ok") or set(baseline_result.get("systems", [])) != set(BASELINES):
            raise RuntimeError("Five-system generator did not return the complete expected system set.")
        baseline_files = {name: Path(path).resolve() for name, path in baseline_result["outputs"].items()}
        if set(baseline_files) != set(BASELINES) or not all(path.is_file() for path in baseline_files.values()):
            raise RuntimeError("One or more five-system prediction artifacts are missing.")
        baseline_report = output / "baseline_comparison.json"
        compare_args = [
            "--benchmark", str(benchmark), "--split", args.split,
            "--evidence-budget", str(args.evidence_budget), "--output", str(baseline_report),
        ]
        for name in BASELINES:
            compare_args.extend([f"--{name.replace('_', '-')}", str(baseline_files[name])])
        run([PYTHON, str(ROOT / "scripts/evaluation/compare_discovery_gap_baselines.py"), *compare_args])
        summary["steps"]["five_systems"] = {
            "systems": list(BASELINES), "prediction_files": {
                name: {"file_name": path.name, "sha256": sha256(path)} for name, path in baseline_files.items()
            },
            "comparison": {"file_name": baseline_report.name, "sha256": sha256(baseline_report)},
        }

        ablation_common = [
            "--benchmark", str(benchmark), "--output-dir", str(output / "ablation_predictions"),
            "--split", args.split, "--evidence-budget", str(args.evidence_budget),
            "--code-revision", args.code_revision, "--model-provider", args.model_provider,
            "--model-name", args.model_name, "--prompt-version", args.prompt_version,
            "--embedding-model", args.embedding_model, "--retrieval-config", args.retrieval_config,
        ]
        ablation_run = run([PYTHON, str(ROOT / "scripts/evaluation/generate_discovery_gap_ablations.py"), *ablation_common])
        ablation_result = json.loads(ablation_run["stdout"])
        if not ablation_result.get("ok") or set(ablation_result.get("variants", [])) != set(ABLATIONS):
            raise RuntimeError("Ablation generator did not return all six expected variants.")
        ablation_files = {name: Path(path).resolve() for name, path in ablation_result["outputs"].items()}
        if set(ablation_files) != set(ABLATIONS) or not all(path.is_file() for path in ablation_files.values()):
            raise RuntimeError("One or more six-ablation prediction artifacts are missing.")
        ablation_report = output / "ablation_comparison.json"
        ablation_args = ["--benchmark", str(benchmark), "--split", args.split, "--output", str(ablation_report)]
        for name in ABLATIONS:
            ablation_args.extend([f"--{name.replace('_', '-')}", str(ablation_files[name])])
        run([PYTHON, str(ROOT / "scripts/evaluation/run_discovery_gap_ablations.py"), *ablation_args])
        summary["steps"]["six_ablations"] = {
            "variants": list(ABLATIONS), "prediction_files": {
                name: {"file_name": path.name, "sha256": sha256(path)} for name, path in ablation_files.items()
            },
            "comparison": {"file_name": ablation_report.name, "sha256": sha256(ablation_report)},
        }
        summary["status"] = "completed"
    except Exception as exc:
        summary["status"] = "blocked_or_failed"
        summary["error"] = str(exc)
        summary["run_finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        (output / "phase4_run_summary.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(json.dumps({"ok": False, "summary": str(output / "phase4_run_summary.json"),
                          "status": summary["status"], "error": str(exc)}, indent=2))
        return 1

    summary["run_finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    summary_path = output / "phase4_run_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "status": summary["status"], "summary": str(summary_path),
                      "baseline_comparison": str(output / "baseline_comparison.json"),
                      "ablation_comparison": str(output / "ablation_comparison.json")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
