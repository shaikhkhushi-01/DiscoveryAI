# DiscoveryAI — Technology Stack

## 1. Purpose

This document defines the technology stack selected for DiscoveryAI based on the system architecture, research requirements, scalability goals, and implementation constraints established during Days 1–5.

The stack is selected to support:

* Scientific research workflows
* Evidence-grounded AI pipelines
* Hybrid vector + graph retrieval
* Reproducible experiments
* Modular backend development
* Asynchronous processing
* Production deployment
* Future selective service extraction

Exact dependency versions will be pinned during implementation rather than using floating `latest` versions.

---

# 2. Technology Stack Summary

| Layer            | Selected Technology                 | Primary Responsibility            |
| ---------------- | ----------------------------------- | --------------------------------- |
| Frontend         | Next.js + React + TypeScript        | Research dashboard and UI         |
| Backend API      | Python + FastAPI                    | REST API and application boundary |
| Validation       | Pydantic                            | Typed schemas and validation      |
| AI Orchestration | Python + LangGraph                  | Stateful AI workflows             |
| ML/NLP           | PyTorch + Hugging Face Transformers | Scientific NLP and ML             |
| Embeddings       | Sentence Transformers               | Semantic representations          |
| LLM              | Provider abstraction                | Model interchangeability          |
| Local LLM        | Ollama                              | Local/private inference           |
| Relational DB    | PostgreSQL                          | Application state and metadata    |
| Knowledge Graph  | Neo4j                               | Scientific relationships          |
| Vector DB        | Qdrant                              | Semantic retrieval                |
| Cache/Queue      | Redis                               | Cache and job coordination        |
| Workers          | Celery                              | Background processing             |
| PDF Processing   | PyMuPDF                             | Scientific document extraction    |
| Testing          | Pytest + HTTPX                      | Backend testing                   |
| Frontend Testing | Vitest + Playwright                 | Frontend testing                  |
| Containers       | Docker + Docker Compose             | Reproducible environment          |
| CI/CD            | GitHub Actions                      | Automated validation              |
| Observability    | Structured logging + OpenTelemetry  | Monitoring and tracing            |
| Version Control  | Git + GitHub                        | Source control                    |

---

# 3. Frontend Technology

## Selected Technologies

* Next.js
* React
* TypeScript

## Responsibilities

The frontend will provide:

* Research query interface
* Paper explorer
* Document upload
* Knowledge graph visualization
* Research-gap visualization
* Trend dashboards
* Research opportunity reports
* Hypothesis visualization
* Experiment-plan visualization
* Authentication interface

The frontend must **not contain core scientific reasoning logic**.

Scientific reasoning will remain inside backend/application modules.

---

# 4. Backend Technology

## Selected Technologies

* Python
* FastAPI
* Pydantic

FastAPI will provide the main application API.

Responsibilities include:

* Authentication boundary
* Authorization
* Request validation
* API routing
* Research queries
* Document upload
* Job creation
* Job status
* Result retrieval
* Report retrieval

Example API structure:

```text
/api/v1/research/query
/api/v1/documents
/api/v1/documents/{id}
/api/v1/gaps
/api/v1/trends
/api/v1/reports/{id}
```

API routes should remain thin.

They should call application services instead of directly executing LLM or scientific reasoning logic.

---

# 5. Application Orchestration

## Selected Technologies

* Python application services
* LangGraph for complex stateful workflows

The orchestration layer will coordinate:

* Document-processing workflows
* Retrieval workflows
* Evidence-validation workflows
* Gap-detection workflows
* Research-critic workflows
* Hypothesis generation
* Experiment planning
* Report generation

LangGraph should be used when explicit state, branching, retries, checkpoints, or agent coordination provide a concrete benefit.

Simple deterministic operations should remain ordinary Python services.

---

# 6. AI / ML Stack

## Selected Technologies

* PyTorch
* Hugging Face Transformers
* Sentence Transformers

These technologies will support:

* Scientific NLP
* Entity extraction
* Classification
* Semantic embeddings
* Reranking experiments
* Model evaluation
* Fine-tuning when scientifically justified

The system should avoid introducing custom ML models before a baseline has been established.

---

# 7. LLM Provider Architecture

DiscoveryAI will not depend on one specific LLM provider.

The application will define provider interfaces:

