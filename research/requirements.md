# DiscoveryAI — System Requirements Specification

## 1. Purpose

This document defines the functional, AI/ML, data, security, performance, and research requirements for DiscoveryAI.

The purpose of the requirements specification is to establish a clear and testable foundation for the architecture and implementation of the system.

Requirements are intended to guide implementation, testing, evaluation, and later architectural decisions.

---

# 2. System Objective

DiscoveryAI is intended to analyze scientific literature and identify evidence-grounded research opportunities.

The system should support:

```text
Scientific Document Understanding
        ↓
Scientific Knowledge Representation
        ↓
Hybrid Retrieval
        ↓
Research Landscape Analysis
        ↓
Research Gap Detection
        ↓
Evidence Validation
        ↓
Research Opportunity Assessment
        ↓
Hypothesis Generation
        ↓
Experiment Planning
```

---

# 3. Functional Requirements

## FR-01 — Scientific Document Ingestion

The system shall allow scientific documents to be ingested into the platform.

Initial supported inputs:

* PDF documents
* Abstracts
* Scientific metadata
* References

Future inputs may include technical reports, patents, and datasets.

---

## FR-02 — Scientific Document Parsing

The system shall extract relevant document information including:

* Title
* Authors
* Abstract
* Sections
* References
* Tables
* Figure metadata
* Publication year
* DOI or other identifiers

---

## FR-03 — Scientific Information Extraction

The system shall identify scientific entities including:

* Paper
* Author
* Institution
* Topic
* Method
* Dataset
* Problem
* Application
* Metric
* Experiment
* Domain

---

## FR-04 — Scientific Relationship Extraction

The system shall identify relationships including:

```text
USES
EVALUATED_ON
ADDRESSES
USES_METRIC
APPLIED_TO
AUTHORED_BY
AFFILIATED_WITH
CITES
MENTIONS_LIMITATION
PROPOSES_FUTURE_WORK
```

---

## FR-05 — Knowledge Graph Construction

The system shall construct a structured scientific knowledge graph from extracted entities and relationships.

---

## FR-06 — Vector Indexing

The system shall generate embeddings for relevant scientific content and store them in a vector database.

---

## FR-07 — Natural Language Research Search

The system shall allow users to submit scientific research questions using natural language.

---

## FR-08 — Hybrid Retrieval

The system shall support retrieval using both:

```text
Vector similarity
+
Knowledge graph relationships
```

---

## FR-09 — Research Gap Detection

The system shall generate candidate research gaps across multiple categories:

* Topic gap
* Dataset gap
* Benchmark gap
* Experiment gap
* Evaluation gap
* Application gap
* Interdisciplinary gap

---

## FR-10 — Supporting Evidence Retrieval

The system shall retrieve evidence supporting candidate research gaps.

---

## FR-11 — Contradictory Evidence Retrieval

The system shall search for evidence that challenges candidate research gaps.

---

## FR-12 — Temporal Research Analysis

The system shall analyze temporal research signals including:

* Publication frequency
* Topic growth
* Method adoption
* Dataset usage
* Citation trends
* Research concentration
* Research stagnation
* Emerging topics

---

## FR-13 — Research Opportunity Assessment

The system shall produce an explainable assessment containing:

* Candidate opportunity
* Gap type
* Supporting evidence
* Contradictory evidence
* Research density
* Temporal evidence
* Confidence

---

## FR-14 — Hypothesis Generation

The system shall generate candidate scientific hypotheses from validated research opportunities.

---

## FR-15 — Experiment Planning

The system shall generate experiment plans containing:

* Research question
* Hypothesis
* Dataset
* Baseline
* Method
* Metrics
* Experimental setup
* Expected challenges

---

## FR-16 — Research Report Generation

The system shall generate structured research reports containing:

* Research opportunity
* Gap explanation
* Evidence
* Contradictory evidence
* Confidence
* Hypothesis
* Experiment plan
* References

---

# 4. AI/ML Requirements

## ML-01 — Model Provider Abstraction

The system shall provide a common abstraction for multiple LLM providers.

Initial target providers:

```text
Ollama
OpenAI
Gemini
Claude
```

