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


if __name__ == "__main__":
    unittest.main()
