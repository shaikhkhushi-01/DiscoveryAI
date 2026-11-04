import pytest

from app.services.gap_detection import research_critic


def hits():
    return [
        {"paper_id": 1, "document_id": 10, "title": "Paper A", "text": "Relevant context A"},
        {"paper_id": 2, "document_id": 20, "title": "Paper B", "text": "Relevant context B"},
    ]


@pytest.mark.asyncio
async def test_critic_requires_multiple_distinct_papers(monkeypatch):
    monkeypatch.setattr(research_critic, "retrieve_graph_rag", lambda *a, **k: {"items": hits()[:1]})
    result = await research_critic.critique_research_gap("A possible gap")
    assert result["verdict"] == "review"
    assert result["distinct_paper_count"] == 1


@pytest.mark.asyncio
async def test_critic_filters_unknown_evidence_ids(monkeypatch):
    class FakeLLM:
        async def structured(self, *args, **kwargs):
            return {
                "verdict": "accept",
                "rationale": "Plausible within corpus.",
                "evidence_ids": ["EVIDENCE 1", "EVIDENCE 99"],
                "checks": ["Evidence reviewed."],
                "limitations": [],
            }

    monkeypatch.setattr(research_critic, "retrieve_graph_rag", lambda *a, **k: {"items": hits()})
    monkeypatch.setattr(research_critic, "get_llm_provider", lambda: FakeLLM())
    result = await research_critic.critique_research_gap("A possible gap")
    assert result["verdict"] == "accept"
    assert result["evidence_ids"] == ["EVIDENCE 1"]
    assert result["scope"] == "indexed_corpus"


@pytest.mark.asyncio
async def test_uncited_accept_or_reject_is_downgraded_to_review(monkeypatch):
    class FakeLLM:
        async def structured(self, *args, **kwargs):
            return {"verdict": "reject", "rationale": "Already addressed.", "evidence_ids": []}

    monkeypatch.setattr(research_critic, "retrieve_graph_rag", lambda *a, **k: {"items": hits()})
    monkeypatch.setattr(research_critic, "get_llm_provider", lambda: FakeLLM())
    result = await research_critic.critique_research_gap("A possible gap")
    assert result["verdict"] == "review"
