import asyncio
from unittest.mock import AsyncMock, patch


def _hits():
    return [
        {"paper_id": 1, "document_id": 11, "chunk_id": 101, "title": "Paper A", "section": "Methods", "text": "A study of neural retrieval."},
        {"paper_id": 2, "document_id": 22, "chunk_id": 202, "title": "Paper B", "section": "Results", "text": "A study of retrieval robustness."},
        {"paper_id": 3, "document_id": 33, "chunk_id": 303, "title": "Paper C", "section": "Discussion", "text": "A study of domain adaptation."},
    ]


def test_prepare_sources_deduplicates_chunks_and_limits_per_paper():
    from app.services.research_engine import _prepare_sources

    hits = [
        {"paper_id": 1, "document_id": 1, "chunk_id": 1, "text": "first"},
        {"paper_id": 1, "document_id": 1, "chunk_id": 1, "text": "duplicate"},
        {"paper_id": 1, "document_id": 1, "chunk_id": 2, "text": "second"},
        {"paper_id": 1, "document_id": 1, "chunk_id": 3, "text": "third"},
        {"paper_id": 2, "document_id": 2, "chunk_id": 4, "text": "other paper"},
    ]
    sources, selected = _prepare_sources(hits, 10)
    assert len(sources) == 3
    assert len(selected) == 3
    assert [item["evidence_id"] for item in sources] == ["EVIDENCE 1", "EVIDENCE 2", "EVIDENCE 3"]


def test_research_engine_fails_closed_with_fewer_than_two_papers():
    from app.services.research_engine import analyze_research_query

    with patch("app.services.research_engine.retrieve_graph_rag", return_value={"items": _hits()[:1]}):
        result = asyncio.run(analyze_research_query("neural retrieval"))
    assert result["status"] == "insufficient_evidence"
    assert result["research_gaps"] == []
    assert result["hypotheses"] == []


def test_research_engine_filters_unknown_and_single_paper_gap_citations():
    from app.services.research_engine import analyze_research_query

    llm_result = {
        "executive_summary": "Retrieved papers study retrieval and robustness.",
        "themes": [{"theme": "retrieval", "synthesis": "Both papers discuss retrieval.", "evidence_ids": ["EVIDENCE 1"]}],
        "research_gaps": [
            {"title": "Unsupported", "rationale": "Only one paper.", "evidence_ids": ["EVIDENCE 1"]},
            {"title": "Potential robustness gap", "rationale": "Two papers leave an evaluation question.", "evidence_ids": ["EVIDENCE 1", "EVIDENCE 2", "EVIDENCE 999"]},
        ],
        "hypotheses": [
            {"statement": "H1", "rationale": "Motivated by two papers.", "experiment": "Compare methods.", "possible_measurements": ["F1"], "evidence_ids": ["EVIDENCE 1", "EVIDENCE 2"]}
        ],
        "disagreements": [],
        "limitations": ["Only a small retrieved sample was inspected."],
    }
    provider = AsyncMock()
    provider.structured.return_value = llm_result
    critic = AsyncMock(return_value={
        "verdict": "review", "rationale": "Evidence is related but inconclusive.",
        "evidence_ids": ["EVIDENCE 1"], "distinct_paper_count": 3,
    })
    with patch("app.services.research_engine.retrieve_graph_rag", return_value={"items": _hits()}), \
         patch("app.services.research_engine.get_llm_provider", return_value=provider), \
         patch("app.services.research_engine.critique_research_gap", critic):
        result = asyncio.run(analyze_research_query("neural retrieval"))

    assert result["status"] == "completed"
    assert len(result["research_gaps"]) == 1
    assert result["research_gaps"][0]["evidence_ids"] == ["EVIDENCE 1", "EVIDENCE 2"]
    assert result["research_gaps"][0]["status"] == "needs_review"
    assert result["hypotheses"][0]["possible_measurements"] == ["F1"]
    assert result["hypotheses"][0]["evidence_ids"] == ["EVIDENCE 1", "EVIDENCE 2"]


def test_research_engine_returns_retrieval_provenance_and_disclaimers():
    from app.services.research_engine import analyze_research_query

    with patch("app.services.research_engine.retrieve_graph_rag", return_value={"items": _hits()}):
        result = asyncio.run(analyze_research_query("neural retrieval"))
    assert result["scope"] == "indexed_corpus"
    assert result["distinct_paper_count"] == 3
    assert result["retrieved_source_count"] == 3
    assert len(result["sources"]) == 3
    assert "not proof of global novelty" in result["limitations"][1]



def test_research_engine_maps_critic_sources_to_original_evidence_ids():
    from app.services.research_engine import analyze_research_query

    llm_result = {
        "executive_summary": "Cross-paper summary.",
        "themes": [],
        "research_gaps": [{"title": "Candidate", "rationale": "Two-paper rationale.", "evidence_ids": ["EVIDENCE 1", "EVIDENCE 2"]}],
        "hypotheses": [],
        "disagreements": [],
        "limitations": [],
    }
    provider = AsyncMock()
    provider.structured.return_value = llm_result
    critic = AsyncMock(return_value={
        "verdict": "accept",
        "rationale": "Critic found a directly relevant passage.",
        "distinct_paper_count": 2,
        "sources": [
            {"paper_id": 2, "document_id": 22, "chunk_id": 202},
            {"paper_id": 3, "document_id": 33, "chunk_id": 303},
        ],
    })
    with patch("app.services.research_engine.retrieve_graph_rag", return_value={"items": _hits()}), \
         patch("app.services.research_engine.get_llm_provider", return_value=provider), \
         patch("app.services.research_engine.critique_research_gap", critic):
        result = asyncio.run(analyze_research_query("neural retrieval"))

    candidate = result["research_gaps"][0]
    assert candidate["critic"]["evidence_ids"] == ["EVIDENCE 2", "EVIDENCE 3"]
    assert candidate["critic"]["distinct_paper_count"] == 2
    assert candidate["status"] == "critic_supported_candidate"
