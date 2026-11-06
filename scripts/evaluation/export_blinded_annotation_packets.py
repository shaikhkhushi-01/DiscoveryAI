#!/usr/bin/env python3
"""Export blinded, gold-label-free packets from candidate-only records for independent reviewers.

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



def _opaque_id(record_id: str, salt: str) -> str:
    digest = hashlib.sha256(f"{salt}:{record_id}".encode("utf-8")).hexdigest()[:16]
    return f"blind-{digest}"


def _validate_candidate_source(source: Any) -> None:
    if not isinstance(source, dict):
        raise ValueError("candidate source root must be an object")
    for field in ("benchmark_id", "benchmark_version", "annotation_rubric_version"):
        if not isinstance(source.get(field), str) or not source[field].strip():
            raise ValueError(f"{field} must be a non-empty string")
    records = source.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("records must be a non-empty array")
    seen: set[str] = set()
    for index, record in enumerate(records):
        prefix = f"records[{index}]"
        if not isinstance(record, dict):
            raise ValueError(f"{prefix} must be an object")
        rid = record.get("record_id")
        if not isinstance(rid, str) or not rid.strip():
            raise ValueError(f"{prefix}.record_id must be non-empty")
        if rid in seen:
            raise ValueError(f"duplicate record_id {rid!r}")
        seen.add(rid)
        if not isinstance(record.get("research_question"), str) or not record["research_question"].strip():
            raise ValueError(f"{prefix}.research_question must be non-empty")
        corpus = record.get("corpus_snapshot")
        if not isinstance(corpus, dict) or any(not isinstance(corpus.get(k), str) or not corpus[k].strip() for k in ("corpus_id", "snapshot_date", "scope_statement")):
            raise ValueError(f"{prefix}.corpus_snapshot is incomplete")
        candidate = record.get("candidate_gap")
        if not isinstance(candidate, dict) or any(not isinstance(candidate.get(k), str) or not candidate[k].strip() for k in ("candidate_id", "title", "description", "gap_type")):
            raise ValueError(f"{prefix}.candidate_gap is incomplete")


def build_blinded_packets(
    benchmark: dict[str, Any], *, include_paper_ids: bool = False, salt: str | None = None
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build two identical blind packets from candidate-only input."""
    _validate_candidate_source(benchmark)
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
    parser.add_argument("--candidates", required=True, type=Path, help="Candidate-only JSON without gold labels.")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--include-paper-ids", action="store_true",
                        help="Include corpus paper IDs; default hides them to reduce identity cues.")
    args = parser.parse_args()
    try:
        benchmark, _ = load_benchmark(args.benchmark, require_evaluable=False)
        source = json.loads(args.candidates.read_text(encoding="utf-8"))
        packet, crosswalk = build_blinded_packets(
            source, include_paper_ids=args.include_paper_ids
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
