import pytest

from app.services import hypothesis_intelligence


def test_distinct_source_count_uses_papers_not_chunks():
    evidence = [
        {"paper_id": 1, "document_id": 10},
        {"paper_id": 1, "document_id": 10},
        {"paper_id": 2, "document_id": 20},
        {"document_id": 30},
    ]
    assert hypothesis_intelligence._distinct_source_count(evidence) == 3


@pytest.mark.asyncio
async def test_hypothesis_generation_skips_single_paper_candidates(monkeypatch):
    monkeypatch.setattr(
        hypothesis_intelligence,
        "score_opportunities",
        lambda limit: {
            "items": [
                {
                    "title": "Too little evidence",
                    "evidence_status": "evidence_supported",
                    "evidence": [
                        {"paper_id": 1, "document_id": 10},
                        {"paper_id": 1, "document_id": 10},
                    ],
                }
            ]
        },
    )

    async def should_not_generate(*args, **kwargs):
        raise AssertionError("Hypothesis generation must not run with one source paper")

    monkeypatch.setattr(hypothesis_intelligence, "generate_hypothesis", should_not_generate)
    result = await hypothesis_intelligence.generate_opportunity_plan("test question")

    assert result["count"] == 0
    assert result["skipped_count"] == 1
    assert result["skipped_candidates"][0]["distinct_source_count"] == 1


@pytest.mark.asyncio
async def test_hypothesis_generation_keeps_independently_supported_candidates(monkeypatch):
    monkeypatch.setattr(
        hypothesis_intelligence,
        "score_opportunities",
        lambda limit: {
            "items": [
                {
                    "title": "Supported candidate",
                    "evidence_status": "evidence_supported",
                    "evidence": [
                        {"paper_id": 1, "document_id": 10},
                        {"paper_id": 2, "document_id": 20},
                    ],
                }
            ]
        },
    )

    async def fake_generate(question, gap, evidence):
        return {"hypothesis": "Testable statement", "result_status": "not_run"}

    monkeypatch.setattr(hypothesis_intelligence, "generate_hypothesis", fake_generate)
    result = await hypothesis_intelligence.generate_opportunity_plan("test question")

    assert result["count"] == 1
    assert result["plans"][0]["supporting_distinct_paper_count"] == 2
    assert "not experimental results" in result["warning"]
