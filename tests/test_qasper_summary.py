from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.benchmarks.build_qasper_summary import build_summary


class QasperSummaryTests(unittest.TestCase):
    def test_summary_contains_aggregate_metrics_and_hashes_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({"dataset": "allenai/qasper", "dataset_version": "0.3.0"}), encoding="utf-8")
            import hashlib
            manifest_hash = hashlib.sha256(manifest.read_bytes()).hexdigest()
            entries = {}
            for name, answer_f1, evidence_f1 in (("abstract_only", 0.1, 0.2), ("full_text", 0.3, 0.4)):
                report = root / f"{name}.json"
                metadata = root / f"{name}.jsonl.metadata.json"
                report.write_text(json.dumps({
                    "questions_scored": 5, "predictions_received": 5,
                    "missing_predictions": 0, "extra_predictions_ignored": 0,
                    "answer_f1": answer_f1, "evidence_f1": evidence_f1,
                    "answer_f1_by_type": {"extractive": answer_f1},
                }), encoding="utf-8")
                metadata.write_text(json.dumps({
                    "split": "validation", "mode": "extractive", "context_scope": name,
                    "questions_generated": 5, "code_revision": "abc123",
                    "query_file_sha256": "a" * 64, "chunk_file_sha256": "b" * 64,
                    "manifest_sha256": manifest_hash, "gold_references_loaded": False,
                }), encoding="utf-8")
                entries[name] = (report, metadata)
            summary = build_summary(manifest, entries)
            self.assertEqual(summary["systems"]["full_text"]["answer_f1"], 0.3)
            rendered = json.dumps(summary)
            self.assertNotIn("predicted_answer", rendered)
            self.assertNotIn("paragraph text", rendered)
            self.assertEqual(len(summary["manifest_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