The core application should not depend on a single provider.

---

## ML-02 — Configurable Embeddings

The embedding model shall be configurable.

The final model selection will be determined through later empirical evaluation.

---

## ML-03 — Structured Scientific Extraction

Scientific information extraction should produce structured outputs rather than unrestricted natural-language output.

Example:

```json
{
  "methods": [],
  "datasets": [],
  "problems": [],
  "metrics": [],
  "limitations": [],
  "future_work": []
}
```

---

## ML-04 — Evidence Grounding

Important generated scientific claims should be linked to retrieved evidence whenever evidence is available.

---

## ML-05 — Confidence Information

The system shall maintain confidence information for important extracted and generated results.

---

## ML-06 — Unsupported Claim Reduction

The system shall use retrieval, evidence linking, contradiction checking, and research criticism to reduce unsupported scientific claims.

---

## ML-07 — Experiment Reproducibility

The system shall record relevant model configuration including:

* Model name
* Model version
* Prompt configuration
* Temperature or equivalent generation parameters
* Retrieval configuration
* Embedding model
* Timestamp

---

# 5. Data and Database Requirements

## DB-01 — PostgreSQL

PostgreSQL shall store structured application data such as:

* Users
* Projects
* Document metadata
* Processing jobs
* Experiments
* Reports
* Audit information

---

## DB-02 — Neo4j

Neo4j shall store and support reasoning over the scientific knowledge graph.

---

## DB-03 — Qdrant

Qdrant shall store scientific embeddings and support semantic retrieval.

---

## DB-04 — Redis

Redis may be used for:

* Caching
* Temporary state
* Task coordination
* Queue support

---

## DB-05 — Data Provenance

Scientific entities and important generated results should preserve provenance linking them to source documents and, where possible, source sections or passages.

Example:

```text
Entity
 ↓
Source Document
 ↓
Source Section
 ↓
Source Passage
```

---

# 6. Security Requirements

## SEC-01 — Authentication

Protected system functionality shall require authentication.

---

## SEC-02 — Authorization

The system shall support role-based access control.

Initial roles:

```text
Admin
Researcher
User
```

---

## SEC-03 — Credential Protection

Passwords shall never be stored as plaintext.

---

## SEC-04 — API Protection

API endpoints shall support appropriate:

* Authentication
* Authorization
* Input validation
* Rate limiting

---

## SEC-05 — Secret Management

API keys and credentials shall not be committed to source control.

Secrets shall be supplied through environment variables or an appropriate secret-management mechanism.

---

## SEC-06 — Audit Logging

Security-sensitive and important system actions should be auditable.

Examples:

* Login
* Document upload
* Research search
* Gap generation
* Report generation
* Administrative changes

---

## SEC-07 — Data Privacy

User-specific data shall not be exposed to unauthorized users.

---

# 7. Performance and Scalability Requirements

## PERF-01 — Research Search Latency

The initial target for a normal indexed research query is:

```text
< 5 seconds
```

excluding unusually expensive long-running analyses.

This is an initial engineering target and may be revised after benchmarking.

---

## PERF-02 — Asynchronous Processing

Large or computationally expensive tasks shall be processed asynchronously.

Example:

```text
Upload
  ↓
Job Queue
  ↓
Processing
  ↓
Status Tracking
  ↓
Completion
```

---

## PERF-03 — Scalable Architecture

The architecture should support increasing:

* Number of documents
* Number of users
* Query volume
* Knowledge graph size
* Embedding collection size

without requiring a complete system redesign.

---

## PERF-04 — Background Processing

Expensive operations should support background execution, including:

* PDF processing
* Embedding generation
* Knowledge graph construction
* Trend analysis
* Large-scale gap detection
* Report generation

---

## PERF-05 — Caching

Repeated computationally expensive operations should support caching where caching does not compromise scientific correctness or evidence freshness.

---

# 8. Research and Evaluation Requirements

## RES-01 — Information Extraction Evaluation

Scientific entity and relationship extraction shall be evaluated using:

* Precision
* Recall
* F1

---

## RES-02 — Retrieval Evaluation

Retrieval performance shall be evaluated using:

