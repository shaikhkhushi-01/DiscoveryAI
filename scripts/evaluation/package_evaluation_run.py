#!/usr/bin/env python3
"""Create a provenance manifest for one completed offline evaluation run.

The manifest stores artifact hashes and selected run metadata, not source PDFs,
reviewer identities, API keys, raw prompts, or private corpus contents.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is not readable valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} JSON root must be an object")
    return value


def _git_revision() -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], check=True, capture_output=True,
            text=True, timeout=5,
        ).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def build_run_manifest(
    *, benchmark_path: Path, predictions_path: Path, report_path: Path,
    protocol_path: Path | None = None, rubric_path: Path | None = None,
    dependency_lock_paths: list[Path] | None = None,
    code_revision: str | None = None,
) -> dict[str, Any]:
    benchmark = _read_json(benchmark_path, "benchmark")
    predictions = _read_json(predictions_path, "predictions")
    report = _read_json(report_path, "evaluation report")

    run_metadata = predictions.get("run_metadata")
    report_metadata = report.get("run_metadata")
    if not isinstance(run_metadata, dict) or not isinstance(report_metadata, dict):
        raise ValueError("prediction and report must both contain run_metadata objects")
    if run_metadata != report_metadata:
        raise ValueError("evaluation report run_metadata differs from the source prediction artifact")

    expected = {
        "benchmark_id": benchmark.get("benchmark_id"),
        "benchmark_version": benchmark.get("benchmark_version"),
        "annotation_rubric_version": benchmark.get("annotation_rubric_version"),
    }
    reported = report.get("benchmark") or {}
    for key, value in expected.items():
        if reported.get(key) != value:
            raise ValueError(f"evaluation report {key} does not match the benchmark artifact")

    predictions_list = predictions.get("predictions")
    if not isinstance(predictions_list, list):
        raise ValueError("predictions artifact must contain a predictions array")
    predicted_ids = [item.get("record_id") for item in predictions_list if isinstance(item, dict)]
    if len(predicted_ids) != len(predictions_list) or len(predicted_ids) != len(set(predicted_ids)):
        raise ValueError("predictions artifact contains malformed or duplicate record IDs")

    revision = code_revision or os.getenv("GITHUB_SHA") or _git_revision()
    if not revision:
        raise ValueError("code revision is required; pass --code-revision or set GITHUB_SHA")

    artifacts: dict[str, Any] = {}
    for label, path in (
        ("benchmark", benchmark_path), ("predictions", predictions_path),
        ("evaluation_report", report_path), ("protocol", protocol_path),
        ("annotation_rubric", rubric_path),
    ):
        if path is None:
            continue
        if not path.is_file():
            raise ValueError(f"{label} artifact does not exist: {path}")
        artifacts[label] = {"file_name": path.name, "sha256": sha256_file(path), "size_bytes": path.stat().st_size}

    lock_artifacts = []
    for path in dependency_lock_paths or []:
        if not path.is_file():
            raise ValueError(f"dependency lock file does not exist: {path}")
        lock_artifacts.append({
            "file_name": path.name, "sha256": sha256_file(path), "size_bytes": path.stat().st_size
        })

    benchmark_meta = report.get("benchmark") or {}
    return {
        "manifest_schema_version": "1.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_id": run_metadata.get("run_id"),
        "system_id": run_metadata.get("system_id"),
        "code_revision": revision,
        "benchmark": {
            **expected,
            "corpus_ids": benchmark_meta.get("corpus_ids", []),
            "split": benchmark_meta.get("split"),
            "evaluated_record_count": benchmark_meta.get("evaluated_record_count"),
            "prediction_record_count": len(predicted_ids),
        },
        "model_and_retrieval": {
            key: run_metadata.get(key) for key in (
                "system_version", "model_provider", "model_name", "prompt_version",
                "embedding_model", "retrieval_config", "corpus_id",
            )
        },
        "execution_environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "artifacts": artifacts,
        "dependency_locks": lock_artifacts,
        "integrity_notes": [
            "SHA-256 hashes identify the exact files used to produce this manifest.",
            "This manifest does not independently prove that a model run followed the declared protocol.",
            "Do not place secrets, reviewer identities, private source text, or access tokens in run metadata.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", required=True, type=Path)
    parser.add_argument("--predictions", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--protocol", type=Path)
    parser.add_argument("--rubric", type=Path)
    parser.add_argument("--dependency-lock", action="append", default=[], type=Path)
    parser.add_argument("--code-revision")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        manifest = build_run_manifest(
            benchmark_path=args.benchmark, predictions_path=args.predictions,
            report_path=args.report, protocol_path=args.protocol,
            rubric_path=args.rubric, dependency_lock_paths=args.dependency_lock,
            code_revision=args.code_revision,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps({
        "ok": True, "run_id": manifest["run_id"], "system_id": manifest["system_id"],
        "code_revision": manifest["code_revision"],
        "artifact_count": len(manifest["artifacts"]) + len(manifest["dependency_locks"]),
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
