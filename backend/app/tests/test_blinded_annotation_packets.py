from __future__ import annotations

import unittest

from scripts.evaluation.export_blinded_annotation_packets import build_blinded_packets


class BlindedPacketTests(unittest.TestCase):
    def setUp(self):
        self.benchmark = {
            "benchmark_id": "pilot",
            "benchmark_version": "1.0",
            "annotation_rubric_version": "1.0",
            "records": [{
                "record_id": "private-source-record-123",
                "research_question": "Does method X improve outcome Y?",
                "corpus_snapshot": {
                    "corpus_id": "corpus-1",
                    "snapshot_date": "2026-01-01",
                    "scope_statement": "A bounded test corpus.",
                    "paper_ids": ["paper-1"],
                },
                "candidate_gap": {
                    "candidate_id": "candidate-1",
                    "title": "Potential evaluation gap",
                    "description": "The description shown to reviewers.",
                    "gap_type": "evaluation",
                },
                "gold_evidence": {
                    "supporting": [{"paper_id": "paper-1", "document_id": "d1", "chunk_id": "c1",
                                    "relevance": 3, "rationale": "gold rationale secret"}],
                    "contradictory": [],
                },
                "gold_assessment": {
                    "gap_status": "supported", "novelty_within_corpus": 2,
                    "relevance": 3, "feasibility": 2, "evidence_quality": 3,
                },
                "annotations": {
                    "annotator_ids": ["prior-a", "prior-b"], "annotated_at": "2026-01-02",
                    "adjudication_status": "adjudicated", "adjudication_notes": "private adjudication",
                },
                "split": "train",
            }],
        }

    def test_packet_excludes_gold_labels_and_source_ids(self):
        packet, crosswalk = build_blinded_packets(self.benchmark, salt="fixed-salt")
        rendered = str(packet)
        for secret in ("private-source-record-123", "gold rationale secret",
                       "private adjudication", "supported", "prior-a"):
            self.assertNotIn(secret, rendered)
        self.assertEqual(crosswalk["blind_to_source_record_id"], {
            packet["records"][0]["blind_record_id"]: "private-source-record-123"
        })
        self.assertIsNone(packet["records"][0]["review_form"]["gap_status"])

    def test_default_packet_hides_paper_ids(self):
        packet, _ = build_blinded_packets(self.benchmark, salt="fixed-salt")
        self.assertNotIn("paper_ids", packet["records"][0]["corpus_snapshot"])

    def test_optional_paper_ids(self):
        packet, _ = build_blinded_packets(self.benchmark, include_paper_ids=True, salt="fixed-salt")
        self.assertEqual(packet["records"][0]["corpus_snapshot"]["paper_ids"], ["paper-1"])


if __name__ == "__main__":
    unittest.main()
