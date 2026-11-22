from __future__ import annotations

import json
import unittest
from unittest.mock import AsyncMock, patch

from app.services.evaluation import ablation_prediction_adapters as adapters


class _FakeProvider:
    def __init__(self, result):
        self.result = result

    async def structured(self, *args, **kwargs):
        return self.result


def _response():
    return {
        "gap_status": "supported",
        "ratings": {
            "novelty_within_corpus": 1, "relevance": 3,
            "feasibility": 2, "evidence_quality": 3,
        },
        "evidence": [{"evidence_index": 0, "stance": "supporting"}],
    }


def _record():
    return {"record_id": "r1", "research_question": "Does method X improve NLP evaluation?"}


def _hit():
    return {
        "paper_id": "p1", "document_id": "d1", "chunk_id": "c1",
        "text": "Evidence about method X.", "rerank_score": 0.8,
    }


class AblationPredictionAdapterTests(unittest.IsolatedAsyncioTestCase):
    async def test_each_variant_has_exactly_one_declared_component_removed(self):
        self.assertEqual(set(adapters.ABLATION_CONFIGS), {
            "full", "without_vector_retrieval", "without_graph_retrieval",
            "without_research_critic", "without_temporal_signals",
            "without_discovery_score",
        })
        for variant, switches in adapters.ABLATION_CONFIGS.items():
            disabled = [name for name, enabled in switches.items() if not enabled]
            expected = [] if variant == "full" else [variant.removeprefix("without_")]
            self.assertEqual(disabled, expected)

    async def test_without_vector_uses_graph_search_without_hybrid_retrieval(self):
        with patch.object(adapters, "graph_search", return_value=[_hit()]), \
             patch.object(adapters, "graph_expand", return_value=[]), \
             patch.object(adapters, "hybrid_search") as hybrid, \
             patch.object(adapters, "critique_research_gap", new_callable=AsyncMock, return_value={"verdict": "review"}), \
             patch.object(adapters, "topic_timeline", return_value=[]), \
             patch.object(adapters, "compute_discovery_score", return_value={"discovery_score": 70}), \
             patch.object(adapters, "get_llm_provider", return_value=_FakeProvider(_response())):
            result = await adapters.generate_ablation_prediction(
                _record(), adapters.AblationConfig.from_id("without_vector_retrieval")
            )
        hybrid.assert_not_called()
        self.assertEqual(result["evidence"][0]["paper_id"], "p1")

    async def test_without_graph_uses_vector_search_without_graph_pipeline(self):
        with patch.object(adapters, "hybrid_search", return_value=[_hit()]), \
             patch.object(adapters, "rerank", return_value=[_hit()]), \
             patch.object(adapters, "retrieve_graph_rag") as graph, \
             patch.object(adapters, "critique_research_gap", new_callable=AsyncMock, return_value={"verdict": "review"}), \
             patch.object(adapters, "topic_timeline", return_value=[]), \
             patch.object(adapters, "compute_discovery_score", return_value={"discovery_score": 70}), \
             patch.object(adapters, "get_llm_provider", return_value=_FakeProvider(_response())):
            result = await adapters.generate_ablation_prediction(
                _record(), adapters.AblationConfig.from_id("without_graph_retrieval")
            )
        graph.assert_not_called()
        self.assertEqual(result["evidence"][0]["paper_id"], "p1")

    async def test_component_removals_skip_the_disabled_calls(self):
        config = adapters.AblationConfig.from_id("without_research_critic")
        with patch.object(adapters, "retrieve_graph_rag", return_value={"items": [_hit()]}), \
             patch.object(adapters, "critique_research_gap", new_callable=AsyncMock) as critic, \
             patch.object(adapters, "topic_timeline", return_value=[]), \
             patch.object(adapters, "compute_discovery_score", return_value={"discovery_score": 70}), \
             patch.object(adapters, "get_llm_provider", return_value=_FakeProvider(_response())):
            await adapters.generate_ablation_prediction(_record(), config)
        critic.assert_not_awaited()

    async def test_temporal_and_score_ablation_skip_only_their_component_calls(self):
        for variant, disabled in (
            ("without_temporal_signals", "topic_timeline"),
            ("without_discovery_score", "compute_discovery_score"),
        ):
            config = adapters.AblationConfig.from_id(variant)
            with patch.object(adapters, "retrieve_graph_rag", return_value={"items": [_hit()]}), \
                 patch.object(adapters, "critique_research_gap", new_callable=AsyncMock, return_value={"verdict": "review"}), \
                 patch.object(adapters, "topic_timeline", return_value=[]) as temporal, \
                 patch.object(adapters, "compute_discovery_score", return_value={"discovery_score": 70}) as score, \
                 patch.object(adapters, "get_llm_provider", return_value=_FakeProvider(_response())):
                await adapters.generate_ablation_prediction(_record(), config)
            (temporal if disabled == "topic_timeline" else score).assert_not_called()

    async def test_no_adjudicated_records_fails_closed_before_writing(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as directory:
            benchmark = Path(directory) / "benchmark.json"
            benchmark.write_text(json.dumps({
                "benchmark_version": "v1",
                "records": [{
                    "record_id": "r1", "split": "test",
                    "corpus_snapshot": {"corpus_id": "corpus-1"},
                    "annotations": {"adjudication_status": "pending"},
                }],
            }), encoding="utf-8")
            output = Path(directory) / "outputs"
            with self.assertRaisesRegex(ValueError, "no adjudicated records"):
                await adapters.generate_ablation_predictions(
                    benchmark, output, code_revision="abc",
                    model_provider="test", model_name="test",
                )
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
