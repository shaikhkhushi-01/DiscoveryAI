# Day 120 — Final Engineering Hardening and Evaluation Readiness

## Implemented

### 1. Continuous integration
Added GitHub Actions workflow:
- backend dependency installation
- Python compilation check
- backend unit tests
- frontend dependency installation
- frontend production build
- repository foundation check
- Docker Compose configuration validation

### 2. Release readiness check
Added:
`scripts/evaluation/release_check.py`

It verifies critical scientific modules, API integration surface, and all six Compose services.

### 3. Evaluation framework

DiscoveryAI evaluation is organized into:

| Area | Metrics |
|---|---|
| Document extraction | Precision, Recall, F1 |
| Retrieval | Recall@K, Precision@K, MRR, nDCG |
| Gap detection | Precision@K, Recall@K, F1, nDCG, FDR |
| Evidence | Citation correctness, evidence faithfulness, contradiction detection, unsupported-claim rate |
| Discovery Score | Correlation/calibration against expert assessments |
| Hypotheses | Expert testability, novelty, falsifiability |
| Experiments | Expert relevance, reproducibility, completeness |
| Trends | Temporal holdout accuracy/calibration |

## Required baselines

Evaluation should compare:
1. LLM-only
2. Standard RAG
3. GraphRAG
4. Hybrid RAG
5. DiscoveryAI

## Required ablations

At minimum:
- without knowledge graph
- without vector retrieval
- without trend analysis
- without research critic
- without Discovery Score
- without multi-agent orchestration
- full system

## DiscoveryGapBench

The benchmark schema should contain:
- research question
- corpus
- candidate gap
- gap type
- supporting papers
- contradictory papers
- evidence
- expert ratings

## Evidence policy

The system must not claim:
“nobody has researched this.”

Preferred language:
“No relevant evidence was identified within the indexed corpus and search scope.”

## Scientific validation requirements

Current repository implementation provides infrastructure and evaluation definitions. It does not claim measured benchmark scores until a labeled corpus, expert annotations, and controlled runs are completed.

## Deployment readiness

Before production:
- set production environment variables
- use non-default secrets
- deploy FastAPI backend
- set Vercel `NEXT_PUBLIC_API_URL`
- configure authentication and CORS
- run CI
- run database migrations
- ingest a controlled evaluation corpus
- execute baseline/ablation experiments
- review unsupported-claim rate

## Final architecture

Question → GraphRAG → Gap Detection → Evidence Validation → Discovery Score → Temporal Intelligence → Research Critic → Hypothesis → Experiment Plan → Dashboard.

## Day 120 status

Engineering roadmap implementation: complete through the planned Day 120 scope.

Scientific performance claims: pending controlled evaluation and expert validation.