```text
LLMProvider
EmbeddingProvider
RerankerProvider
```

Initial provider targets:

```text
Ollama
OpenAI-compatible provider
Gemini-compatible provider
Anthropic-compatible provider
```

Provider-specific implementations should remain isolated inside adapter modules.

Conceptual architecture:

```text
AI Layer
│
├── interfaces/
│   ├── llm.py
│   ├── embeddings.py
│   └── reranker.py
│
└── providers/
    ├── ollama/
    ├── openai/
    ├── gemini/
    └── anthropic/
```

This allows DiscoveryAI to compare different models without modifying the complete application.

---

# 8. Relational Database

## Selected Technology

**PostgreSQL**

PostgreSQL will own application state and structured metadata.

It will store:

* Users
* Roles
* Documents
* Processing jobs
* Research queries
* Reports
* Experiment records
* Model-run metadata
* Audit records
* Configuration metadata

PostgreSQL is not intended to replace the scientific knowledge graph or vector database.

---

# 9. Scientific Knowledge Graph

## Selected Technology

**Neo4j**

Neo4j will represent scientific entities and their relationships.

Primary node types:

```text
Paper
Author
Institution
Topic
Method
Dataset
Problem
Application
Metric
Experiment
Domain
ResearchGap
Hypothesis
```

Example relationships:

```text
Paper
 ├── AUTHORED_BY → Author
 ├── AFFILIATED_WITH → Institution
 ├── USES → Method
 ├── EVALUATED_ON → Dataset
 ├── USES_METRIC → Metric
 ├── ADDRESSES → Problem
 ├── APPLIED_TO → Application
 ├── CITES → Paper
 └── PROPOSES_FUTURE_WORK → ResearchGap
```

Neo4j will primarily support multi-hop scientific relationship traversal and graph-based reasoning.

---

# 10. Vector Database

## Selected Technology

**Qdrant**

Qdrant will store embeddings for:

* Papers
* Abstracts
* Sections
* Chunks
* Evidence passages
* Research questions

Each vector record should retain useful metadata such as:

```text
paper_id
document_id
section
page
chunk_id
publication_year
topic
source
```

Qdrant provides the semantic retrieval component of DiscoveryAI.

---

# 11. Hybrid Retrieval Architecture

DiscoveryAI will use:

```text
Vector Retrieval
        +
Graph Retrieval
        +
Evidence Fusion
        +
Reranking
```

Conceptual flow:

```text
Research Question
       │
       ▼
Query Understanding
       │
   ┌───┴────┐
   ▼        ▼
 Qdrant   Neo4j
   │        │
   ▼        ▼
Semantic  Structural
Evidence  Evidence
   └───┬────┘
       ▼
Evidence Fusion
       ▼
Reranker
       ▼
Final Evidence Set
```

Retrieval evaluation will use:

* Recall@K
* Precision@K
* MRR
* nDCG

---

# 12. Cache and Background Processing

## Selected Technologies

* Redis
* Celery

Redis will provide:

* Caching
* Queue/broker support
* Short-lived processing state

Celery workers will handle expensive workloads such as:

* PDF processing
* Embedding generation
* Knowledge graph construction
* Large corpus analysis
* Trend computation
* Gap detection
* Report generation

Long-running tasks should not block normal API requests.

Example:

```text
POST /documents
       │
       ▼
Create Job
       │
       ▼
Return Job ID
       │
       ▼
Background Worker
       │
       ▼
Process Document
       │
       ▼
Store Results
```

---

# 13. Scientific Document Processing

## Initial Technology

**PyMuPDF**

Initial pipeline:

```text
PDF
 ↓
Document Validation
 ↓
Text Extraction
 ↓
Section Detection
 ↓
Reference Extraction
 ↓
Table / Figure Metadata
 ↓
Chunking
 ↓
Embedding Generation
 ↓
Scientific Information Extraction
 ↓
Qdrant + Neo4j + PostgreSQL
```

The pipeline must preserve source provenance.

For example:

```text
Document
 → Page
 → Section
 → Paragraph
 → Chunk
 → Evidence
```

This provenance is necessary for evidence-grounded research claims.

---

# 14. Data Validation and Schemas

## Selected Technology

**Pydantic**

Pydantic will define typed contracts between modules.

Important schemas will include:

