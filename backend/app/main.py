from fastapi import FastAPI

from app.core.config import settings
from app.core.environment import validate_environment
from app.core.logging import configure_logging, get_logger

validate_environment()
configure_logging()

logger = get_logger(__name__)

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
    }
