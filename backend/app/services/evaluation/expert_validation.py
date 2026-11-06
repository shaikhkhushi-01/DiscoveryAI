from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATUSES = {"supported", "contradicted", "inconclusive"}
RATINGS = ("novelty_within_corpus", "relevance", "feasibility", "evidence_quality")


def _kappa(left: list[Any], right: list[Any], *, ordinal: bool = False) -> dict[str, Any]:
    if len(left) != len(right) or not left:
        return {"value": None, "n": len(left), "reason": "requires paired non-empty annotations"}
    categories = sorted(set(left) | set(right))
    n = len(left)
    observed = sum(a == b for a, b in zip(left, right)) / n
    left_counts, right_counts = Counter(left), Counter(right)
    expected = sum(left_counts[c] * right_counts[c] for c in categories) / (n * n)
    if ordinal:
        if len(categories) < 2:
            return {"value": 1.0 if observed == 1.0 else None, "n": n, "method": "quadratic weighted Cohen kappa"}
        span = max(categories) - min(categories)
        if span == 0:
            return {"value": 1.0, "n": n, "method": "quadratic weighted Cohen kappa"}
        observed_disagreement = sum(
            ((a-b)/span) ** 2 for a,b in zip(left,right)
        ) / n
        expected_disagreement = sum(
            left_counts[a] * right_counts[b] * ((a-b)/span) ** 2
            for a in categories for b in categories
        ) / (n*n)
        value = 1 - observed_disagreement / expected_disagreement if expected_disagreement else 1.0
        return {"value": value, "n": n, "method": "quadratic weighted Cohen kappa"}
    value = (observed - expected) / (1 - expected) if expected < 1 else (1.0 if observed == 1 else None)
    return {"value": value, "n": n, "observed_agreement": observed, "method": "Cohen kappa"}


def _validate_annotation_payload(payload: Any, label: str) -> dict[str, dict[str, Any]]:
    if not isinstance(payload, dict) or not isinstance(payload.get("annotator_id"), str) or not payload["annotator_id"].strip():
        raise ValueError(f"{label}: annotator_id is required")
    annotations = payload.get("annotations")
    if not isinstance(annotations, list) or not annotations:
        raise ValueError(f"{label}: annotations must be a non-empty array")
    result = {}
    for i, item in enumerate(annotations):
        if not isinstance(item, dict) or not isinstance(item.get("record_id"), str) or not item["record_id"].strip():
            raise ValueError(f"{label}: annotations[{i}].record_id is required")
        rid = item["record_id"]
        if rid in result:
            raise ValueError(f"{label}: duplicate record_id {rid!r}")
        assessment = item.get("assessment")
        if not isinstance(assessment, dict) or assessment.get("gap_status") not in STATUSES:
            raise ValueError(f"{label}/{rid}: invalid assessment.gap_status")
        for field in RATINGS:
            value = assessment.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 3:
                raise ValueError(f"{label}/{rid}: {field} must be an integer from 0 to 3")
        evidence = item.get("evidence")
        if not isinstance(evidence, list):
            raise ValueError(f"{label}/{rid}: evidence must be an array")
        seen = set()
        for entry in evidence:
            if not isinstance(entry, dict) or not all(isinstance(entry.get(k), str) and entry[k].strip() for k in ("paper_id","document_id","chunk_id")):
                raise ValueError(f"{label}/{rid}: evidence requires paper_id/document_id/chunk_id")
            if entry.get("stance") not in {"supporting","contradictory"}:
                raise ValueError(f"{label}/{rid}: invalid evidence stance")
            key=(entry["paper_id"],entry["document_id"],entry["chunk_id"])
            if key in seen:
                raise ValueError(f"{label}/{rid}: duplicate evidence tuple {key!r}")
            seen.add(key)
        result[rid] = {"assessment": assessment, "evidence": {(
            e["paper_id"],e["document_id"],e["chunk_id"]
        ): e["stance"] for e in evidence}}
    return result


def _evidence_agreement(a: dict[Any,str], b: dict[Any,str]) -> dict[str, float]:
    left, right = set(a), set(b)
    overlap = left & right
    precision = len(overlap)/len(right) if right else (1.0 if not left else 0.0)
    recall = len(overlap)/len(left) if left else (1.0 if not right else 0.0)
    f1 = 2*precision*recall/(precision+recall) if precision+recall else 0.0
    stance = sum(a[k] == b[k] for k in overlap)/len(overlap) if overlap else 0.0
    return {"evidence_precision":precision,"evidence_recall":recall,"evidence_f1":f1,"shared_evidence_stance_agreement":stance}


def analyze_expert_agreement(first: Any, second: Any) -> dict[str, Any]:
    """Compute paired inter-annotator agreement and produce a disagreement queue."""
    a = _validate_annotation_payload(first, "annotator_a")
    b = _validate_annotation_payload(second, "annotator_b")
    if first["annotator_id"] == second["annotator_id"]:
        raise ValueError("two distinct annotator IDs are required")
    if set(a) != set(b):
        raise ValueError(f"annotators must label identical record IDs; only_a={sorted(set(a)-set(b))}, only_b={sorted(set(b)-set(a))}")
    ids = sorted(a)
    statuses_a=[a[r]["assessment"]["gap_status"] for r in ids]
    statuses_b=[b[r]["assessment"]["gap_status"] for r in ids]
    status_agreement=_kappa(statuses_a,statuses_b)
    ratings={}
    for field in RATINGS:
        ratings[field]=_kappa([a[r]["assessment"][field] for r in ids],
                              [b[r]["assessment"][field] for r in ids],ordinal=True)
    per_record=[]
    for rid in ids:
        evidence=_evidence_agreement(a[rid]["evidence"],b[rid]["evidence"])
        disagreements=[]
        if a[rid]["assessment"]["gap_status"] != b[rid]["assessment"]["gap_status"]:
            disagreements.append("gap_status")
        for field in RATINGS:
            if a[rid]["assessment"][field] != b[rid]["assessment"][field]:
                disagreements.append(field)
        if a[rid]["evidence"] != b[rid]["evidence"]:
            disagreements.append("evidence")
        per_record.append({"record_id":rid,"disagreement_fields":disagreements,**evidence})
    return {
        "report_schema_version":"1.0",
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "annotators":[first["annotator_id"],second["annotator_id"]],
        "record_count":len(ids),
        "agreement":{
            "gap_status":status_agreement,
            "ordinal_ratings":ratings,
            "mean_ordinal_weighted_kappa":sum(v["value"] for v in ratings.values() if v["value"] is not None)/sum(v["value"] is not None for v in ratings.values()) if any(v["value"] is not None for v in ratings.values()) else None,
            "mean_evidence_f1":sum(x["evidence_f1"] for x in per_record)/len(per_record),
            "mean_shared_evidence_stance_agreement":sum(x["shared_evidence_stance_agreement"] for x in per_record)/len(per_record),
        },
        "adjudication_queue":[x for x in per_record if x["disagreement_fields"]],
        "per_record":per_record,
        "interpretation_note":"Agreement statistics are descriptive. Kappa can be unstable with small samples or highly imbalanced labels; report raw agreement and category prevalence alongside it.",
    }


def write_agreement_report(report: dict[str, Any], path: str | Path) -> None:
    target=Path(path)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
