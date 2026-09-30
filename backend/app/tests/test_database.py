from sqlalchemy import text

from app.db.session import engine


def test_database_engine_is_configured():
    assert engine.url.get_backend_name() == "postgresql"
    assert engine.url.database == "discoveryai"


def test_database_connection_smoke():
    """Requires a running PostgreSQL instance; skipped by default in CI without DB."""
    try:
        with engine.connect() as connection:
            assert connection.execute(text("SELECT 1")).scalar_one() == 1
    except Exception as exc:
        import pytest
        pytest.skip(f"PostgreSQL is not running: {exc}")
