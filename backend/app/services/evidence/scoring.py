from __future__ import annotations

from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EvidenceSignals:
    evidence_strength: float
    contradiction: float
    corpus_coverage: float
    source_diversity: float

def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))

def compute_evidence_signals(candidate: dict[str, Any]) -> EvidenceSignals:
    count = int(candidate.get("retrieval_evidence_count", 0))
    supporting = int(candidate.get("supporting_signal", 0))
    contradictory = 1.0 if candidate.get("contradictory_signal") else 0.0
    evidence_strength = clamp(min(1.0, (supporting / max(1, count)) + min(count, 5) * 0.08))
    corpus_coverage = clamp(count / 10.0)
    paper_ids = {x for x in candidate.get("supporting_papers", []) if x is not None}
    source_diversity = clamp(len(paper_ids) / 5.0)
    return EvidenceSignals(
        evidence_strength=evidence_strength,
        contradiction=contradictory,
        corpus_coverage=corpus_coverage,
        source_diversity=source_diversity,
    )

def compute_discovery_score(candidate: dict[str, Any]) -> dict[str, Any]:
    evidence = compute_evidence_signals(candidate)
    # These are explicit opportunity signals, not an assertion of global novelty.
    novelty = clamp(1.0 - evidence.corpus_coverage)
    impact = clamp(float(candidate.get("impact_signal", 0.5)))
    feasibility = clamp(float(candidate.get("feasibility_signal", 0.5)))
    social_importance = clamp(float(candidate.get("social_importance_signal", 0.5)))
    technical_difficulty = clamp(float(candidate.get("technical_difficulty_signal", 0.5)))
    competition = clamp(float(candidate.get("competition_signal", evidence.corpus_coverage)))
    cross_domain = clamp(float(candidate.get("cross_domain_signal", 0.5)))

    raw = (
        0.22 * novelty
        + 0.16 * impact
        + 0.12 * feasibility
        + 0.10 * social_importance
        + 0.10 * technical_difficulty
        + 0.12 * cross_domain
        + 0.10 * evidence.source_diversity
        + 0.08 * (1.0 - competition)
        - 0.15 * evidence.contradiction
    )
    score = round(100 * clamp(raw), 2)
    return {
        "discovery_score": score,
        "score_version": "v1",
        "components": {
            "novelty_signal": round(novelty, 4),
            "impact_signal": round(impact, 4),
            "feasibility_signal": round(feasibility, 4),
            "social_importance_signal": round(social_importance, 4),
            "technical_difficulty_signal": round(technical_difficulty, 4),
            "cross_domain_signal": round(cross_domain, 4),
            "competition_signal": round(competition, 4),
            "evidence_strength": round(evidence.evidence_strength, 4),
            "contradiction_signal": round(evidence.contradiction, 4),
            "corpus_coverage": round(evidence.corpus_coverage, 4),
        },
        "interpretation": "Opportunity signal within the indexed corpus; not proof of global research novelty.",
    }
