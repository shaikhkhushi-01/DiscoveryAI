#!/usr/bin/env python3
"""Export blinded, gold-label-free packets for independent DiscoveryGapBench reviewers.

The input benchmark is treated as confidential source material. Packets never include
gold_assessment, gold_evidence, adjudication state, prior annotator IDs, or source record IDs.
A private mapping file is emitted separately and must not be shared with reviewers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import secrets
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.evaluation.discovery_gap_bench import load_benchmark  # noqa: E402


def _opaque_id(record_id: str, salt: str) -> str:
    digest = hashlib.sha256(f"{salt}:{record_id}".encode("utf-8")).hexdigest()[:16]
    return f"blind-{digest}"


def build_blinded_packets(
    benchmark: dict[str, Any], *, include_paper_ids: bool = False, salt: str | None = None
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build two identical blind packets plus a confidential source-ID crosswalk."""
    salt = salt or secrets.token_hex(16)
    mapping: dict[str, str] = {}
    packet_records = []
    seen_blind: set[str] = set()

    for record in benchmark["records"]:
        source_id = record["record_id"]
        blind_id = _opaque_id(source_id, salt)
        if blind_id in seen_blind:
            raise ValueError("blind ID collision; regenerate with a new salt")
        seen_blind.add(blind_id)
        mapping[blind_id] = source_id

        corpus = record["corpus_snapshot"]
        corpus_view = {
            "corpus_id": corpus["corpus_id"],
            "snapshot_date": corpus["snapshot_date"],
            "scope_statement": corpus["scope_statement"],
        }
        if include_paper_ids:
            corpus_view["paper_ids"] = list(corpus["paper_ids"])

        packet_records.append({
            "blind_record_id": blind_id,
            "research_question": record["research_question"],
            "corpus_snapshot": corpus_view,
            "candidate_gap": dict(record["candidate_gap"]),
            "review_form": {
                "gap_status": None,
                "novelty_within_corpus": None,
                "relevance": None,
                "feasibility": None,
                "evidence_quality": None,
                "evidence": [],
                "rationale": "",
                "reviewer_notes": "",
            },
        })

    packet = {
        "packet_schema_version": "1.0",
        "benchmark_id": benchmark["benchmark_id"],
        "benchmark_version": benchmark["benchmark_version"],
        "annotation_rubric_version": benchmark["annotation_rubric_version"],
        "instructions": (
            "Annotate independently using the supplied rubric. Do not infer global novelty. "
            "Do not discuss labels with the other reviewer. Cite evidence using paper_id, "
            "document_id, chunk_id and stance. Do not access model predictions."
        ),
        "records": packet_records,
    }
    crosswalk = {
        "warning": "CONFIDENTIAL: never share this file with reviewers or publish it.",
        "blind_id_salt": salt,
        "blind_to_source_record_id": mapping,
    }
    return packet, crosswalk


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--include-paper-ids", action="store_true",
                        help="Include corpus paper IDs; default hides them to reduce identity cues.")
    args = parser.parse_args()
    try:
        benchmark, _ = load_benchmark(args.benchmark, require_evaluable=False)
        packet, crosswalk = build_blinded_packets(
            benchmark, include_paper_ids=args.include_paper_ids
        )
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for reviewer in ("reviewer-a", "reviewer-b"):
            target = args.output_dir / f"{reviewer}-packet.json"
            target.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
        crosswalk_path = args.output_dir / "CONFIDENTIAL-blind-id-crosswalk.json"
        crosswalk_path.write_text(json.dumps(crosswalk, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({
            "ok": True,
            "record_count": len(packet["records"]),
            "reviewer_packets": 2,
            "output_dir": str(args.output_dir),
            "crosswalk": str(crosswalk_path),
            "warning": "Keep the crosswalk private; packets intentionally exclude gold labels and evidence.",
        }, indent=2))
        return 0
    except (OSError, json.JSONDecodeError, ValueError, KeyError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
