def test_discovery_score_is_bounded():
    from app.services.evidence.scoring import compute_discovery_score
    result = compute_discovery_score({
        "retrieval_evidence_count": 2,
        "supporting_signal": 1,
        "supporting_papers": [1, 2],
        "contradictory_signal": False,
        "impact_signal": 0.8,
        "feasibility_signal": 0.7,
        "social_importance_signal": 0.6,
        "technical_difficulty_signal": 0.5,
        "cross_domain_signal": 0.9
    })
    assert 0 <= result["discovery_score"] <= 100
    assert result["score_version"] == "v1"

def test_clamp_handles_extremes():
    from app.services.evidence.scoring import clamp
    assert clamp(-1) == 0
    assert clamp(2) == 1