* Recall@K
* Precision@K
* MRR
* nDCG

---

## RES-03 — Research Gap Evaluation

Research-gap detection shall be evaluated using appropriate ranking and classification metrics including:

* Precision@K
* Recall@K
* F1
* nDCG
* False Discovery Rate

---

## RES-04 — Evidence Evaluation

The system shall be evaluated for:

* Evidence coverage
* Citation correctness
* Unsupported claim rate
* Contradiction detection

---

## RES-05 — Expert Evaluation

Experts may evaluate candidate research opportunities using dimensions including:

* Novelty
* Relevance
* Feasibility
* Impact
* Evidence quality

These dimensions are evaluation criteria and not predetermined system scores.

---

## RES-06 — Baseline Comparison

DiscoveryAI shall be evaluated against progressively stronger baselines:

```text
LLM-only
Vector RAG
GraphRAG
Hybrid RAG
DiscoveryAI
```

---

## RES-07 — Ablation Studies

The system shall support evaluation of component contributions through ablations including:

```text
Full DiscoveryAI
DiscoveryAI - Knowledge Graph
DiscoveryAI - Vector Retrieval
DiscoveryAI - Temporal Analysis
DiscoveryAI - Evidence Validation
DiscoveryAI - Research Critic
```

---

## RES-08 — Reproducibility

Research experiments should record:

* Dataset version
* Corpus
* Model
* Prompt
* Model parameters
* Retrieval configuration
* Evaluation script
* Results

---

# 9. Requirement Priorities

Requirements shall be prioritized using:

```text
P0 = Critical
P1 = Important
P2 = Future
```

Initial priorities:

| Requirement Area                  | Priority |
| --------------------------------- | -------- |
| Scientific document ingestion     | P0       |
| Scientific information extraction | P0       |
| Knowledge graph                   | P0       |
| Vector retrieval                  | P0       |
| Hybrid retrieval                  | P0       |
| Research gap detection            | P0       |
| Evidence validation               | P0       |
| Authentication                    | P1       |
| Temporal analysis                 | P1       |
| Hypothesis generation             | P1       |
| Experiment planning               | P1       |
| Advanced collaboration features   | P2       |

---

# 10. Requirement Traceability

Each major requirement should eventually map to:

```text
Requirement
     ↓
Implementation
     ↓
Test
     ↓
Research Evaluation
```

Example:

```text
FR-09 Research Gap Detection
        ↓
Gap Detection Module
        ↓
Gap Detection Tests
        ↓
DiscoveryGapBench Evaluation
```

---

# 11. Out of Scope

The initial DiscoveryAI system will not guarantee:

* Discovery of every unknown research opportunity
* Proof that a research topic has never been investigated
* Universal coverage of all scientific literature
* Automatic scientific truth verification
* Autonomous laboratory experimentation
* Replacement of human scientific judgment

DiscoveryAI operates within its indexed corpus, retrieval capabilities, evidence coverage, and defined search scope.

---

# 12. Core Evidence Requirement

The system shall not convert absence of retrieved evidence into a universal claim.

Incorrect:

> Nobody has researched this.

Preferred:

> No relevant evidence was identified within the indexed corpus and search scope.

This requirement applies to research-gap detection, opportunity generation, and generated research reports.

---

# 13. Day 4 Completion Criteria

Day 4 is complete when:

* [ ] Functional requirements are defined.
* [ ] AI/ML requirements are defined.
* [ ] Database requirements are defined.
* [ ] Security requirements are defined.
* [ ] Performance requirements are defined.
* [ ] Research/evaluation requirements are defined.
* [ ] Requirement priorities are defined.
* [ ] Traceability approach is defined.
* [ ] Out-of-scope requirements are documented.
* [ ] `research/requirements.md` is created.
* [ ] Document is committed to GitHub.

---

# 14. Day 4 Final Principle

DiscoveryAI should not be implemented directly from the feature list.

The development sequence should be:

```text
Requirement
    ↓
Design
    ↓
Implementation
    ↓
Unit Test
    ↓
System Test
    ↓
Research Evaluation
    ↓
Evidence
```

The requirements document therefore acts as the bridge between the research specification and the future system architecture.
