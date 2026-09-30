# Days 71–80 — Research Gap Detection Engine

## Implemented

### Day 71 — Gap taxonomy
Added explicit gap types: missing dataset, missing experiment, missing evaluation, underexplored topic, missing application, conflicting evidence and future work.

### Day 72 — Candidate generation
Neo4j is used to identify low-coverage topics and method/dataset coverage patterns.

### Day 73 — Underexplored topic signals
Topics with small indexed paper coverage are surfaced as candidate opportunity signals.

### Day 74 — Missing experiment signals
Methods associated with only one observed dataset in the indexed graph are surfaced as coverage-gap candidates.

### Day 75 — Evidence validation
Each candidate is sent through the existing GraphRAG retrieval pipeline to collect related evidence.

### Day 76 — Contradiction signal
Candidates with strong related evidence are marked `needs_review` rather than being treated as evidence of absence.

### Day 77 — Scope-aware confidence
Confidence is based on retrieved/indexed evidence and explicitly refers to the indexed corpus.

### Day 78 — Gap API
GET /api/v1/gaps returns validated candidate opportunity signals.

### Day 79 — Testing
Gap taxonomy and scope-aware validation tests were added.

### Day 80 — Documentation
This document records the research-gap milestone.

## Critical scientific rule
The engine never interprets lack of retrieved evidence as proof that nobody has researched the topic. It reports opportunity signals relative to the indexed corpus and search scope.

## Runtime note
Live gap detection requires populated Neo4j, Qdrant and scientific extraction data. No global novelty claim or live quality score is made without a validated corpus/evaluation set.