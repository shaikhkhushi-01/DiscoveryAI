# DiscoveryAI

**Evidence-grounded scientific discovery, research-gap analysis, and hypothesis planning.**

[![DiscoveryAI CI](https://github.com/shaikhkhushi-01/DiscoveryAI/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/shaikhkhushi-01/DiscoveryAI/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-see%20repository-blue.svg)](LICENSE)
[![Frontend](https://img.shields.io/badge/demo-live-16a085)](https://discovery-ai-swart.vercel.app/)
[![API](https://img.shields.io/badge/API-docs-2563eb)](https://discoveryai-6dmk.onrender.com/docs)

**Live application:** https://discovery-ai-swart.vercel.app/  
**API documentation:** https://discoveryai-6dmk.onrender.com/docs  
**Source code:** https://github.com/shaikhkhushi-01/DiscoveryAI

> **Research prototype, not a validated scientific product.** The live demo demonstrates evidence retrieval and grounded answer generation over the currently indexed corpus. Research-gap novelty, expert agreement, and baseline superiority have not yet been established through completed independent expert evaluation.


DiscoveryAI is a research-oriented platform that ingests scientific papers, extracts structured scientific information, indexes papers for hybrid retrieval, builds a knowledge graph, and generates evidence-bounded research-gap assessments and opportunity reports.

> **Scientific integrity:** DiscoveryAI can identify opportunities not represented in a specified indexed corpus and search scope. It cannot prove that a topic has never been researched globally.

## Quick tour

1. Open the [live dashboard](https://discovery-ai-swart.vercel.app/).
2. Try a scientific question that is covered by the currently indexed papers.
3. Inspect the generated answer and follow its numbered evidence citations to the retrieved source passages.
4. Review the [API documentation](https://discoveryai-6dmk.onrender.com/docs) for the backend interfaces.
5. Read the [evaluation status](docs/submission/EVALUATION_STATUS.md) before interpreting any reported benchmark numbers.

The public demo's indexed corpus may be small and can change as documents are added or re-indexed. A successful demo query is a functional demonstration, not evidence of broad scientific coverage.

## Verified live demo journey

On 2026-11-28, the deployed Explore flow was manually checked with a BERT masked-language-modeling question. The API returned an answer grounded in eight retrieved evidence passages; citation links opened the corresponding evidence passages and scrolled to the correct locations in the page.

This verifies that specific question-answering and evidence-navigation journey against the currently indexed corpus. It is not a benchmark score, a broad-coverage claim, or validation of research-gap novelty.

## What the system does

1. **Document intelligence** — PDF validation, parsing, metadata normalization, scientific extraction, and indexing.
2. **Hybrid scientific retrieval** — vector retrieval, knowledge-graph retrieval, fusion, and reranking.
3. **Evidence-grounded reasoning** — source-linked claims, supporting/contradictory evidence, and evidence validation.
4. **Research intelligence** — paper comparison, literature-review synthesis, temporal trends, and candidate-gap detection.
5. **Research Critic** — challenges candidate gaps against retrieved literature and returns a bounded verdict.
6. **Opportunity reports** — synthesizes evidence, limitations, research directions, hypotheses, and experiment plans.
7. **Evaluation tooling** — benchmark schema, adjudicated-gold evaluator, baseline comparison, ablation analysis, and dual-annotator agreement tooling.

## Architecture

```text
Next.js dashboard
       |
       v
FastAPI application ---- Authentication / API validation
       |
       +---- PDF ingestion and scientific extraction
       |
       +---- Hybrid retrieval ---- Qdrant (vectors)
       |                      \--- Neo4j (knowledge graph)
       |
       +---- PostgreSQL (users, papers, documents, jobs, metadata)
       |
       +---- Gemini / configured LLM provider
       |
       +---- Evidence validation -> Gap detection -> Research Critic
       |                                              |
       +---- Temporal trends / synthesis              v
                                          Opportunity report
                                          Hypothesis + experiments

Offline evaluation:
DiscoveryGapBench -> predictions -> evaluator -> baselines/ablations
                  -> dual-reviewer agreement -> adjudication
```

## Technology

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, React 19, TypeScript |
| API | Python 3.12, FastAPI, Pydantic |
| Relational data | PostgreSQL, SQLAlchemy, Alembic |
| Vector search | Qdrant |
| Knowledge graph | Neo4j |
| Background/runtime support | Redis, FastAPI background tasks / worker |
| LLM | Gemini provider, with provider abstractions for other configured backends |
| Document processing | PyMuPDF |
| Deployment | Vercel frontend, Render backend (current public deployment configuration), Docker Compose for local stack |
| Quality | pytest, TypeScript/Next production build, GitHub Actions |

## Repository map

- `backend/app/api/` — HTTP routes and request schemas.
- `backend/app/services/` — ingestion, extraction, retrieval, graph, evidence, gap detection, synthesis, agents, and evaluation services.
- `backend/app/models/` and `backend/alembic/` — persistence models and database migrations.
- `backend/app/tests/` and `backend/tests/` — unit and regression tests.
- `frontend/` — Next.js dashboard.
- `data/evaluation/` — benchmark schemas and starter templates; starter templates are not gold data.
- `research/` — research design, annotation rubrics, protocols, and release gates.
- `scripts/evaluation/` — benchmark, baseline, ablation, expert-agreement, and release-check CLIs.
- `docker-compose.yml` — local six-service development stack.

## Local development

### Prerequisites

- Python 3.12
- Node.js 20 and npm
- Docker Engine with Docker Compose
- Provider credentials for live LLM calls
- Sufficient disk/RAM for the selected embedding model and paper corpus

### 1. Configure environment

Copy `.env.example` to `.env` and replace all development placeholders where appropriate. Never commit real API keys, database credentials, JWT secrets, or reviewer identities.

For a production deployment, use `.env.production.example` as a variable checklist. Generate strong, unique secrets and configure explicit frontend origins.

### 2. Start infrastructure

```bash
docker compose up -d postgres neo4j qdrant redis
```

### 3. Start the backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`; interactive API documentation is at `http://localhost:8000/docs`.

### 4. Start the frontend

In a second terminal:

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

The dashboard is available at `http://localhost:3000`. Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local` for local API access.

### 5. Or start the complete Compose stack

```bash
docker compose up --build
```

The Compose file starts PostgreSQL, Neo4j, Qdrant, Redis, the API, and the frontend. Review the development-only default credentials before exposing any service beyond localhost.

## API entry points

- `GET /health` and `GET /api/v1/health` — process/API health.
- `GET /api/v1/public/overview`, `/gaps`, and `/trends` — public dashboard data.
- `POST /api/v1/public/graph-rag/retrieve` — public read-only retrieval surface.
- `POST /api/v1/public/graph-rag/ask` — public evidence-grounded question answering with retrieved source passages and graph context.
- `POST /api/v1/documents/upload` — authenticated PDF ingestion.
- `POST /api/v1/documents/{id}/index` — authenticated indexing.
- `GET /api/v1/diagnostics/qdrant-health` — authenticated Qdrant diagnostic.
- `/api/v1/gaps` — candidate gaps, critic, and opportunity reports (authenticated).
- `/api/v1/intelligence` — hypotheses, comparison, and literature review (authenticated).
- `/api/v1/agents` — discovery workflow (authenticated).

The deployed API's OpenAPI page is the source of truth for the exact current request and response schemas.

## Scientific evaluation

The evaluation framework is intentionally separate from the live product path.

### Benchmark and annotation

- Schema: `data/evaluation/discovery_gap_bench.schema.json`
- Annotation rubric: `research/discovery_gap_bench_annotation_rubric.md`
- Protocols: `research/phase4_*_protocol.md`
- Expert annotation instructions: `research/phase4_expert_validation_protocol.md`

Validate a benchmark:

```bash
python scripts/evaluation/validate_discovery_gap_bench.py path/to/benchmark.json
```

Run an adjudicated benchmark split:

```bash
python scripts/evaluation/run_discovery_gap_bench.py \
  --benchmark path/to/benchmark.json \
  --predictions path/to/predictions.json \
  --split test \
  --output reports/evaluation/discoveryai-test.json
```

Compare the five baseline systems:

```bash
python scripts/evaluation/compare_discovery_gap_baselines.py --help
```

Run component ablations:

```bash
python scripts/evaluation/run_discovery_gap_ablations.py --help
```

Analyze independent reviewer agreement:

```bash
python scripts/evaluation/analyze_expert_agreement.py \
  --annotator-a data/evaluation/annotations/reviewer-a.json \
  --annotator-b data/evaluation/annotations/reviewer-b.json \
  --output reports/evaluation/expert-agreement.json
```

Do not score the starter templates as if they were reviewed gold data. Do not publish benchmark scores, baseline superiority, or global-novelty claims until real expert annotations, adjudication, frozen corpus snapshots, and reproducible runs exist.

## Engineering checks

From the repository root:

```bash
python scripts/evaluation/release_check.py
```

Backend tests (run from `backend/`):

```bash
pip install -r requirements.txt pytest pytest-asyncio
PYTHONPATH=. pytest app/tests tests -q
python -m compileall app
```

Frontend production build (run from `frontend/`):

```bash
npm install
npm run build
```

CI runs backend compilation/tests, frontend production build, repository release checks, and Docker Compose configuration validation.

## Deployment notes

Current deployment configuration:

- Frontend: `https://discovery-ai-swart.vercel.app/`
- Backend: `https://discoveryai-6dmk.onrender.com/`
- API docs: `https://discoveryai-6dmk.onrender.com/docs`

Set `NEXT_PUBLIC_API_URL` in the frontend deployment to the backend origin. Set `CORS_ORIGINS` on the backend to the exact frontend origin(s). Configure PostgreSQL, Neo4j, Qdrant, Redis, LLM credentials, JWT secret, and all production secrets in the hosting provider's secret manager. Never put backend secrets in frontend variables.

A successful `/health` response proves that the API process responds; it does **not** prove that every database, vector index, graph query, LLM provider, or protected workflow is healthy. Validate each dependency and user journey separately.

## Current completion status

**Engineering:** the planned core product capabilities and Phase 4 evaluation tooling (benchmark specification, runner, baseline harness, ablation harness, and expert-agreement analysis) are implemented in the repository.

**Scientific validation:** still pending. The repository does not yet contain a populated, independently annotated and adjudicated benchmark with reported baseline/ablation results. Expert agreement and performance must be measured from real reviewer annotations and controlled prediction artifacts.

**Release status:** treat the project as an advanced research prototype until the engineering release checklist and scientific evaluation gate in `research/mbzuai_level_quality_gates.md` are satisfied.

## Research integrity commitments

- Scope every novelty statement to a named corpus snapshot and search protocol.
- Preserve provenance from claim to paper, document, and chunk.
- Include contradictory evidence and report uncertainty.
- Keep raw annotations, adjudication, and test labels separate.
- Record model/provider, prompt, embedding, retrieval configuration, code revision, corpus, benchmark, split, and random seed for every run.
- Report negative results and limitations; do not tune on the held-out test set.


## Submission package

The current submission materials are maintained in [`docs/submission/`](docs/submission/):

- [Project report draft](docs/submission/PROJECT_REPORT.md) — abstract, problem, objectives, related-work context, methodology, architecture, evaluation plan, limitations, and conclusion.
- [Architecture and data flow](docs/submission/ARCHITECTURE.md) — Mermaid system diagram and workflow descriptions.
- [Scientific evaluation status](docs/submission/EVALUATION_STATUS.md) — implemented tooling versus pending empirical evidence.
- [Presentation outline](docs/submission/PRESENTATION_OUTLINE.md) — 10-slide structure and integrity rules.
- [Demo script](docs/submission/DEMO_SCRIPT.md) — 7–9 minute walkthrough using verified live data.

These are submission drafts. Complete empirical results, a populated expert-adjudicated benchmark, and verified production end-to-end evidence must be added before describing the project as scientifically validated or fully production-ready.
