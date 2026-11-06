import pytest
from app.services.evaluation.expert_validation import analyze_expert_agreement


def _payload(annotator, status="supported", rating=3, evidence=None):
    return {"annotator_id":annotator,"annotations":[{
        "record_id":"r1",
        "assessment":{"gap_status":status,"novelty_within_corpus":rating,"relevance":3,"feasibility":2,"evidence_quality":3},
        "evidence": evidence if evidence is not None else [{"paper_id":"p1","document_id":"d1","chunk_id":"c1","stance":"supporting"}],
    }]}


def test_identical_annotations_have_perfect_agreement():
    result=analyze_expert_agreement(_payload("a"),_payload("b"))
    assert result["agreement"]["gap_status"]["value"] == 1.0
    assert result["agreement"]["ordinal_ratings"]["relevance"]["value"] == 1.0
    assert result["adjudication_queue"] == []


def test_disagreement_is_sent_to_adjudication_queue():
    result=analyze_expert_agreement(_payload("a"),_payload("b","contradicted",1))
    assert result["adjudication_queue"][0]["record_id"] == "r1"
    assert "gap_status" in result["adjudication_queue"][0]["disagreement_fields"]
    assert "novelty_within_corpus" in result["adjudication_queue"][0]["disagreement_fields"]


def test_evidence_disagreement_is_reported():
    result=analyze_expert_agreement(
        _payload("a"),
        _payload("b",evidence=[{"paper_id":"p2","document_id":"d2","chunk_id":"c2","stance":"contradictory"}]),
    )
    assert "evidence" in result["adjudication_queue"][0]["disagreement_fields"]
    assert result["agreement"]["mean_evidence_f1"] == 0.0


def test_requires_same_record_ids():
    a=_payload("a")
    b=_payload("b")
    b["annotations"][0]["record_id"]="different"
    with pytest.raises(ValueError,match="identical record IDs"):
        analyze_expert_agreement(a,b)


def test_rejects_same_annotator_identity():
    with pytest.raises(ValueError,match="distinct annotator IDs"):
        analyze_expert_agreement(_payload("same"),_payload("same"))
