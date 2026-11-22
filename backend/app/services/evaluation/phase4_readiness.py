from __future__ import annotations

"""Read-only readiness checks for live Phase 4 integrations.

The report contains connection state and aggregate counts only. It never returns
connection strings, API keys, passwords, or source-paper content.
"""

import importlib.util
from typing import Any

import httpx
from sqlalchemy import func, select

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.document import Document
from app.models.paper import Paper
from app.services.knowledge_graph.neo4j import get_driver
from app.services.vector_store import get_qdrant


def _check_database() -> dict[str, Any]:
    db = SessionLocal()
    try:
        papers = int(db.scalar(select(func.count()).select_from(Paper)) or 0)
        documents = int(db.scalar(select(func.count()).select_from(Document)) or 0)
        statuses = {
            str(status or "unknown"): int(count)
            for status, count in db.execute(
                select(Document.status, func.count()).group_by(Document.status)
            ).all()
        }
        return {
            "status": "connected",
            "papers": papers,
            "documents": documents,
            "document_status_counts": statuses,
            "ready": papers > 0 and documents > 0,
        }
    finally:
        db.close()


def _check_qdrant() -> dict[str, Any]:
    client = get_qdrant()
    collections = client.get_collections()
    names = sorted(item.name for item in collections.collections)
    collection_name = settings.qdrant_collection
    if collection_name not in names:
        return {
            "status": "connected",
            "collection": collection_name,
            "available_collections": names,
            "points": 0,
            "ready": False,
            "reason": "configured_collection_missing",
        }
    info = client.get_collection(collection_name=collection_name)
    count = client.count(collection_name=collection_name, exact=True)
    points = int(count.count)
    return {
        "status": "connected",
        "collection": collection_name,
        "points": points,
        "ready": points > 0,
    }


def _check_neo4j() -> dict[str, Any]:
    driver = get_driver()
    driver.verify_connectivity()
    with driver.session(database=settings.neo4j_database) as session:
        papers = int(session.run("MATCH (p:Paper) RETURN count(p) AS n").single()["n"])
        nodes = int(session.run("MATCH (n) RETURN count(n) AS n").single()["n"])
        relationships = int(session.run("MATCH ()-[r]->() RETURN count(r) AS n").single()["n"])
    return {
        "status": "connected",
        "paper_nodes": papers,
        "nodes": nodes,
        "relationships": relationships,
        "ready": papers > 0 and relationships > 0,
    }


def _check_llm_provider() -> dict[str, Any]:
    provider = settings.llm_provider.strip().lower()
    if provider == "gemini":
        configured = bool(settings.gemini_api_key and settings.gemini_api_key.get_secret_value())
        return {
            "status": "configured" if configured else "missing_credential",
            "provider": provider,
            "model": settings.gemini_model,
            "credential_present": configured,
            "ready": configured,
            "note": "Credential presence only; no billable generation request was sent.",
        }
    if provider == "openai":
        configured = bool(settings.openai_api_key and settings.openai_api_key.get_secret_value())
        return {
            "status": "configured" if configured else "missing_credential",
            "provider": provider,
            "model": settings.openai_model,
            "credential_present": configured,
            "ready": configured,
            "note": "Credential presence only; no billable generation request was sent.",
        }
    if provider == "ollama":
        try:
            response = httpx.get(f"{settings.ollama_base_url.rstrip('/')}/api/tags", timeout=3.0)
            response.raise_for_status()
            data = response.json()
            models = [
                str(row.get("name"))
                for row in data.get("models", [])
                if isinstance(row, dict) and row.get("name")
            ]
            return {
                "status": "connected",
                "provider": provider,
                "available_models": models,
                "ready": bool(models),
            }
        except Exception:
            return {
                "status": "unreachable",
                "provider": provider,
                "ready": False,
                "reason": "Ollama tags endpoint did not respond successfully.",
            }
    return {
        "status": "unsupported",
        "provider": provider,
        "ready": False,
    }


def _check_embedding_provider() -> dict[str, Any]:
    provider = settings.embedding_provider.strip().lower()
    if provider == "sentence-transformers":
        available = importlib.util.find_spec("sentence_transformers") is not None
        return {
            "status": "installed" if available else "package_missing",
            "provider": provider,
            "model": settings.embedding_model,
            "ready": available,
            "note": "Package presence only; model weights are not downloaded or loaded by this check.",
        }
    if provider == "gemini":
        configured = bool(settings.gemini_api_key and settings.gemini_api_key.get_secret_value())
        return {
            "status": "configured" if configured else "missing_credential",
            "provider": provider,
            "model": settings.gemini_embedding_model,
            "credential_present": configured,
            "ready": configured,
            "note": "Credential presence only; no embedding request was sent.",
        }
    return {"status": "unsupported", "provider": provider, "ready": False}


def run_phase4_readiness() -> dict[str, Any]:
    """Check configured services independently and return a secret-free report."""
    checks: dict[str, Any] = {}
    checkers = {
        "database": _check_database,
        "qdrant": _check_qdrant,
        "neo4j": _check_neo4j,
        "llm_provider": _check_llm_provider,
        "embedding_provider": _check_embedding_provider,
    }
    for name, checker in checkers.items():
        try:
            checks[name] = checker()
        except Exception as exc:
            checks[name] = {
                "status": "error",
                "ready": False,
                "error_type": type(exc).__name__,
                "reason": "Check failed; inspect service logs without exposing credentials.",
            }
    required = list(checkers)
    ready = all(bool(checks[name].get("ready")) for name in required)
    return {
        "schema_version": "1.0",
        "purpose": "read_only_phase4_live_integration_preflight",
        "ready": ready,
        "checks": checks,
        "blocked_checks": [name for name in required if not checks[name].get("ready")],
        "safety": {
            "read_only": True,
            "secrets_emitted": False,
            "llm_generation_requested": False,
            "embedding_requested": False,
            "qdrant_or_neo4j_schema_mutated": False,
        },
        "interpretation": (
            "Ready means the configured dependencies and non-empty indexes are reachable; "
            "it does not prove prediction quality or complete a benchmark experiment."
        ),
    }
