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

# 4. Backend Technolog
