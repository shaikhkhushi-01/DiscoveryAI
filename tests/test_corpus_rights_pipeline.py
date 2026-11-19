import tempfile,unittest
from pathlib import Path
from scripts.corpus.build_fulltext_rights_queue import build_row,read_jsonl
from scripts.corpus.acquire_approved_fulltext import approved,download_one

class RightsPipelineTests(unittest.TestCase):
    def test_queue_defaults_pending(self):
        row=build_row({"openalex_id":"W1","title":"Paper","license_claims_openalex":["cc-by"]})
        self.assertEqual(row["rights_status"],"PENDING_HUMAN_REVIEW")
        self.assertEqual(row["approved_for_text_mining"],"false")
    def test_approval_requires_evidence(self):
        row={"openalex_id":"W1","candidate_pdf_url":"https://example.org/a.pdf",
          "approved_for_text_mining":"true","reviewer_id":"r1","evidence_url":"https://example.org/license",
          "license_name":"CC BY","license_url":"https://creativecommons.org/licenses/by/4.0/"}
        self.assertTrue(approved(row)); row["evidence_url"]=""
        self.assertFalse(approved(row))
    def test_non_https_blocked(self):
        self.assertEqual(download_one({"candidate_pdf_url":"http://example.org/a.pdf"},Path("."))["status"],"blocked_non_https")
    def test_jsonl_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"x.jsonl"; p.write_text('{"openalex_id":"W1"}\n',encoding="utf-8")
            self.assertEqual(len(read_jsonl(p)),1)
            p.write_text("{bad json}\n",encoding="utf-8")
            with self.assertRaises(ValueError): read_jsonl(p)
if __name__=="__main__": unittest.main()
