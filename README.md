# DiscoveryAI

## AI for Scientific Discovery and Knowledge Gap Detection

DiscoveryAI is a research-oriented AI system designed to identify and validate potential research opportunities from scientific literature and related evidence.

The system goes beyond conventional paper search and question answering by combining:

* Scientific document intelligence
* Knowledge graphs
* Vector retrieval
* Hybrid GraphRAG
* Temporal research analysis
* Evidence validation
* Research gap detection
* Research opportunity scoring
* Hypothesis generation
* Experiment planning

## Research Question

> What important research opportunities can be identified from existing scientific evidence, and how can those opportunities be validated and explained without making unsupported claims about the absence of research?

## Core Principle

DiscoveryAI must never make an absolute claim such as:

> "Nobody has researched this."

Instead, the system should communicate evidence-bounded conclusions such as:

> "No relevant evidence was identified within the indexed corpus and search scope."

## Architecture

DiscoveryAI uses a modular architecture built around:

```text
Frontend
    ↓
FastAPI
    ↓
Application Orchestration
    ↓
Scientific AI / ML
    ↓
Hybrid Retrieval
    ↓
PostgreSQL + Neo4j + Qdrant
    ↓
Evidence Validation
    ↓
Gap Detection
    ↓
Research Opportunity
    ↓
Hypothesis + Experiment Planning
```

## Technology Stack

### Frontend

* Next.js
* React
* TypeScript

### Backend

* Python
* FastAPI
* Pydantic

### AI / ML

* PyTorch
* Hugging Face Transformers
* Sentence Transformers
* LangGraph

### Data

* PostgreSQL
* Neo4j
* Qdrant
* Redis

### Processing

* Celery
* PyMuPDF

### Infrastructure

* Docker
* Docker Compose
* GitHub Actions

## Repository Structure

```text
DiscoveryAI/
│
├── backend/
│   └── app/
│
├── frontend/
│
├── research/
│
├── data/
│
├── scripts/
│
├── tests/
│
├── docker/
│
├── .github/
│
├── .gitignore
├── .env.example
├── README.md
└── LICENSE
```

## Research Documentation

The `research/` directory contains the project's research foundation:

* `problem_statement.md`
* `existing_research.md`
* `novelty.md`
* `requirements.md`
* `architecture.md`
* `architecture_decisions.md`
* `technology_stack.md`

## Development Status

The project is being developed incrementally through a structured research and engineering roadmap.

Current phase:

**Research Foundation and System Design**

## Engineering Principle

Every major component should be:

* Modular
* Testable
* Observable
* Reproducible
* Evidence-grounded
* Replaceable when benchmarks justify an alternative

## Research Reproducibility

Experiments should record relevant configuration including:

* Model
* Model version
* Embedding model
* Retrieval configuration
* Prompt/version
* Corpus version
* Knowledge graph version
* Evaluation dataset
* Random seed where applicable
* Runtime configuration

## License

To be finalized according to the project's publication and distribution requirements.
