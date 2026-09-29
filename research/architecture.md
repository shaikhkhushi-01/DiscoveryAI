# DiscoveryAI — System Architecture

## 1. Purpose

This document defines the high-level architecture of DiscoveryAI and maps the requirements defined in `research/requirements.md` to system components, data flows, AI/ML modules, storage systems, and execution workflows.

The architecture is designed to support evidence-grounded scientific research opportunity discovery while remaining modular, testable, reproducible, and scalable.

---

# 2. Architectural Principles

DiscoveryAI follows these principles:

1. Modular design
2. Clear component boundaries
3. Evidence-grounded scientific reasoning
4. Separation of application logic and AI providers
5. Hybrid vector and graph retrieval
6. Asynchronous processing for expensive workloads
7. Scientific data provenance
8. Reproducible AI execution
9. Testability of individual modules
10. Future service extraction without requiring an initial distributed architecture

---

# 3. High-Level Architecture

```text
                         ┌──────────────────────┐
                         │        USER          │
                         │ Researcher / Admin   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Next.js Frontend   │
                         │      Dashboard       │
                         └──────────┬───────────┘
                                    │ HTTPS
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI         │
                         │ API / Auth Layer     │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    │               │                │
                    ▼               ▼                ▼
             ┌───────────┐   ┌────────────┐   ┌─────────────┐
             │ Research  │   │ Document   │   │ Auth / User │
             │  Module   │   │  Pipeline  │   │   Module    │
             └─────┬─────┘   └──────┬─────┘   └─────────────┘
                   │                │
                   └───────┬────────┘
                           ▼
                ┌────────────────────────┐
                │    AI / ML Layer       │
                │                        │
                │ LLM / Embeddings /     │
                │ Reranking / Extraction │
                └───────────┬────────────┘
                            │
                            ▼
                ┌────────────────────────┐
                │   Hybrid Retrieval     │
                │                        │
                │ Vector + Graph Search   │
                └───────────┬────────────┘
                            │
                   ┌────────┴────────┐
                   ▼                 ▼
             ┌────────────┐    ┌────────────┐
             │   Qdrant   │    │   Neo4j    │
             │Vector Store│    │Knowledge KG│
             └────────────┘    └────────────┘
                   │                 │
                   └────────┬────────┘
                            ▼
                 ┌──────────────────────┐
                 │ Scientific Reasoning │
                 │      Modules         │
                 │                      │
                 │ Gap Detection        │
                 │ Evidence Validation  │
                 │ Temporal Analysis    │
                 │ Opportunity Engine   │
                 └──────────┬───────────┘
                            │
                   ┌────────┴────────┐
                   ▼                 ▼
            Hypothesis        Experiment
            Generator          Planner
                   │                 │
                   └────────┬────────┘
                            ▼
                    Report Generator
```

---

# 4. Presentation Layer

Technology target:

```text
Next.js
React
TypeScript
```

Responsibilities:

* Research search interface
* Document upload
* Paper explorer
* Knowledge graph visualization
* Research gap visualization
* Trend dashboards
* Research opportunity reports
* Hypothesis display
* Experiment plan display
* Authentication interface

The frontend shall not contain core scientific reasoning logic.

---

# 5. API Layer

Technology target:

```text
Python
FastAPI
```

Responsibilities:

* Authentication
* Authorization
* Request validation
* API routing
* Research queries
* Document upload
* Job creation
* Job status
* Result retrieval
* Report retrieval

Example endpoints:

```text
POST /api/v1/research/query

POST /api/v1/documents

GET /api/v1/documents/{id}

GET /api/v1/gaps

GET /api/v1/trends

GET /api/v1/reports/{id}
```

The API layer should coordinate application services rather than directly embedding scientific reasoning or provider-specific LLM logic.

---

# 6. Application and Orchestration Layer

This layer coordinates DiscoveryAI workflows.

Responsibilities:

* Research workflow execution
* Pipeline coordination
* Agent/module coordination
* Job management
* Evidence aggregation
* Result generation
* Error handling

Conceptual flow:

```text
API
 ↓
Application Service
 ↓
Research Workflow
 ↓
AI / Retrieval / Knowledge Modules
```

---

# 7. Scientific Document Pipeline

