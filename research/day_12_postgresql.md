# Day 12 — PostgreSQL + SQLAlchemy + Alembic

## Roadmap scope
- PostgreSQL integration
- SQLAlchemy
- Alembic
- Initial migration

## Implementation
- `app/db/base.py` defines the SQLAlchemy declarative base.
- `app/db/session.py` creates the PostgreSQL engine and `SessionLocal` factory and exposes FastAPI-compatible `get_db()` dependency.
- `alembic.ini` configures migration discovery.
- `alembic/env.py` reads the existing `DATABASE_URL` configuration and targets SQLAlchemy metadata.
- `alembic/versions/0001_initial.py` establishes the first migration revision.
- PostgreSQL dependencies are pinned in `backend/requirements.txt`.

## Validation
Run from `backend/` after starting PostgreSQL:

```bash
alembic upgrade head
pytest app/tests/test_database.py
```

The migration is intentionally minimal because domain models are scheduled for Days 13–18. No user, paper, or scientific entity tables are introduced early.

## Runtime note
GitHub repository operations do not execute the local Docker/PostgreSQL environment, so migration execution is documented but not claimed as locally run.
