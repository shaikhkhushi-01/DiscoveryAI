#!/usr/bin/env python3
"""Validate paired, independently submitted NLP annotation JSONL records."""
import argparse
import json
from collections import defaultdict
from pathlib import Path

CATEGORIES = {"MODEL_METHOD","DATA_RESOURCE","EVALUATION","ROBUSTNESS_SAFETY","RETRIEVAL_QA_RAG","LINGUISTIC_ANALYSIS","REPRODUCIBILITY","OTHER_NLP","OUT_OF_SCOPE"}
RELEVANCE = {"IN_SCOPE","OUT_OF_SCOPE","UNCERTAIN"}
CONTRIBUTIONS = {"METHOD","DATA","EVALUATION","ANALYSIS","REPLICATION","POSITION","OTHER"}
CONFIDENCE = {"LOW","MEDIUM","HIGH"}
REPRO = {"CODE_AVAILABLE","DATA_AVAILABLE","DETAILS_SUFFICIENT","NOT_REPORTED","NOT_APPLICABLE"}
REQUIRED = {"paper_id","version_id","reviewer_id","annotated_at_utc","nlp_relevance","primary_category","contribution_type","research_question","claimed_contribution","evidence_locators","reproducibility","confidence"}

def load_records(path):
    records = []
    for line_no, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {line_no}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"line {line_no}: record must be a JSON object")
        missing = sorted(REQUIRED - row.keys())
        if missing:
            raise ValueError(f"line {line_no}: missing fields: {', '.join(missing)}")
        checks = [
            ("nlp_relevance", RELEVANCE), ("primary_category", CATEGORIES),
            ("contribution_type", CONTRIBUTIONS), ("confidence", CONFIDENCE)
        ]
        for field, allowed in checks:
            if row[field] not in allowed:
                raise ValueError(f"line {line_no}: invalid {field}")
        if not isinstance(row["evidence_locators"], list) or not row["evidence_locators"]:
            raise ValueError(f"line {line_no}: evidence_locators must be a non-empty list")
        if not isinstance(row["reproducibility"], list) or not set(row["reproducibility"]) <= REPRO:
            raise ValueError(f"line {line_no}: invalid reproducibility values")
        if row["nlp_relevance"] == "OUT_OF_SCOPE" and row["primary_category"] != "OUT_OF_SCOPE":
            raise ValueError(f"line {line_no}: OUT_OF_SCOPE relevance requires OUT_OF_SCOPE category")
        for field in ("paper_id","version_id","reviewer_id","annotated_at_utc","research_question","claimed_contribution"):
            if not isinstance(row[field], str) or not row[field].strip():
                raise ValueError(f"line {line_no}: {field} must be a non-empty string")
        records.append(row)
    return records

def validate_pairs(records):
    grouped, seen = defaultdict(list), set()
    for row in records:
        key = (row["paper_id"], row["version_id"], row["reviewer_id"])
        if key in seen:
            raise ValueError(f"duplicate reviewer record: {key}")
        seen.add(key)
        grouped[(row["paper_id"], row["version_id"])].append(row)
    incomplete = []
    for (paper_id, version_id), pair in grouped.items():
        if len(pair) != 2 or len({x["reviewer_id"] for x in pair}) != 2:
            incomplete.append({"paper_id":paper_id,"version_id":version_id,"reviewer_count":len(pair)})
    return grouped, incomplete

def cohen_kappa(pairs):
    n = len(pairs)
    if not n:
        return None
    labels = {v for pair in pairs for v in pair}
    observed = sum(a == b for a,b in pairs) / n
    a_counts, b_counts = defaultdict(int), defaultdict(int)
    for a,b in pairs:
        a_counts[a] += 1
        b_counts[b] += 1
    expected = sum((a_counts[x]/n)*(b_counts[x]/n) for x in labels)
    return None if expected == 1 else (observed-expected)/(1-expected)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    records = load_records(args.input)
    grouped, incomplete = validate_pairs(records)
    agreement = {}
    for field in ("nlp_relevance","primary_category","contribution_type"):
        pairs = [(v[0][field],v[1][field]) for v in grouped.values() if len(v)==2 and v[0]["reviewer_id"] != v[1]["reviewer_id"]]
        agreement[field] = {"paired_n":len(pairs),"raw_agreement":sum(a==b for a,b in pairs)/len(pairs) if pairs else None,"cohens_kappa":cohen_kappa(pairs)}
    report = {"record_count":len(records),"paper_version_count":len(grouped),"complete_independent_pairs":sum(1 for v in grouped.values() if len(v)==2 and v[0]["reviewer_id"] != v[1]["reviewer_id"]),"incomplete_pairs":incomplete,"agreement":agreement,"warning":"Descriptive agreement only; this does not establish reviewer qualification, blinding, rights clearance, or scientific validity."}
    out = Path(args.report)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))

if __name__ == "__main__":
    main()