```text
PDF
 │
 ▼
Document Upload
 │
 ▼
Document Processor
 │
 ▼
Text Extraction
 │
 ▼
Section Detection
 │
 ▼
Chunk Generation
 │
 ├───────────────┐
 ▼               ▼
Embeddings     LLM Extraction
 │               │
 ▼               ▼
Qdrant        Scientific Entities
                  │
                  ▼
                Neo4j
```

The document pipeline shall preserve document metadata and provenance.

---

# 8. AI / ML Layer

The AI layer shall provide provider-independent abstractions.

Core interfaces:

```text
LLMProvider
EmbeddingProvider
RerankerProvider
```

Potential providers:

```text
Ollama
OpenAI
Gemini
Claude
```

Conceptual interface:

```python
class LLMProvider:
    def generate(self, prompt, context):
        ...
```

Provider-specific implementations should remain behind the abstraction.

---

# 9. Knowledge Layer

The knowledge layer consists of:

```text
Scientific Knowledge Graph
Vector Retrieval
Evidence Store
Metadata
Provenance
```

## Neo4j

Neo4j shall represent scientific entities and relationships.

Example:

```text
Paper
 ├── USES → Method
 ├── EVALUATED_ON → Dataset
 ├── USES_METRIC → Metric
 ├── ADDRESSES → Problem
 ├── CITES → Paper
 └── PROPOSES_FUTURE_WORK → ResearchGap
```

## Qdrant

Qdrant shall store:

* Paper embeddings
* Abstract embeddings
* Chunk embeddings
* Evidence embeddings

---

# 10. Hybrid Retrieval

Hybrid retrieval combines semantic and structural retrieval.

```text
User Query
    │
    ▼
Query Understanding
    │
    ├───────────────┐
    ▼               ▼
Vector Search    Graph Search
    │               │
    ▼               ▼
Semantic          Structural
Evidence          Evidence
    │               │
    └───────┬───────┘
            ▼
       Evidence Fusion
            │
            ▼
          Reranker
            │
            ▼
      Final Evidence Set
```

The objective is to combine semantic similarity with scientific graph structure.

---

# 11. Research Gap Engine

```text
Evidence
   │
   ▼
Research Landscape
   │
   ▼
Gap Candidate Generator
   │
   ├── Topic Gap
   ├── Dataset Gap
   ├── Benchmark Gap
   ├── Experiment Gap
   ├── Evaluation Gap
   ├── Application Gap
   └── Interdisciplinary Gap
   │
   ▼
Candidate Gaps
   │
   ▼
Evidence Validator
   │
   ▼
Research Critic
   │
   ▼
Validated Opportunity
```

The gap detector shall not independently make universal claims about the absence of research.

---

# 12. Evidence Validation

Each candidate research gap should be challenged through evidence validation.

```text
Candidate Gap
      │
      ▼
Supporting Evidence Search
      │
      ▼
Contradictory Evidence Search
      │
      ▼
Evidence Analysis
      │
      ▼
Research Critic
      │
      ▼
Confidence
```

A lack of retrieved evidence shall be interpreted within the indexed corpus and search scope.

---

# 13. Temporal Intelligence

```text
Scientific Corpus
       │
       ▼
Time-aware Metadata
       │
       ▼
Topic / Method / Dataset Trends
       │
       ▼
Trend Engine
       │
       ├── Emerging
       ├── Growing
       ├── Stable
       └── Declining
       │
       ▼
Opportunity Analysis
```

Temporal signals are treated as additional evidence rather than as proof of a research opportunity.

---

# 14. Research Opportunity Engine

```text
Research Gap
     +
Supporting Evidence
     +
Contradictory Evidence
     +
Temporal Signal
     +
Research Density
     +
Feasibility
     +
Impact
     ↓
Research Opportunity
```

The opportunity engine will later support the Discovery Score defined in the research specification.

---

# 15. Hypothesis and Experiment Layer

```text
Validated Opportunity
        │
        ▼
Hypothesis Generator
        │
        ▼
Candidate Hypotheses
        │
        ▼
Research Critic
        │
        ▼
Experiment Planner
        │
        ├── Dataset
        ├── Baseline
        ├── Method
        ├── Metrics
        └── Experimental Setup
```

---

# 16. Agent Architecture

The initial implementation will treat agents as logical modules rather than independent microservices.

```text
Coordinator
│
├── Paper Reader
├── Knowledge Graph Agent
├── Retrieval Agent
├── Gap Detection Agent
├── Trend Agent
├── Research Critic
├── Hypothesis Agent
├── Experiment Planner
└── Report Generator
```

