from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
GAP_TYPES = {"topic", "dataset", "benchmark", "experiment", "evaluation", "application", "interdisciplinary"}
GAP_STATUSES = {"supported", "contradicted", "inconclusive"}
ANNOTATION_STATES = {"pending", "adjudicated"}
SPLITS = {"train", "validation", "test"}
RATING_FIELDS = ("novelty_within_corpus", "relevance", "feasibility", "evidence_quality")


@dataclass
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    evaluable_record_ids: list[str] = field(default_factory=list)
    pending_record_ids: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors

    @property
    def evaluable_count(self) -> int:
        return len(self.evaluable_record_ids)

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "record_count": self.evaluable_count + len(self.pending_record_ids),
            "evaluable_record_count": self.evaluable_count,
            "pending_record_count": len(self.pending_record_ids),
            "evaluable_record_ids": self.evaluable_record_ids,
            "pending_record_ids": self.pending_record_ids,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and not value.strip().lower().startswith("replace-with")


def _is_rating(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 3


def _validate_evidence(items: Any, path: str, paper_ids: set[str], report: ValidationReport) -> int:
    if not isinstance(items, list):
        report.errors.append(f"{path} must be an array")
        return 0
    seen: set[tuple[str, str, str]] = set()
    for index, item in enumerate(items):
        item_path = f"{path}[{index}]"
        if not isinstance(item, dict):
            report.errors.append(f"{item_path} must be an object")
            continue
        paper_id, document_id, chunk_id = (item.get(k) for k in ("paper_id", "document_id", "chunk_id"))
        if not all(_nonempty(v) for v in (paper_id, document_id, chunk_id)):
            report.errors.append(f"{item_path} requires non-empty paper_id, document_id, and chunk_id")
            continue
        if paper_id not in paper_ids:
            report.errors.append(f"{item_path}.paper_id {paper_id!r} is not in corpus_snapshot.paper_ids")
        key = (paper_id, document_id, chunk_id)
        if key in seen:
            report.errors.append(f"{item_path} duplicates evidence tuple {key!r}")
        seen.add(key)
        relevance = item.get("relevance")
        if not _is_rating(relevance):
            report.errors.append(f"{item_path}.relevance must be an integer from 0 to 3")
        if not _nonempty(item.get("rationale")):
            report.errors.append(f"{item_path}.rationale must be a non-placeholder explanation")
    return len(items)


def validate_benchmark(data: Any) -> ValidationReport:
    report = ValidationReport()
    if not isinstance(data, dict):
        report.errors.append("benchmark root must be an object")
        return report
    for key in ("schema_version", "benchmark_id", "benchmark_version", "annotation_rubric_version"):
        if not _nonempty(data.get(key)):
            report.errors.append(f"{key} must be a non-empty, non-placeholder string")
    if data.get("schema_version") != SCHEMA_VERSION:
        report.errors.append(f"schema_version must equal supported version {SCHEMA_VERSION!r}")
    records = data.get("records")
    if not isinstance(records, list):
        report.errors.append("records must be an array")
        return report
    if not records:
        report.warnings.append("benchmark contains no records; no metrics can be computed")

    seen_record_ids: set[str] = set()
    for index, record in enumerate(records):
        path = f"records[{index}]"
        if not isinstance(record, dict):
            report.errors.append(f"{path} must be an object")
            continue
        record_id = record.get("record_id")
        if not _nonempty(record_id):
            report.errors.append(f"{path}.record_id must be a non-empty, non-placeholder string")
            record_id = f"__invalid_{index}"
        elif record_id in seen_record_ids:
            report.errors.append(f"{path}.record_id {record_id!r} is duplicated")
        seen_record_ids.add(record_id)

        question = record.get("research_question")
        if not _nonempty(question):
            report.errors.append(f"{path}.research_question must be non-empty")
        corpus = record.get("corpus_snapshot")
        if not isinstance(corpus, dict):
            report.errors.append(f"{path}.corpus_snapshot must be an object")
            corpus = {}
        if not _nonempty(corpus.get("corpus_id")):
            report.errors.append(f"{path}.corpus_snapshot.corpus_id must be non-empty")
        if not _nonempty(corpus.get("scope_statement")):
            report.errors.append(f"{path}.corpus_snapshot.scope_statement must describe corpus scope")
        try:
            date.fromisoformat(corpus.get("snapshot_date", ""))
        except (TypeError, ValueError):
            report.errors.append(f"{path}.corpus_snapshot.snapshot_date must use YYYY-MM-DD")
        paper_ids = corpus.get("paper_ids")
        if not isinstance(paper_ids, list) or not paper_ids or any(not _nonempty(p) for p in paper_ids):
            report.errors.append(f"{path}.corpus_snapshot.paper_ids must be a non-empty array of IDs")
            paper_ids_set: set[str] = set()
        else:
            paper_ids_set = set(paper_ids)
            if len(paper_ids_set) != len(paper_ids):
                report.errors.append(f"{path}.corpus_snapshot.paper_ids contains duplicates")

        candidate = record.get("candidate_gap")
        if not isinstance(candidate, dict):
            report.errors.append(f"{path}.candidate_gap must be an object")
            candidate = {}
        for key in ("candidate_id", "title", "description"):
            if not _nonempty(candidate.get(key)):
                report.errors.append(f"{path}.candidate_gap.{key} must be non-empty")
        if candidate.get("gap_type") not in GAP_TYPES:
            report.errors.append(f"{path}.candidate_gap.gap_type must be one of {sorted(GAP_TYPES)}")

        evidence = record.get("gold_evidence")
        if not isinstance(evidence, dict):
            report.errors.append(f"{path}.gold_evidence must be an object")
            evidence = {}
        support_count = _validate_evidence(evidence.get("supporting"), f"{path}.gold_evidence.supporting", paper_ids_set, report)
        contradiction_count = _validate_evidence(evidence.get("contradictory"), f"{path}.gold_evidence.contradictory", paper_ids_set, report)
        if support_count + contradiction_count == 0:
            report.errors.append(f"{path}.gold_evidence must contain at least one supporting or contradictory passage")

        assessment = record.get("gold_assessment")
        if not isinstance(assessment, dict):
            report.errors.append(f"{path}.gold_assessment must be an object")
            assessment = {}
        if assessment.get("gap_status") not in GAP_STATUSES:
            report.errors.append(f"{path}.gold_assessment.gap_status must be one of {sorted(GAP_STATUSES)}")
        for key in RATING_FIELDS:
            if not _is_rating(assessment.get(key)):
                report.errors.append(f"{path}.gold_assessment.{key} must be an integer from 0 to 3")

        annotations = record.get("annotations")
        if not isinstance(annotations, dict):
            report.errors.append(f"{path}.annotations must be an object")
            annotations = {}
        annotators = annotations.get("annotator_ids")
        if not isinstance(annotators, list) or not annotators or any(not _nonempty(a) for a in annotators):
            report.errors.append(f"{path}.annotations.annotator_ids must contain pseudonymous IDs")
        try:
            date.fromisoformat(annotations.get("annotated_at", ""))
        except (TypeError, ValueError):
            report.errors.append(f"{path}.annotations.annotated_at must use YYYY-MM-DD")
        annotation_state = annotations.get("adjudication_status")
        if annotation_state not in ANNOTATION_STATES:
            report.errors.append(f"{path}.annotations.adjudication_status must be pending or adjudicated")
        if annotation_state == "adjudicated" and not _nonempty(annotations.get("adjudication_notes")):
            report.errors.append(f"{path}.annotations.adjudication_notes is required for adjudicated records")
        if record.get("split") not in SPLITS:
            report.errors.append(f"{path}.split must be one of {sorted(SPLITS)}")

        # Pending labels are valid draft data but are never eligible for scored runs.
        if annotation_state == "adjudicated" and all(_is_rating(assessment.get(k)) for k in RATING_FIELDS):
            report.evaluable_record_ids.append(str(record_id))
        else:
            report.pending_record_ids.append(str(record_id))
            report.warnings.append(f"{path} is not score-eligible until expert annotation is adjudicated")

    if not report.evaluable_record_ids:
        report.warnings.append("no adjudicated records available; evaluation must not emit benchmark metrics")
    return report


def load_benchmark(path: str | Path, *, require_evaluable: bool = False) -> tuple[dict[str, Any], ValidationReport]:
    """Load and validate a JSON benchmark; malformed data fails closed."""
    source = Path(path)
    with source.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    report = validate_benchmark(data)
    if not report.valid:
        raise ValueError("Invalid DiscoveryGapBench:\n- " + "\n- ".join(report.errors))
    if require_evaluable and report.evaluable_count == 0:
        raise ValueError("DiscoveryGapBench has no adjudicated records; refusing to score an empty gold set")
    return data, report


def evaluable_records(data: dict[str, Any], report: ValidationReport) -> list[dict[str, Any]]:
    """Return only adjudicated records after successful validation."""
    if not report.valid:
        raise ValueError("Cannot select records from an invalid benchmark")
    eligible = set(report.evaluable_record_ids)
    return [record for record in data["records"] if record["record_id"] in eligible]
