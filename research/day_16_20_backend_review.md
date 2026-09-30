# Days 16–20 — Backend Foundation Review

## Day 16
Paper, Document, Author, and Institution models added.

## Day 17
Dataset, Method, Topic, Problem, and Application models added.

## Day 18
ResearchGap, Hypothesis, Experiment, and Metric models added with Alembic revision `0003_scientific_models`.

## Day 19
Scientific response schemas added. FastAPI versioned routes and generated Swagger/OpenAPI documentation are available through `/docs` and `/openapi.json`.

## Day 20
Scientific model unit tests and authentication tests added. Alembic metadata discovery was hardened so all ORM models are loaded during migration generation/execution.

## Validation commands
```bash
cd backend
pytest app/tests
alembic upgrade head
```

Runtime execution is not claimed through GitHub repository operations.
