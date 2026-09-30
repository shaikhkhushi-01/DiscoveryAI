# Days 81–90 — Evidence Validation and Discovery Score

## Implemented

### Day 81 — Evidence model
Evidence validation now records supporting papers, retrieval evidence count, supporting signal and contradiction signal.

### Day 82 — Contradiction detection
Strong reranked evidence with graph connectivity is treated as a review/contradiction signal rather than ignored.

### Day 83 — Evidence status
Candidates are classified as evidence_supported, contradicted_or_needs_review, or insufficient_evidence.

### Day 84 — Discovery Score
Added an explicit v1 score from 0–100 composed of novelty, impact, feasibility, social importance, technical difficulty, cross-domain potential, source diversity and competition, with contradiction as a penalty.

### Day 85 — Explainability
Every score returns component-level signals and a version identifier.

### Day 86 — Corpus-aware novelty
Novelty is defined as an indexed-corpus opportunity signal derived from coverage, not global research absence.

### Day 87 — Opportunity ranking
Opportunity endpoint sorts candidates by Discovery Score.

### Day 88 — Evidence API
GET /api/v1/evidence/opportunities and GET /api/v1/evidence/gap/{gap_index}.

### Day 89 — Tests
Discovery Score bounds and clamp behavior are covered by unit tests.

### Day 90 — Documentation
This document records the evidence/score milestone.

## Discovery Score v1
The score is intentionally transparent and versioned. Its weights are an initial engineering/research specification and require empirical validation and expert calibration before being treated as a validated scientific metric.

## Critical limitation
A high score does not mean a research gap is globally novel or that an opportunity will succeed. It is an evidence-based signal relative to the indexed corpus and configured scoring model.