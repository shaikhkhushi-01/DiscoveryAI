from __future__ import annotations

import unittest
from unittest.mock import AsyncMock, patch

from app.services.evaluation import prediction_adapters as adapters


class _FakeProvider:
    def __init__(self, result):
        self.result = result

    async def structured(self, *args, **kwargs):
        return self.result


class PredictionAdapterTests(unittest.IsolatedAsyncioTestCase):
    async def test_prediction_attaches_only_allowlisted_retrieved_evidence(self):
        record = {"record_id": "r1", "research_question": "Does method X improve NLP evaluation?"}
        retrieved = [{
            "paper_id": "p1", "document_id": "d1", "chunk_id": "c1",
            "text": "Reported evidence for method X.",
        }]
        response = {
            "gap_status": "supported",
            "ratings": {
                "novelty_within_corpus": 1, "relevance": 3,
                "feasibility": 2, "evidence_quality": 3,
            },
            "evidence": [{"evidence_index": 0, "stance": "supporting"}],
        }
        with patch.dict(adapters.RETRIEVERS, {"vector_rag": AsyncMock(return_value=retrieved)}), \
             patch.object(adapters, "get_llm_provider", return_value=_FakeProvider(response)):
            result = await adapters.generate_prediction("vector_rag", record)
        self.assertEqual(result["record_id"], "r1")
        self.assertEqual(result["evidence"], [{
            "paper_id": "p1", "document_id": "d1", "chunk_id": "c1",
            "stance": "supporting",
        }])

    async def test_model_cannot_cite_out_of_range_evidence(self):
        record = {"record_id": "r2", "research_question": "A research question"}
        response = {
            "gap_status": "inconclusive",
            "ratings": {
                "novelty_within_corpus": 0, "relevance": 0,
                "feasibility": 0, "evidence_quality": 0,
            },
            "evidence": [{"evidence_index": 0, "stance": "supporting"}],
        }
        with patch.dict(adapters.RETRIEVERS, {"llm_only": AsyncMock(return_value=[])}), \
             patch.object(adapters, "get_llm_provider", return_value=_FakeProvider(response)):
            with self.assertRaisesRegex(ValueError, "outside supplied evidence"):
                await adapters.generate_prediction("llm_only", record)

    async def test_invalid_model_rating_is_rejected(self):
        record = {"record_id": "r3", "research_question": "A research question"}
        response = {
            "gap_status": "inconclusive",
            "ratings": {
                "novelty_within_corpus": True, "relevance": 0,
                "feasibility": 0, "evidence_quality": 0,
            },
            "evidence": [],
        }
        with patch.dict(adapters.RETRIEVERS, {"llm_only": AsyncMock(return_value=[])}), \
             patch.object(adapters, "get_llm_provider", return_value=_FakeProvider(response)):
            with self.assertRaisesRegex(ValueError, "integer 0..3"):
                await adapters.generate_prediction("llm_only", record)

    async def test_unknown_system_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsupported system_id"):
            await adapters.generate_prediction("unknown", {
                "record_id": "r4", "research_question": "A research question"
            })

    async def test_all_five_systems_dispatch_through_their_named_retriever(self):
        record = {"record_id": "dispatch-1", "research_question": "How are NLP models evaluated?"}
        response = {
            "gap_status": "inconclusive",
            "ratings": {
                "novelty_within_corpus": 0, "relevance": 0,
                "feasibility": 0, "evidence_quality": 0,
            },
            "evidence": [],
        }
        for system_id in adapters.SYSTEMS:
            retriever = AsyncMock(return_value=[])
            with self.subTest(system_id=system_id), \
                 patch.dict(adapters.RETRIEVERS, {system_id: retriever}), \
                 patch.object(adapters, "get_llm_provider", return_value=_FakeProvider(response)):
                result = await adapters.generate_prediction(system_id, record)
            retriever.assert_awaited_once_with(record["research_question"], adapters.MAX_EVIDENCE)
            self.assertEqual(result["record_id"], record["record_id"])
            self.assertEqual(result["evidence"], [])

    async def test_records_without_text_are_not_sent_as_retrieved_evidence(self):
        record = {"record_id": "empty-text", "research_question": "A research question"}
        retrieved = [
            {"paper_id": "p1", "document_id": "d1", "chunk_id": "c1", "text": "   "},
            {"paper_id": "p2", "document_id": "d2", "chunk_id": "c2", "text": "Useful excerpt"},
        ]
        response = {
            "gap_status": "supported",
            "ratings": {
                "novelty_within_corpus": 1, "relevance": 2,
                "feasibility": 2, "evidence_quality": 2,
            },
            "evidence": [{"evidence_index": 0, "stance": "supporting"}],
        }
        with patch.dict(adapters.RETRIEVERS, {"vector_rag": AsyncMock(return_value=retrieved)}), \
             patch.object(adapters, "get_llm_provider", return_value=_FakeProvider(response)) as provider_factory:
            result = await adapters.generate_prediction("vector_rag", record)
        self.assertEqual(result["evidence"], [{
            "paper_id": "p2", "document_id": "d2", "chunk_id": "c2",
            "stance": "supporting",
        }])
        provider_factory.return_value.structured.assert_awaited_once()
        prompt = provider_factory.return_value.structured.await_args.args[0]
        self.assertNotIn('"paper_id": "p1"', prompt)
        self.assertIn("Useful excerpt", prompt)

    async def test_non_object_structured_response_is_rejected(self):
        record = {"record_id": "bad-shape", "research_question": "A research question"}
        with patch.dict(adapters.RETRIEVERS, {"llm_only": AsyncMock(return_value=[])}), \
             patch.object(adapters, "get_llm_provider", return_value=_FakeProvider([])):
            with self.assertRaisesRegex(ValueError, "must be an object"):
                await adapters.generate_prediction("llm_only", record)

    async def test_empty_retrieval_forces_inconclusive_zero_ratings(self):
        record = {"record_id": "no-evidence", "research_question": "A research question"}
        response = {
            "gap_status": "supported",
            "ratings": {
                "novelty_within_corpus": 3, "relevance": 3,
                "feasibility": 3, "evidence_quality": 3,
            },
            "evidence": [],
        }
        with patch.dict(adapters.RETRIEVERS, {"vector_rag": AsyncMock(return_value=[])}), \
             patch.object(adapters, "get_llm_provider", return_value=_FakeProvider(response)):
            result = await adapters.generate_prediction("vector_rag", record)
        self.assertEqual(result["gap_status"], "inconclusive")
        self.assertEqual(result["ratings"], {field: 0 for field in adapters.RATING_FIELDS})
        self.assertEqual(result["evidence"], [])


if __name__ == "__main__":
    unittest.main()
