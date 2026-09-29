# DiscoveryAI — Architecture Decisions

## ADR-001 — Modular Architecture

### Decision

DiscoveryAI will use a modular architecture with explicit internal component boundaries.

### Reason

The system contains multiple scientific and AI capabilities that require independent testing and evolution.

The architecture should avoid tightly coupling:

* Document processing
* Retrieval
* Knowledge graph construction
* Gap detection
* Evidence validation
* Trend analysis
* Hypothesis generation
* Experiment planning

---

## ADR-002 — Avoid Premature Microservices

### Decision

The initial implementation will not split every module into an independent microservice.

### Reason

The system is still discovering its domain boundaries. Excessive early distribution would introduce additional operational complexity, network failures, deployment complexity, and debugging overhead.

Instead, modules will maintain explicit interfaces so that selected components can be extracted later if required.

---

## ADR-003 — Hybrid Retrieval

### Decision

DiscoveryAI will combine vector retrieval with knowledge graph retrieval.

### Reason

Scientific research questions may require both semantic similarity and structured relationship reasoning.

Vector retrieval provides semantic evidence while graph retrieval provides structural context.

---

## ADR-004 — Separate Vector and Graph Stores

### Decision

Qdrant will be used for vector retrieval and Neo4j for scientific graph relationships.

### Reason

The two systems serve different data-access patterns:

```text
Qdrant
→ semantic similarity

Neo4j
→ graph relationships and multi-hop reasoning
```

---

## ADR-005 — Asynchronous Processing

### Decision

Expensive scientific processing will use background workers.

### Reason

PDF processing, embedding generation, knowledge graph construction, trend analysis, and large-scale gap detection may exceed normal API request latency.

---

## ADR-006 — LLM Provider Abstraction

### Decision

LLM providers will be accessed through a common provider interface.

### Reason

DiscoveryAI should not be architecturally locked to a single model provider.

The system should support experimentation with different models and local inference.

---

## ADR-007 — Evidence Provenance

### Decision

Scientific results should retain provenance to source documents and, where possible, source sections or passages.

### Reason

Research-gap discovery is an evidence-sensitive task. Provenance supports verification, debugging, reproducibility, and citation correctness.

---

## ADR-008 — Evidence Validation Before Opportunity Reporting

### Decision

Candidate research gaps should pass through supporting-evidence search, contradictory-evidence search, and research criticism before being presented as validated opportunities.

### Reason

Absence of retrieved evidence is not proof of universal research absence.

The system must reason within the indexed corpus and search scope.

---

## ADR-009 — Future Service Extraction

### Decision

Modules should expose clear interfaces that permit future extraction into independent services where justified.

### Extraction triggers

Potential triggers include:

* Independent scaling
* Independent deployment
* Fault isolation
* Different runtime requirements
* Organizational ownership

No module should be extracted merely because microservices are considered more advanced.

---

## ADR-010 — Observability

### Decision

DiscoveryAI will maintain logs, metrics, traces, and audit information.

### Reason

A multi-stage AI research pipeline must make its intermediate operations observable for debugging, evaluation, and reproducibility.

---

# Decision Summary

```text
Architecture Style
→ Modular

Deployment Strategy
→ Initially consolidated application + workers

Retrieval
→ Vector + Graph

Vector Store
→ Qdrant

Knowledge Graph
→ Neo4j

Application Database
→ PostgreSQL

Cache / Queue
→ Redis

LLM Integration
→ Provider abstraction

Scientific Validation
→ Evidence + Contradiction + Critic

Heavy Processing
→ Background workers

Future Scaling
→ Selective service extraction
```
