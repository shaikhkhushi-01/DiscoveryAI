from unittest.mock import patch

import pytest

from app.services import research_synthesis


@pytest.mark.asyncio
async def test_comparison_requires_two_distinct_papers():
    with patch.object(research_synthesis, "hybrid_search", return_value=[
        {"paper_id": 7, "text": "Evidence from one paper.", "score": 0.9}
    ]), patch.object(research_synthesis, "rerank", side_effect=lambda q, items, limit: items):
        result = await research_synthesis.synthesize_research(
            "Compare approaches to machine translation", mode="comparison", limit=8
        )

    assert result["paper_count"] == 1
    assert result["sources"] == []
    assert "at least two distinct papers" in result["answer"]
    assert result["scope"] == "indexed_corpus"


@pytest.mark.asyncio
async def test_empty_corpus_returns_explicit_limitation():
    with patch.object(research_synthesis, "hybrid_search", return_value=[]):
        result = await research_synthesis.synthesize_research(
            "Summarize research on attention mechanisms", mode="literature_review"
        )

    assert result["sources"] == []
    assert result["citations"] == []
    assert result["limitations"]


@pytest.mark.asyncio
async def test_synthesis_validates_citations_and_returns_source_metadata():
    class FakeProvider:
        async def structured(self, prompt, *, system, temperature):
            return {
                "answer": "Paper finding [EVIDENCE 1].",
                "sections": [{
                    "heading": "Findings",
                    "content": "Reported result [EVIDENCE 1].",
                    "evidence_ids": ["EVIDENCE 1", "EVIDENCE 999"],
                }],
                "comparisons": [{
                    "dimension": "Method",
                    "findings": "Different methods [EVIDENCE 1].",
                    "evidence_ids": ["EVIDENCE 1"],
                }],
                "citations": ["EVIDENCE 1", "EVIDENCE 999"],
                "limitations": ["Only one source was retrieved."],
            }

    item = {
        "paper_id": 11, "document_id": 4, "chunk_id": "chunk-a",
        "title": "Attention Study", "section": "Abstract",
        "text": "The paper reports an attention-based method.", "score": 0.91,
    }
    with patch.object(research_synthesis, "hybrid_search", return_value=[item]), \
         patch.object(research_synthesis, "rerank", side_effect=lambda q, items, limit: items), \
         patch.object(research_synthesis, "get_llm_provider", return_value=FakeProvider()):
        result = await research_synthesis.synthesize_research(
            "Review attention-based methods", mode="literature_review", limit=8
        )

    assert result["citations"] == ["EVIDENCE 1"]
    assert result["sections"][0]["evidence_ids"] == ["EVIDENCE 1"]
    assert result["sources"][0]["paper_id"] == 11
    assert result["sources"][0]["chunk_id"] == "chunk-a"



@pytest.mark.asyncio
async def test_synthesis_removes_fabricated_inline_evidence_markers():
    class FakeProvider:
        async def structured(self, prompt, *, system, temperature):
            return {
                "answer": "Supported claim [EVIDENCE 1]. Unsupported claim [EVIDENCE 999].",
                "sections": [{
                    "heading": "Findings",
                    "content": "Supported [EVIDENCE 1]; fabricated [EVIDENCE 999].",
                    "evidence_ids": ["EVIDENCE 1"],
                }],
                "comparisons": [],
                "citations": ["EVIDENCE 1"],
                "limitations": [],
            }

    item = {
        "paper_id": 21, "document_id": 8, "chunk_id": "chunk-1",
        "title": "A Study", "section": "Results",
        "text": "The study reports a measured result.", "score": 0.8,
    }
    with (
        patch.object(research_synthesis, "hybrid_search", return_value=[item]),
        patch.object(research_synthesis, "rerank", side_effect=lambda q, items, limit: items),
        patch.object(research_synthesis, "get_llm_provider", return_value=FakeProvider()),
    ):
        result = await research_synthesis.synthesize_research(
            "Summarize measured results", mode="literature_review", limit=5
        )

    assert "[EVIDENCE 1]" in result["answer"]
    assert "[EVIDENCE 999]" not in result["answer"]
    assert "[EVIDENCE 999]" not in result["sections"][0]["content"]
