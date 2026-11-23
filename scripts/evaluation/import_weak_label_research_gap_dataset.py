#!/usr/bin/env python3
"""Import the LLM-extracted Research Gap Discovery dataset as explicitly weak labels.

This importer does not convert source rows into the adjudicated DiscoveryAI gold
benchmark. It preserves source provenance and emits a separate, non-evaluable
silver-label artifact for descriptive text analysis only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

DATASET_ID = "research-gap-discovery-llm-extracted-limit-v2"
DATASET_VERSION = "2"
DATASET_DOI = "10.17632/px9xd7tw8n.2"
DATASET_URL = "https://data.mendeley.com/datasets/px9xd7tw8n/2"
REQUIRED_COLUMNS = (
    "Serial", "Paper ID", "Version", "Title", "Published",
    "Primary Category", "Categories", "Abstract", "Limitation",
    "Research Gap", "Importance", "Gap Refers To Own Work",
    "Generator Model", "Split",
)
ALLOWED_SPLITS = {"train", "validation", "test"}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def import_weak_label_csv(csv_path: str | Path) -> dict[str, Any]:
    """Read and validate source CSV without upgrading labels to human gold."""
    source = Path(csv_path)
    if not source.is_file():
        raise FileNotFoundError(f"dataset CSV not found: {source}")

    records: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    split_counts: Counter[str] = Counter()
    model_counts: Counter[str] = Counter()
    own_work_counts: Counter[str] = Counter()
    min_published: date | None = None
    max_published: date | None = None

    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV header is missing")
        missing = sorted(set(REQUIRED_COLUMNS) - set(reader.fieldnames))
        if missing:
            raise ValueError(f"CSV missing required columns: {missing}")

        for line_number, row in enumerate(reader, start=2):
            paper_id = (row.get("Paper ID") or "").strip()
            if not paper_id:
                raise ValueError(f"line {line_number}: Paper ID is empty")
            if paper_id in seen_ids:
                raise ValueError(f"line {line_number}: duplicate Paper ID {paper_id!r}")
            seen_ids.add(paper_id)

            split = (row.get("Split") or "").strip().lower()
            if split not in ALLOWED_SPLITS:
                raise ValueError(f"line {line_number}: unsupported Split {split!r}")
            model = (row.get("Generator Model") or "").strip()
            if not model:
                raise ValueError(f"line {line_number}: Generator Model is empty")

            required_text = ("Title", "Abstract", "Limitation", "Research Gap", "Importance", "Published")
            empty = [column for column in required_text if not (row.get(column) or "").strip()]
            if empty:
                raise ValueError(f"line {line_number}: empty required fields {empty}")
            published_text = row["Published"].strip()
            try:
                published = date.fromisoformat(published_text[:10])
            except ValueError as exc:
                raise ValueError(f"line {line_number}: invalid Published date {published_text!r}") from exc

            own_work = (row.get("Gap Refers To Own Work") or "").strip().lower()
            if own_work not in {"true", "false"}:
                raise ValueError(f"line {line_number}: Gap Refers To Own Work must be true or false")

            records.append({
                "paper_id": paper_id,
                "version": (row.get("Version") or "").strip(),
                "title": row["Title"].strip(),
                "published": published.isoformat(),
                "primary_category": (row.get("Primary Category") or "").strip(),
                "categories_raw": (row.get("Categories") or "").strip(),
                "abstract": row["Abstract"].strip(),
                "limitation_llm_inferred": row["Limitation"].strip(),
                "research_gap_llm_inferred": row["Research Gap"].strip(),
                "importance_llm_inferred": row["Importance"].strip(),
                "gap_refers_to_own_work_heuristic": own_work == "true",
                "generator_model": model,
                "split": split,
                "source_serial": (row.get("Serial") or "").strip(),
                "label_provenance": {
                    "method": "LLM-generated from title and abstract",
                    "human_expert_validated": False,
                    "adjudicated": False,
                },
            })
            split_counts[split] += 1
            model_counts[model] += 1
            own_work_counts[own_work] += 1
            min_published = published if min_published is None else min(min_published, published)
            max_published = published if max_published is None else max(max_published, published)

    if not records:
        raise ValueError("CSV contains no data rows")
    return {
        "artifact_schema_version": "1.0",
        "artifact_type": "weak_label_research_gap_dataset",
        "evaluation_eligibility": {
            "status": "not_gold_benchmark_compatible",
            "allowed_use": ["descriptive_text_analysis", "weak_label_exploration"],
            "prohibited_claims": [
                "expert-validated ground truth",
                "adjudicated benchmark performance",
                "evidence-grounded retrieval accuracy",
                "research-gap discovery effectiveness",
            ],
            "reason": (
                "Source labels are LLM-inferred from title and abstract, have no "
                "expert adjudication or traceable full-text chunk evidence, and "
                "do not match the DiscoveryAI gold benchmark schema."
            ),
        },
        "source": {
            "dataset_id": DATASET_ID,
            "dataset_version": DATASET_VERSION,
            "doi": DATASET_DOI,
            "url": DATASET_URL,
            "filename": source.name,
            "sha256": _sha256(source),
            "row_count": len(records),
            "published_date_range": {
                "min": min_published.isoformat(),
                "max": max_published.isoformat(),
            },
            "split_counts": dict(sorted(split_counts.items())),
            "generator_model_counts": dict(sorted(model_counts.items())),
            "own_work_flag_counts": dict(sorted(own_work_counts.items())),
            "known_methodological_limitations": [
                "Labels are LLM-inferred from title and abstract, not expert-validated.",
                "Generator models may have distinguishable output styles.",
                "Limitation, research gap, and importance fields are generated together and may echo one another.",
                "Title and method names may leak into generated text.",
                "Source selection used limitation/future-work keyword queries.",
                "The own-work flag is heuristic and may contain errors.",
                "Splits are random 80/10/10 stratified by primary category and generator model, not chronological.",
            ],
        },
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Path to source gaps_v2.csv")
    parser.add_argument("--output", required=True, type=Path, help="Destination JSON artifact")
    args = parser.parse_args()
    try:
        artifact = import_weak_label_csv(args.input)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_suffix(args.output.suffix + ".tmp")
        temporary.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        temporary.replace(args.output)
    except (OSError, UnicodeError, csv.Error, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps({
        "ok": True,
        "output": str(args.output),
        "rows": artifact["source"]["row_count"],
        "split_counts": artifact["source"]["split_counts"],
        "evaluation_eligibility": artifact["evaluation_eligibility"]["status"],
        "sha256": artifact["source"]["sha256"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
