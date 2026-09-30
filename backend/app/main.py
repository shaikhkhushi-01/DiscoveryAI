from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import router
from app.api.auth import router as auth_router
from app.api.protected import router as protected_router
from app.core.config import settings
from app.core.environment import validate_environment
from app.core.errors import (
    DiscoveryAIError,
    discoveryai_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
)
from app.core.logging import configure_logging, get_logger
from app.core.middleware import request_logging_middleware

validate_environment()
configure_logging()

logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Research-grade AI system for scientific knowledge reasoning and research opportunity discovery.",
)

app.middleware("http")(request_logging_middleware)
app.add_exception_handler(DiscoveryAIError, discoveryai_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(router)
app.include_router(auth_router)
app.include_router(protected_router)


@app.get("/health", tags=["system"])
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
    }
