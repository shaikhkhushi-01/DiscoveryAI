from app.services.gap_detection import validator as gap_validator
from app.services.evidence import validator as evidence_validator
from app.services.evidence.scoring import compute_discovery_score


def _sources():
    return [
        {"paper_id": 1, "document_id": 11, "title": "Paper one", "text": "Relevant context", "rerank_score": 0.92, "semantic_score": 0.9, "graph_score": 0.8},
        {"paper_id": 1, "document_id": 11, "title": "Paper one", "text": "Another chunk", "rerank_score": 0.88, "semantic_score": 0.8, "graph_score": 0.7},
        {"paper_id": 2, "document_id": 12, "title": "Paper two", "text": "Related work", "rerank_score": 0.76, "semantic_score": 0.7, "graph_score": 0.6},
    ]


def test_high_relevance_is_not_mistaken_for_contradiction(monkeypatch):
    monkeypatch.setattr(gap_validator, "retrieve_graph_rag", lambda *a, **k: {"items": _sources()})
    result = gap_validator.validate_candidate({"title": "Candidate gap", "description": "A research opportunity"})
    assert result["contradictory_signal"] is False
    assert result["distinct_paper_count"] == 2
    assert result["supporting_papers"] == [1, 2]
    assert result["status"] == "weak_candidate"
    assert result["scope"] == "indexed_corpus"


def test_gap_requires_multiple_distinct_papers(monkeypatch):
    sources = _sources() + [
        {"paper_id": 3, "document_id": 13, "title": "Paper three", "text": "More context", "rerank_score": 0.7}
    ]
    monkeypatch.setattr(gap_validator, "retrieve_graph_rag", lambda *a, **k: {"items": sources})
    result = gap_validator.validate_candidate({"title": "Candidate gap"})
    assert result["status"] == "supported_candidate"
    assert result["distinct_paper_count"] == 3
    assert result["confidence"] <= 0.75


def test_evidence_validator_preserves_excerpt_and_does_not_infer_contradiction(monkeypatch):
    monkeypatch.setattr(evidence_validator, "retrieve_graph_rag", lambda *a, **k: {"items": _sources()})
    result = evidence_validator.validate_evidence({"title": "Candidate gap"})
    assert result["contradictory_signal"] is False
    assert result["evidence_status"] == "evidence_supported"
    assert result["evidence"][0]["excerpt"] == "Relevant context"
    assert result["score_version"] == "v2"


def test_discovery_score_discloses_unmeasured_defaults():
    result = compute_discovery_score({"retrieval_evidence_count": 0, "supporting_papers": []})
    assert 0 <= result["discovery_score"] <= 100
    assert result["score_version"] == "v2"
    assert result["assumptions"]["impact_signal"] == "default_assumption"
    assert "not proof" in result["interpretation"]
