import json
import tempfile
import unittest
from pathlib import Path
from scripts.corpus.validate_nlp_annotations import load_records, validate_pairs, cohen_kappa

def record(reviewer, **updates):
    row = {
        "paper_id":"W1","version_id":"v1","reviewer_id":reviewer,
        "annotated_at_utc":"2026-11-20T10:00:00Z",
        "nlp_relevance":"IN_SCOPE","primary_category":"MODEL_METHOD",
        "contribution_type":"METHOD","research_question":"How does method X work?",
        "claimed_contribution":"Introduces method X.","evidence_locators":["p. 2","sec. 3"],
        "reproducibility":["NOT_REPORTED"],"confidence":"MEDIUM"
    }
    row.update(updates)
    return row

class AnnotationProtocolTests(unittest.TestCase):
    def test_valid_two_reviewer_pair(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"annotations.jsonl"
            path.write_text("\n".join(json.dumps(x) for x in [record("A"),record("B")]),encoding="utf-8")
            grouped,incomplete=validate_pairs(load_records(path))
            self.assertEqual(len(grouped),1)
            self.assertEqual(incomplete,[])
    def test_same_reviewer_cannot_form_pair(self):
        _,incomplete=validate_pairs([record("A"),record("B",reviewer_id="A",claimed_contribution="Different")])
        self.assertEqual(len(incomplete),1)
    def test_missing_evidence_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"bad.jsonl"
            path.write_text(json.dumps(record("A",evidence_locators=[])),encoding="utf-8")
            with self.assertRaises(ValueError):
                load_records(path)
    def test_duplicate_reviewer_record_rejected(self):
        with self.assertRaises(ValueError):
            validate_pairs([record("A"),record("A",claimed_contribution="Duplicate")])
    def test_kappa_constant_perfect_agreement_undefined(self):
        self.assertIsNone(cohen_kappa([("IN_SCOPE","IN_SCOPE")]))

if __name__=="__main__":
    unittest.main()
