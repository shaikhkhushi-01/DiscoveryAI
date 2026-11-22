from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.benchmarks.generate_qasper_predictions import (
    extractive_prediction,
    generate,
    retrieve_paragraphs,
)


class QasperPredictionRunnerTests(unittest.TestCase):
    def test_retrieval_prefers_query_relevant_paragraph(self):
        chunks = [
            {"chunk_id": "c1", "text": "We introduce a neural retrieval model for scientific papers."},
            {"chunk_id": "c2", "text": "The weather was sunny during the conference."},
        ]
        ranked = retrieve_paragraphs("neural retrieval model", chunks, top_k=2)
        self.assertEqual(ranked[0]["chunk_id"], "c1")


    def test_abstract_only_scope_excludes_body_paragraphs(self):
        chunks = [
            {"chunk_id": "abstract", "section_name": "Abstract", "text": "neural retrieval method"},
            {"chunk_id": "body", "section_name": "Method", "text": "neural retrieval method"},
        ]
        ranked = retrieve_paragraphs("neural retrieval", chunks, top_k=5, context_scope="abstract_only")
        self.assertEqual([row["chunk_id"] for row in ranked], ["abstract"])

    def test_extractive_prediction_cites_selected_paragraphs(self):
        query = {"query_id": "q1", "question": "What retrieval model is proposed?"}
        chunks = [
            {"chunk_id": "c1", "text": "We propose a dense retrieval model."},
            {"chunk_id": "c2", "text": "Experiments use three datasets."},
        ]
        result = extractive_prediction(query, chunks, top_k=1)
        self.assertEqual(result["question_id"], "q1")
        self.assertEqual(result["predicted_answer"], "We propose a dense retrieval model.")
        self.assertEqual(result["predicted_evidence"], ["We propose a dense retrieval model."])

    def test_no_matching_paragraph_returns_unanswerable(self):
        result = extractive_prediction(
            {"query_id": "q2", "question": "quantum chromodynamics"},
            [{"text": "This paper studies neural machine translation."}],
        )
        self.assertEqual(result["predicted_answer"], "Unanswerable")
        self.assertEqual(result["predicted_evidence"], [])

    def test_generation_never_allows_test_split(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(ValueError, "Test split is locked"):
                import asyncio
                asyncio.run(generate(root, root / "out.jsonl", split="test", mode="extractive",
                                     top_k=5, max_questions=None, code_revision="test"))

    def test_generate_extractive_keeps_gold_out_of_prediction_and_writes_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            normalized = root / "normalized"
            for name in ("queries", "chunks"):
                (normalized / name).mkdir(parents=True)
            (normalized / "queries" / "validation.jsonl").write_text(
                json.dumps({
                    "query_id": "q1", "paper_id": "p1", "question": "What model is proposed?",
                    "paper_title": "Paper", "paper_abstract": "Abstract",
                }) + "\n", encoding="utf-8"
            )
            (normalized / "chunks" / "validation.jsonl").write_text(
                json.dumps({"paper_id": "p1", "chunk_id": "c1",
                            "text": "We propose a dense neural retrieval model."}) + "\n",
                encoding="utf-8",
            )
            (normalized / "manifest.json").write_text(
                json.dumps({"dataset": "allenai/qasper", "dataset_version": "0.3.0"}),
                encoding="utf-8",
            )
            import asyncio
            output = root / "predictions" / "validation.jsonl"
            report = asyncio.run(generate(
                root, output, split="validation", mode="extractive", top_k=3,
                max_questions=None, code_revision="test-revision",
            ))
            prediction = json.loads(output.read_text(encoding="utf-8").strip())
            self.assertEqual(prediction["question_id"], "q1")
            self.assertNotIn("gold", prediction)
            self.assertFalse(report["gold_references_loaded"])
            self.assertFalse(report["test_split_used"])
            self.assertEqual(report["questions_generated"], 1)
            metadata = json.loads(Path(report["metadata_file"]).read_text(encoding="utf-8"))
            self.assertEqual(len(metadata["query_file_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