```text
PaperMetadata
Document
Section
Chunk
ScientificEntity
Relationship
Evidence
ResearchGap
ResearchOpportunity
Hypothesis
ExperimentPlan
ModelRun
JobStatus
```

The purpose is to prevent uncontrolled data passing between AI modules.

---

# 15. Testing Stack

## Backend

* Pytest
* HTTPX
* Unit tests
* Integration tests

## Frontend

* Vitest
* Playwright

## Research Evaluation

Research evaluation will be maintained separately from ordinary software tests.

Metrics will include:

### Extraction

* Precision
* Recall
* F1

### Retrieval

* Recall@K
* Precision@K
* MRR
* nDCG

### Gap Detection

* Precision@K
* Recall@K
* F1
* nDCG
* False Discovery Rate

### Evidence Quality

* Citation correctness
* Evidence faithfulness
* Unsupported-claim rate
* Contradiction detection

---

# 16. Containerization

## Selected Technologies

* Docker
* Docker Compose

Initial local infrastructure:

```text
┌─────────────────────────────┐
│          Frontend           │
│        Next.js              │
└──────────────┬──────────────┘
               │
┌──────────────▼──────────────┐
│          Backend            │
│          FastAPI            │
└───────┬─────────┬───────────┘
        │         │
        ▼         ▼
 PostgreSQL    Redis
        │         │
        ▼         ▼
     Neo4j      Celery
                  │
                  ▼
               Workers
                  │
                  ▼
                Qdrant
```

Docker Compose will provide reproducible local development.

---

# 17. CI/CD

## Selected Technology

**GitHub Actions**

Initial CI pipeline:

```text
Code Push
   │
   ▼
Formatting Check
   │
   ▼
Linting
   │
   ▼
Type Checking
   │
   ▼
Backend Tests
   │
   ▼
Frontend Tests
   │
   ▼
Build Validation
   │
   ▼
Docker Validation
```

Future CI stages may include:

* Security scanning
* Dependency auditing
* Benchmark evaluation
* Research evaluation datasets
* Deployment workflows

---

# 18. Observability

DiscoveryAI requires more than ordinary application logging because scientific reasoning must be inspectable.

Selected approach:

* Structured logging
* Metrics
* OpenTelemetry-compatible tracing
* Audit events

The following chain should eventually be traceable:

```text
User Query
     ↓
Query Interpretation
     ↓
Retrieved Evidence
     ↓
Model / LLM Call
     ↓
Generated Claim
     ↓
Evidence Validation
     ↓
Final Result
```

This will help identify unsupported scientific claims and retrieval failures.

---

# 19. Security Technology Boundary

Initial security requirements include:

* Authentication
* Authorization
* Input validation
* Rate limiting
* Audit logging
* Environment-based secrets
* Dependency scanning
* No API keys inside source code

Secrets should be supplied through environment variables or a dedicated secret-management system.

Security responsibilities should remain primarily at the API/application boundary.

---

# 20. Development Environment

Recommended baseline:

```text
Python 3.12+
Node.js LTS
Docker
Git
GitHub
VS Code / equivalent IDE
```

Dependency versions will be pinned during repository implementation.

---

# 21. Why Python?

Python is selected as the primary backend language because DiscoveryAI is fundamentally an AI/ML and scientific-data system.

The ecosystem provides strong support for:

* NLP
* Deep learning
* Scientific computing
* PDF processing
* Data analysis
* Graph tooling
* Vector retrieval
* LLM orchestration
* Research evaluation

Keeping the AI and scientific-processing layers in Python also reduces cross-language complexity.

---

# 22. Why FastAPI?

FastAPI provides a typed Python API layer suitable for separating:

```text
HTTP concerns
       ↓
Application services
       ↓
Scientific processing
       ↓
AI/ML systems
```

This separation is important because API endpoints should not directly contain scientific reasoning logic.

---

# 23. Why PostgreSQL + Neo4j + Qdrant?

The three databases have different responsibilities.

```text
PostgreSQL
     ↓
Application State

Neo4j
     ↓
Scientific Relationships

Qdrant
     ↓
Semantic Retrieval
```

This separation prevents one database from becoming responsible for incompatible workloads.

---

# 24. Why Redis + Celery?

Scientific document processing can be computationally expensive.

Examples:

