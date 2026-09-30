from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import router
from app.api.auth import router as auth_router
from app.api.protected import router as protected_router
from app.api.documents import router as documents_router
from app.api.extraction import router as extraction_router
from app.api.discovery import router as discovery_router
from app.api.search import router as search_router
from app.api.rag import router as rag_router
from app.api.knowledge_graph import router as knowledge_graph_router
from app.api.graph_rag import router as graph_rag_router
from app.api.gaps import router as gaps_router
from app.api.evidence import router as evidence_router
from app.api.trends import router as trends_router
from app.api.agents import router as agents_router
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

app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.middleware("http")(request_logging_middleware)
app.add_exception_handler(DiscoveryAIError, discoveryai_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(router)
app.include_router(auth_router)
app.include_router(protected_router)
app.include_router(documents_router)
app.include_router(extraction_router)
app.include_router(discovery_router)
app.include_router(search_router)
app.include_router(rag_router)
app.include_router(knowledge_graph_router)
app.include_router(graph_rag_router)
app.include_router(gaps_router)
app.include_router(evidence_router)
app.include_router(trends_router)
app.include_router(agents_router)


@app.get("/health", tags=["system"])
def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
    }