Conceptual workflow:

```text
Coordinator
      │
      ▼
Paper Reader
      │
      ▼
Knowledge / Retrieval
      │
      ▼
Gap Detector
      │
      ▼
Evidence Validator
      │
      ▼
Research Critic
      │
      ▼
Opportunity
      │
      ├─────────────┐
      ▼             ▼
Hypothesis     Experiment
Generator      Planner
      │             │
      └──────┬──────┘
             ▼
       Report Generator
```

---

# 17. Background Processing

Expensive operations shall use asynchronous background processing.

```text
FastAPI
   │
   ▼
Redis / Queue
   │
   ▼
Worker
   │
   ├── PDF Processing
   ├── Embedding Generation
   ├── Knowledge Graph Construction
   ├── Trend Analysis
   ├── Gap Detection
   └── Report Generation
```

Example:

```text
POST /documents
      │
      ▼
202 Accepted
      │
      ▼
Job ID
      │
      ▼
Worker
      │
      ▼
Completed
```

---

# 18. Data Storage Architecture

```text
PostgreSQL
    ↓
Application State

Neo4j
    ↓
Scientific Relationships

Qdrant
    ↓
Semantic Vectors

Redis
    ↓
Cache / Queue / Temporary State
```

Data ownership should remain explicit.

---

# 19. Security Boundary

```text
Internet
   │
   ▼
Frontend
   │
   ▼
API
   │
   ├── Authentication
   ├── Authorization
   ├── Rate Limiting
   └── Input Validation
   │
   ▼
Application
```

Secrets shall remain outside source control.

---

# 20. Observability

DiscoveryAI should support:

```text
Logs
Metrics
Traces
Audit Logs
```

AI execution traces should support:

```text
User Query
 ↓
Retrieved Evidence
 ↓
LLM Call
 ↓
Generated Claim
 ↓
Validation
 ↓
Final Result
```

This supports debugging, reproducibility, and evidence verification.

---

# 21. Repository Architecture

Planned structure:

```text
DiscoveryAI/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── modules/
│   │   │   ├── ingestion/
│   │   │   ├── extraction/
│   │   │   ├── retrieval/
│   │   │   ├── knowledge_graph/
│   │   │   ├── gap_detection/
│   │   │   ├── evidence/
│   │   │   ├── trends/
│   │   │   ├── hypothesis/
│   │   │   └── experiments/
│   │   └── main.py
│   │
│   └── tests/
│
├── frontend/
├── research/
├── data/
├── scripts/
├── docker/
├── tests/
├── README.md
└── .gitignore
```

This structure is architectural guidance for later implementation; unnecessary directories should not be created before their corresponding development phase.

---

# 22. Scalability Strategy

The initial architecture will use clear internal module boundaries and asynchronous workers.

Individual components may later be extracted into independent services when justified by:

* Independent scaling requirements
* Independent deployment requirements
* Fault isolation requirements
* Team ownership
* Runtime requirements

The system should not introduce distributed services without a concrete architectural reason.

---

# 23. Architecture Quality Goals

The architecture should optimize for:

* Scientific correctness
* Evidence traceability
* Modularity
* Testability
* Reproducibility
* Maintainability
* Scalability
* Observability
* Security

---

# 24. Architecture Completion Criteria

Day 5 is complete when:

* [ ] High-level architecture is defined.
* [ ] Presentation layer is defined.
* [ ] API layer is defined.
* [ ] Application/orchestration layer is defined.
* [ ] Scientific document pipeline is defined.
* [ ] AI/ML layer is defined.
* [ ] Knowledge layer is defined.
* [ ] Hybrid retrieval flow is defined.
* [ ] Research gap engine is defined.
* [ ] Evidence validation flow is defined.
* [ ] Temporal intelligence is defined.
* [ ] Hypothesis and experiment flow is defined.
* [ ] Agent boundaries are defined.
* [ ] Background processing is defined.
* [ ] Database responsibilities are defined.
* [ ] Security boundary is defined.
* [ ] Observability is defined.
* [ ] Repository architecture is planned.
* [ ] Scalability strategy is documented.
* [ ] `research/architecture.md` is created.
* [ ] Architecture decisions are documented separately.
* [ ] Changes are committed to GitHub.
