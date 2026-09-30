from .config import settings


ALLOWED_ENVIRONMENTS = {"development", "production", "test"}


def validate_environment() -> None:
    environment = settings.app_env.lower()
    if environment not in ALLOWED_ENVIRONMENTS:
        raise ValueError(
            f"Unsupported APP_ENV={settings.app_env!r}. "
            f"Expected one of: {sorted(ALLOWED_ENVIRONMENTS)}"
        )

    if settings.is_production and settings.debug:
        raise ValueError("DEBUG must be false when APP_ENV=production")

    if settings.is_production and settings.neo4j_password.get_secret_value() == "change-me":
        raise ValueError("NEO4J_PASSWORD must be changed in production")
