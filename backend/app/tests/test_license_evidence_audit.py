import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "corpus" / "license_evidence_audit.py"

spec = importlib.util.spec_from_file_location("license_audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


@pytest.mark.parametrize(
    "claims,expected",
    [
        ([], "NO_LICENSE_CLAIM"),
        (["cc-by"], "CC_BY_CLAIM_ONLY"),
        (["cc-by-sa"], "CC_BY_SA_CLAIM_ONLY"),
        (["cc-by-nc"], "NONCOMMERCIAL_OR_NODERIVATIVES_CLAIM"),
        (["cc-by-nc-nd"], "NONCOMMERCIAL_OR_NODERIVATIVES_CLAIM"),
        (["public-domain"], "PUBLIC_DOMAIN_CLAIM"),
        (["other-oa"], "OTHER_OA_CLAIM"),
        (["cc-by", "cc-by-sa"], "MULTIPLE_OR_MIXED_CLAIMS"),
        (["unknown-license"], "OTHER_LICENSE_CLAIM"),
    ],
)
def test_classify_claims(claims, expected):
    assert audit.classify_claims(claims) == expected


def test_duplicate_claims_are_deduplicated():
    assert audit.classify_claims(["cc-by", "cc-by"]) == "CC_BY_CLAIM_ONLY"


def test_invalid_claims_type_is_rejected():
    with pytest.raises(ValueError):
        audit.classify_claims("cc-by")


def test_load_records_reads_jsonl(tmp_path):
    source = tmp_path / "input.jsonl"
    source.write_text(
        json.dumps({"id": "W123"}) + "\n",
        encoding="utf-8",
    )

    assert audit.load_records(source) == [{"id": "W123"}]


def test_load_records_rejects_invalid_json(tmp_path):
    source = tmp_path / "invalid.jsonl"
    source.write_text("{invalid json}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid JSON"):
        audit.load_records(source)


def test_load_records_rejects_non_object(tmp_path):
    source = tmp_path / "invalid.jsonl"
    source.write_text('"not an object"\n', encoding="utf-8")

    with pytest.raises(ValueError, match="JSON object"):
        audit.load_records(source)


def test_load_records_rejects_empty_file(tmp_path):
    source = tmp_path / "empty.jsonl"
    source.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="no records"):
        audit.load_records(source)


def test_sha256_file_is_deterministic(tmp_path):
    source = tmp_path / "sample.txt"
    source.write_text("DiscoveryAI", encoding="utf-8")

    assert audit.sha256_file(source) == audit.sha256_file(source)