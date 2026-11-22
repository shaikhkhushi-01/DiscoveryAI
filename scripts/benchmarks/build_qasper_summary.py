#!/usr/bin/env python3
"""Build a shareable aggregate-only QASPER validation report."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def validate_metrics(report: dict[str, Any], label: str) -> None:
    required = ("questions_scored", "predictions_received", "missing_predictions",
                "answer_f1", "evidence_f1", "answer_f1_by_type")
    missing = [key for key in required if key not in report]
    if missing:
        raise ValueError(f"{label}: missing metric fields {missing}")
    for key in ("answer_f1", "evidence_f1"):
        value = report[key]
        if not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError(f"{label}: {key} must be a finite value in [0, 1]")
    if report["questions_scored"] < 1:
        raise ValueError(f"{label}: no questions were scored")


def build_summary(manifest_path: Path,
                  entries: dict[str, tuple[Path, Path]]) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    if manifest.get("dataset") != "allenai/qasper" or manifest.get("dataset_version") != "0.3.0":
        raise ValueError("Expected pinned allenai/qasper v0.3.0 manifest")
    systems: dict[str, Any] = {}
    shared_manifest_hash = sha256_file(manifest_path)
    expected_questions: int | None = None
    shared_query_hash: str | None = None
    shared_chunk_hash: str | None = None
    for label, (report_path, metadata_path) in entries.items():
        report = load_json(report_path)
        metadata = load_json(metadata_path)
        validate_metrics(report, label)
        if metadata.get("split") != "validation":
            raise ValueError(f"{label}: only validation split can be summarized")
        if metadata.get("mode") != "extractive":
            raise ValueError(f"{label}: expected deterministic extractive baseline")
        if metadata.get("gold_references_loaded") is not False:
            raise ValueError(f"{label}: generator metadata indicates gold references were loaded")
        if metadata.get("manifest_sha256") != shared_manifest_hash:
            raise ValueError(f"{label}: manifest hash mismatch")
        query_hash = metadata.get("query_file_sha256")
        chunk_hash = metadata.get("chunk_file_sha256")
        for name, value in (("query", query_hash), ("chunk", chunk_hash)):
            if not isinstance(value, str) or len(value) != 64:
                raise ValueError(f"{label}: missing or malformed {name} SHA-256")
        if shared_query_hash is None:
            shared_query_hash, shared_chunk_hash = query_hash, chunk_hash
        elif query_hash != shared_query_hash or chunk_hash != shared_chunk_hash:
            raise ValueError("Systems were not generated from the same query/chunk snapshots")
        if metadata.get("questions_generated") != report.get("predictions_received"):
            raise ValueError(f"{label}: generated prediction count differs from evaluated prediction count")
        if expected_questions is None:
            expected_questions = report["questions_scored"]
        elif report["questions_scored"] != expected_questions:
            raise ValueError("Systems were not evaluated on the same number of gold questions")
        systems[label] = {
            "split": metadata["split"],
            "mode": metadata["mode"],
            "context_scope": metadata.get("context_scope"),
            "questions_scored": report["questions_scored"],
            "predictions_received": report["predictions_received"],
            "missing_predictions": report["missing_predictions"],
            "answer_f1": report["answer_f1"],
            "answer_f1_by_type": report["answer_f1_by_type"],
            "evidence_f1": report["evidence_f1"],
            "query_file_sha256": metadata["query_file_sha256"],
            "chunk_file_sha256": metadata["chunk_file_sha256"],
            "manifest_sha256": metadata["manifest_sha256"],
            "code_revision": metadata["code_revision"],
        }
    if len(systems) < 2:
        raise ValueError("At least two comparable systems are required")
    labels = list(systems)
    first, second = systems[labels[0]], systems[labels[1]]
    return {
        "report_type": "aggregate_only_qasper_validation",
        "dataset": manifest["dataset"],
        "dataset_version": manifest["dataset_version"],
        "dataset_license_claimed_by_dataset_card": manifest.get("license_claimed_by_official_dataset_card"),
        "manifest_sha256": shared_manifest_hash,
        "questions_scored_per_system": expected_questions,
        "systems": systems,
        "paired_differences": {
            "comparison": f"{labels[1]} minus {labels[0]}",
            "answer_f1": second["answer_f1"] - first["answer_f1"],
            "evidence_f1": second["evidence_f1"] - first["evidence_f1"],
        },
        "interpretation_limitations": [
            "This is a validation-set comparison, not a locked test-set result.",
            "QASPER measures scientific-paper question answering and evidence selection, not research-gap novelty or hypothesis quality.",
            "The BM25 extractive pipeline is a transparent baseline, not a state-of-the-art language model.",
            "The abstract-only versus full-text comparison changes available context and is not a human-annotated discovery-quality evaluation.",
            "No causal or statistical significance claim is made from aggregate score differences alone.",
        ],
        "private_or_large_payloads_excluded": [
            "raw QASPER archives", "normalized paper text", "gold reference JSONL",
            "individual predictions", "per-question outputs",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--abstract-report", type=Path, required=True)
    parser.add_argument("--abstract-metadata", type=Path, required=True)
    parser.add_argument("--full-text-report", type=Path, required=True)
    parser.add_argument("--full-text-metadata", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = build_summary(args.manifest, {
            "abstract_only": (args.abstract_report, args.abstract_metadata),
            "full_text": (args.full_text_report, args.full_text_metadata),
        })
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps({"ok": True, "output": str(args.output),
                      "questions_scored_per_system": result["questions_scored_per_system"],
                      "paired_differences": result["paired_differences"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
