# Day 13 — Core Models

## Implemented
- User model
- Role model
- Organization model
- Project model
- SQLAlchemy relationships and foreign keys
- Alembic migration `0002_core_models`
- ORM metadata registration
- Model structure tests

## Relationships
- User → Role
- User → Organization (optional)
- Project → Organization
- Project → User (owner)

Password hashing and authentication are intentionally deferred to Day 14.

## Validation
```bash
cd backend
pytest app/tests/test_models.py
alembic upgrade head
```
Runtime execution requires PostgreSQL and is not claimed as executed through GitHub repository operations.
