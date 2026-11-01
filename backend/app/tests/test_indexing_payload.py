import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.services.indexing import _load_payload, _index_vectors, _is_job_fresh, STALE_JOB_SECONDS


class IndexingPayloadTests(unittest.TestCase):
    def test_falls_back_to_extracted_text_when_parser_found_no_sections(self):
        document = SimpleNamespace(
            id=7,
            paper_id=12,
            paper=None,
            extracted_text="A" * 2500,
            metadata_json='{"extraction":{"topics":["AI"],"datasets":[]}}',
        )

        extraction, chunks = _load_payload(document)

        self.assertEqual(extraction["title"], "Document 7")
        self.assertEqual(len(chunks), 3)
        self.assertTrue(all(chunk["section"] == "full_text" for chunk in chunks))
        self.assertEqual(chunks[0]["document_id"], 7)
        self.assertEqual(chunks[0]["paper_id"], 12)
        self.assertEqual(chunks[0]["topics"], ["AI"])
        self.assertEqual(chunks[0]["text"], "A" * 1200)
        self.assertEqual(chunks[1]["text"][:150], "A" * 150)

    def test_rejects_empty_chunks_instead_of_reporting_zero_as_success(self):
        with self.assertRaisesRegex(ValueError, "No indexable text chunks"):
            _index_vectors([])

    def test_running_job_is_fresh_before_timeout(self):
        now = datetime.now(timezone.utc)
        job = SimpleNamespace(updated_at=now - timedelta(seconds=STALE_JOB_SECONDS - 1))
        self.assertTrue(_is_job_fresh(job, now))

    def test_running_job_is_stale_after_timeout(self):
        now = datetime.now(timezone.utc)
        job = SimpleNamespace(updated_at=now - timedelta(seconds=STALE_JOB_SECONDS + 1))
        self.assertFalse(_is_job_fresh(job, now))


if __name__ == "__main__":
    unittest.main()
