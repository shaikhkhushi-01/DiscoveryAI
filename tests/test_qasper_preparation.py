from __future__ import annotations

import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

from scripts.benchmarks.prepare_qasper import (
    normalize_paper,
    read_json_from_tar,
    sha256_bytes,
    write_jsonl,
)


class QasperPreparationTests(unittest.TestCase):
    def sample_paper(self):
        return {
            "id": "2101.00001",
            "title": "A Paper About NLP",
            "abstract": "An abstract.",
            "full_text": {
                "section_name": ["Introduction", "Method"],
                "paragraphs": [["First paragraph.", "Second paragraph."], ["A method paragraph."]],
            },
            "qas": [{
                "question": "What is proposed?",
                "question_id": "q1",
                "answers": [{
                    "annotation_id": "ann1",
                    "answer": {
                        "unanswerable": False,
                        "extractive_spans": ["A method."],
                        "yes_no": None,
                        "free_form_answer": "A method is proposed.",
                        "evidence": ["A method paragraph."],
                        "highlighted_evidence": [],
                    },
                }],
            }, {
                "question": "Can this be answered?",
                "question_id": "q2",
                "answers": [{
                    "annotation_id": "ann2",
                    "answer": {
                        "unanswerable": True,
                        "extractive_spans": [],
                        "yes_no": None,
                        "free_form_answer": "",
                        "evidence": [],
                        "highlighted_evidence": [],
                    },
                }],
            }],
        }

    def test_normalization_keeps_gold_separate_from_query(self):
        paper, chunks, queries, references = normalize_paper("train", "2101.00001", self.sample_paper())
        self.assertEqual(paper["paper_id"], "2101.00001")
        self.assertEqual(len(chunks), 4)  # abstract + three body paragraphs
        self.assertEqual(len(queries), 2)
        self.assertNotIn("answers", queries[0])
        self.assertNotIn("evidence", queries[0])
        self.assertEqual(references[0]["answers"][0]["evidence"], ["A method paragraph."])
        self.assertTrue(references[0]["labels_available"])

    def test_malformed_answer_annotations_rejected(self):
        paper = self.sample_paper()
        paper["qas"][0]["answers"] = "not-a-list"
        with self.assertRaisesRegex(ValueError, "answers must be a list"):
            normalize_paper("train", "2101.00001", paper)

    def test_tar_reader_reads_expected_json_and_rejects_missing_member(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.tgz"
            payload = json.dumps({"paper-1": self.sample_paper()}).encode()
            with tarfile.open(path, "w:gz") as archive:
                info = tarfile.TarInfo("folder/fixture.json")
                info.size = len(payload)
                archive.addfile(info, io.BytesIO(payload))
            parsed = read_json_from_tar(path, "fixture.json")
            self.assertIn("paper-1", parsed)
            with self.assertRaisesRegex(ValueError, "Expected exactly one"):
                read_json_from_tar(path, "missing.json")

    def test_tar_reader_rejects_non_regular_member(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.tgz"
            with tarfile.open(path, "w:gz") as archive:
                info = tarfile.TarInfo("fixture.json")
                info.type = tarfile.SYMTYPE
                info.linkname = "../../outside"
                archive.addfile(info)
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                read_json_from_tar(path, "fixture.json")

    def test_jsonl_writer_is_parseable(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "records.jsonl"
            write_jsonl(path, [{"id": "a"}, {"id": "b"}])
            rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual([row["id"] for row in rows], ["a", "b"])

    def test_sha256_helper(self):
        self.assertEqual(
            sha256_bytes(b"abc"),
            "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        )


if __name__ == "__main__":
    unittest.main()