* Large PDF parsing
* Embedding thousands of chunks
* Knowledge graph extraction
* Trend computation
* Gap analysis
* Report generation

Therefore these workloads should execute asynchronously.

```text
FastAPI
   ↓
Job
   ↓
Redis
   ↓
Celery Worker
   ↓
Scientific Processing
```

---

# 25. Why Provider Abstraction?

Scientific experiments may require comparing:

* Different LLMs
* Different embedding models
* Different rerankers
* Local vs hosted inference

Therefore application logic must not depend directly on one provider.

The abstraction makes model experimentation easier and improves reproducibility.

---

# 26. Why Docker?

DiscoveryAI depends on several infrastructure components:

```text
PostgreSQL
Neo4j
Qdrant
Redis
Backend
Worker
Frontend
```

Docker provides a reproducible local environment and reduces installation differences between development machines.

---

# 27. Alternatives Considered

| Concern       | Selected           | Alternatives                  |
| ------------- | ------------------ | ----------------------------- |
| Backend       | FastAPI            | Django, Flask                 |
| Frontend      | Next.js            | Vite React, Remix             |
| Graph DB      | Neo4j              | ArangoDB                      |
| Vector DB     | Qdrant             | Milvus, pgvector              |
| Relational DB | PostgreSQL         | MySQL                         |
| Queue         | Redis + Celery     | RabbitMQ, Kafka               |
| AI Workflow   | LangGraph + Python | Custom engine, LangChain-only |
| Local LLM     | Ollama             | vLLM, llama.cpp               |
| Containers    | Docker Compose     | Kubernetes                    |

These alternatives may be reconsidered later if benchmarks demonstrate a concrete advantage.

---

# 28. Research Reproducibility Policy

Technology choices must not become hidden assumptions in scientific evaluation.

Whenever a component can affect research results, DiscoveryAI should record:

```text
Model name
Model version
Embedding model
Retrieval configuration
Reranker
Prompt/version
Corpus version
Knowledge graph version
Evaluation dataset
Random seed
Runtime configuration
```

This metadata will allow meaningful comparison between experiments.

---

# 29. Architecture-to-Technology Mapping

```text
Presentation
→ Next.js / React / TypeScript

API
→ FastAPI / Pydantic

Application
→ Python Services

AI Workflow
→ Python + LangGraph

ML
→ PyTorch / Transformers

Embeddings
→ Sentence Transformers

LLM
→ Ollama + Provider Adapters

Relational State
→ PostgreSQL

Scientific Graph
→ Neo4j

Semantic Retrieval
→ Qdrant

Cache / Queue
→ Redis

Workers
→ Celery

Document Processing
→ PyMuPDF + Extraction Modules

Containers
→ Docker / Docker Compose

CI
→ GitHub Actions

Observability
→ Structured Logging + OpenTelemetry
```

---

# 30. Technology Stack Completion Criteria

Day 6 is complete when:

* [ ] Frontend stack selected
* [ ] Backend stack selected
* [ ] AI/ML stack selected
* [ ] LLM provider strategy selected
* [ ] Embedding strategy selected
* [ ] Relational database selected
* [ ] Knowledge graph selected
* [ ] Vector database selected
* [ ] Cache/queue selected
* [ ] Worker technology selected
* [ ] Document-processing stack selected
* [ ] Testing stack selected
* [ ] Containerization strategy selected
* [ ] CI strategy selected
* [ ] Observability strategy selected
* [ ] Security boundary defined
* [ ] Alternatives considered
* [ ] Research reproducibility policy defined
* [ ] Architecture-to-technology mapping documented
* [ ] `research/technology_stack.md` committed to GitHub

---

# 31. Final Technology Decision

DiscoveryAI will initially use a Python-centered modular architecture:

```text
Next.js
     +
FastAPI
     +
Python
     +
PyTorch / Transformers
     +
LangGraph
     +
PostgreSQL
     +
Neo4j
     +
Qdrant
     +
Redis
     +
Celery
     +
Docker
     +
GitHub Actions
```

The stack is intentionally modular.

Individual components can later be benchmarked, replaced, or selectively extracted into separate services without redesigning the complete DiscoveryAI architecture.

The technology stack therefore supports the primary project goal:

> Build an evidence-grounded scientific discovery system capable of identifying, validating, and explaining research opportunities rather than merely retrieving existing papers.
