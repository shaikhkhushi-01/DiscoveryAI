#!/usr/bin/env python3
"""Reproducible audit of OpenAlex license metadata claims.

This script does not make legal determinations or grant text-mining permission.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify_claims(claims):
    if not claims:
        return "NO_LICENSE_CLAIM"

    if not isinstance(claims, list):
        raise ValueError("license_claims_openalex must be a list")

    claims = sorted(set(str(x).strip().lower() for x in claims if str(x).strip()))

    if not claims:
        return "NO_LICENSE_CLAIM"
    if len(claims) > 1:
        return "MULTIPLE_OR_MIXED_CLAIMS"

    claim = claims[0]

    categories = {
        "cc-by": "CC_BY_CLAIM_ONLY",
        "cc-by-sa": "CC_BY_SA_CLAIM_ONLY",
        "cc-by-nc": "NONCOMMERCIAL_OR_NODERIVATIVES_CLAIM",
        "cc-by-nc-nd": "NONCOMMERCIAL_OR_NODERIVATIVES_CLAIM",
        "cc-by-nc-sa": "NONCOMMERCIAL_OR_NODERIVATIVES_CLAIM",
        "public-domain": "PUBLIC_DOMAIN_CLAIM",
        "other-oa": "OTHER_OA_CLAIM",
    }

    return categories.get(claim, "OTHER_LICENSE_CLAIM")


def load_records(path):
    records = []

    with Path(path).open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue

            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at line {line_no}: {exc}") from exc

            if not isinstance(row, dict):
                raise ValueError(f"Line {line_no} must contain a JSON object")

            records.append(row)

    if not records:
        raise ValueError("Input contains no records")

    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    records = load_records(args.input)

    categories = Counter()
    rights_status = Counter()
    access_status = Counter()

    output = Path(args.csv)
    output.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        "openalex_id",
        "doi",
        "title",
        "license_claims",
        "metadata_category",
        "original_rights_status",
        "full_text_access_status",
        "evidence_status",
        "approved_for_text_mining",
    ]

    with output.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()

        for row in records:
            claims = row.get("license_claims_openalex") or []
            category = classify_claims(claims)

            categories[category] += 1
            rights_status[row.get("license_rights_status", "missing")] += 1
            access_status[row.get("full_text_access_status", "missing")] += 1

            writer.writerow({
                "openalex_id": row.get("openalex_id") or row.get("id", ""),
                "doi": row.get("doi", ""),
                "title": row.get("title", ""),
                "license_claims": ";".join(claims),
                "metadata_category": category,
                "original_rights_status": row.get(
                    "license_rights_status", "missing"
                ),
                "full_text_access_status": row.get(
                    "full_text_access_status", "missing"
                ),
                "evidence_status": "UNVERIFIED_METADATA_ONLY",
                "approved_for_text_mining": "false",
            })

    report = {
        "record_count": len(records),
        "license_categories": dict(sorted(categories.items())),
        "original_rights_status": dict(sorted(rights_status.items())),
        "full_text_access_status": dict(sorted(access_status.items())),
        "unverified_evidence_count": len(records),
        "text_mining_approved_count": 0,
        "input_sha256": sha256_file(args.input),
        "classification_csv_sha256": sha256_file(output),
        "legal_clearance_performed": False,
        "warning": (
            "OpenAlex license claims are metadata only. "
            "This report does not establish legal permission, "
            "exact-version rights, or text-mining eligibility."
        ),
    }

    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()