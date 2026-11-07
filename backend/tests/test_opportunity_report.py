import pytest

from app.services.gap_detection import opportunity_report


@pytest.mark.asyncio
async def test_report_handles_empty_evidence(monkeypatch):
    async def fake_critic(*args, **kwargs):
        return {"verdict": "review", "sources": [], "limitations": ["Sparse corpus."]}
    monkeypatch.setattr(opportunity_report, "critique_research_gap", fake_critic)
    result = await opportunity_report.build_research_opportunity_report("Possible gap")
    assert result["confidence"] == "low"
    assert result["research_directions"] == []
    assert result["scope"] == "indexed_corpus"


@pytest.mark.asyncio
async def test_report_filters_unknown_evidence_ids(monkeypatch):
    async def fake_critic(*args, **kwargs):
        return {"verdict": "review", "rationale": "Suggestive.", "sources": [{"evidence_id": "EVIDENCE 1"}], "limitations": []}
    class FakeLLM:
        async def structured(self, *args, **kwargs):
            return {
                "executive_summary": "Cautious summary.",
                "evidence_synthesis": [{"claim": "Claim.", "interpretation": "Tentative.", "evidence_ids": ["EVIDENCE 1", "EVIDENCE 9"]}],
                "research_directions": [{"direction": "Explore.", "rationale": "Possible.", "evidence_ids": ["EVIDENCE 9"]}],
                "proposed_experiments": [{"hypothesis": "Test.", "method": "Compare.", "possible_measurements": "Accuracy.", "evidence_ids": ["EVIDENCE 1"]}],
                "confidence": "high", "limitations": [],
            }
    monkeypatch.setattr(opportunity_report, "critique_research_gap", fake_critic)
    monkeypatch.setattr(opportunity_report, "get_llm_provider", lambda: FakeLLM())
    result = await opportunity_report.build_research_opportunity_report("Possible gap")
    assert result["evidence_synthesis"][0]["evidence_ids"] == ["EVIDENCE 1"]
    # Unsupported directions are dropped rather than returned without evidence.
    assert result["research_directions"] == []
    assert result["proposed_experiments"][0]["evidence_ids"] == ["EVIDENCE 1"]
