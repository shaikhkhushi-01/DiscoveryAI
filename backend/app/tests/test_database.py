from sqlalchemy import text

from app.db.session import engine


def test_database_engine_is_configured():
    # CI intentionally uses SQLite; production uses PostgreSQL.
    assert engine.url.get_backend_name() in {"postgresql", "sqlite"}
    if engine.url.get_backend_name() == "postgresql":
        assert engine.url.database == "discoveryai"


def test_database_connection_smoke():
    """Smoke-test whichever database backend is configured."""
    with engine.connect() as connection:
        assert connection.execute(text("SELECT 1")).scalar_one() == 1
