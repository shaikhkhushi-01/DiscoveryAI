# Days 109–116 — Hypothesis Generation and Experiment Intelligence

## Implemented

### Day 109 — Opportunity-to-hypothesis bridge
Scored opportunity candidates can be converted into testable hypothesis proposals.

### Day 110 — Structured hypothesis generation
Hypothesis output includes statement, rationale, variables, expected direction and falsification condition.

### Day 111 — Experiment planner
Plans include objective, datasets, baselines, metrics, protocol and ablations.

### Day 112 — Reproducibility protocol
Plans specify matched settings, fixed train/validation/test separation, repeated seeds where appropriate and statistical reporting.

### Day 113 — Missing-dataset awareness
Candidate missing datasets from the gap engine are carried into the proposed plan when available.

### Day 114 — Evidence linkage
Plans retain supporting evidence identifiers/count and the indexed-corpus scope.

### Day 115 — API
POST /api/v1/intelligence/hypotheses.

### Day 116 — Testing and documentation
Added tests for reproducibility fields and the explicit not-run result status.

## Scientific safeguard
The system generates proposals, not fabricated experimental findings. Every plan starts with `result_status: not_run` and must be executed and evaluated separately.

## Runtime note
Live generation requires the configured LLM provider plus the indexed Neo4j/Qdrant evidence used by the opportunity engine.