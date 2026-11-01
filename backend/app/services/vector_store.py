from functools import lru_cache
import logging
import time
from typing import Any, Callable, TypeVar
from uuid import NAMESPACE_URL, uuid5

from app.core.config import settings

logger = logging.getLogger(__name__)
T = TypeVar("T")
QDRANT_REQUEST_ATTEMPTS = 3


def _with_qdrant_retry(operation: str, action: Callable[[], T]) -> T:
    """Retry transient Qdrant transport failures with short exponential backoff."""
    for attempt in range(1, QDRANT_REQUEST_ATTEMPTS + 1):
        try:
            return action()
        except Exception:
            if attempt == QDRANT_REQUEST_ATTEMPTS:
                raise
            delay = 2 ** (attempt - 1)
            logger.warning(
                "Qdrant %s request failed; retrying attempt=%s/%s delay_seconds=%s",
                operation, attempt, QDRANT_REQUEST_ATTEMPTS, delay,
                exc_info=True,
            )
            time.sleep(delay)
    raise RuntimeError(f"Qdrant {operation} failed after retries")


@lru_cache
def get_qdrant():
    from qdrant_client import QdrantClient

    api_key = settings.qdrant_api_key.get_secret_value() if settings.qdrant_api_key else None
    # Cloud requests can take longer than the client's short default timeout,
    # especially while a free-tier cluster is waking up.
    return QdrantClient(url=settings.qdrant_url, api_key=api_key, timeout=30)


def check_qdrant_connection() -> dict[str, Any]:
    """Perform a read-only connectivity check without exposing credentials."""
    response = _with_qdrant_retry(
        "connectivity check",
        lambda: get_qdrant().get_collections(),
    )
    names = [item.name for item in response.collections]
    return {"status": "connected", "collection_count": len(names), "collections": names}


def ensure_collection(dimension: int) -> None:
    from qdrant_client.models import Distance, PayloadSchemaType, VectorParams

    client = get_qdrant()
    collections = _with_qdrant_retry(
        "list collections",
        lambda: client.get_collections(),
    )
    names = {item.name for item in collections.collections}
    if settings.qdrant_collection not in names:
        _with_qdrant_retry(
            "create collection",
            lambda: client.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
            ),
        )

    # Qdrant requires payload indexes for fields used by filtered vector search.
    # Create these idempotently so existing collections are repaired too.
    for field_name, field_schema in (
        ("topics", PayloadSchemaType.KEYWORD),
        ("datasets", PayloadSchemaType.KEYWORD),
        ("year", PayloadSchemaType.INTEGER),
    ):
        _with_qdrant_retry(
            f"create payload index {field_name}",
            lambda field_name=field_name, field_schema=field_schema: client.create_payload_index(
                collection_name=settings.qdrant_collection,
                field_name=field_name,
                field_schema=field_schema,
                wait=True,
            ),
        )


def upsert_chunks(chunks: list[dict[str, Any]], vectors: list[list[float]]) -> int:
    if not chunks:
        return 0
    from qdrant_client.models import PointStruct

    if not vectors or len(chunks) != len(vectors):
        raise ValueError("Qdrant upsert requires one embedding vector per chunk")
    ensure_collection(len(vectors[0]))
    points = []
    for index, (chunk, vector) in enumerate(zip(chunks, vectors)):
        points.append(
            PointStruct(
                id=str(uuid5(NAMESPACE_URL, f"discoveryai:{chunk['document_id']}:{chunk['chunk_id']}:{index}")),
                vector=vector,
                payload={
                    "document_id": chunk["document_id"],
                    "paper_id": chunk.get("paper_id"),
                    "year": chunk.get("year"),
                    "topics": chunk.get("topics", []),
                    "datasets": chunk.get("datasets", []),
                    "chunk_id": chunk["chunk_id"],
                    "section": chunk.get("section"),
                    "text": chunk.get("text", ""),
                },
            )
        )
    _with_qdrant_retry(
        "upsert points",
        lambda: get_qdrant().upsert(collection_name=settings.qdrant_collection, points=points),
    )
    return len(points)


def search_vectors(vector: list[float], limit: int = 10, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    from qdrant_client.models import FieldCondition, Filter, MatchAny, MatchValue

    ensure_collection(len(vector))
    conditions = []
    for key in ("year", "topic", "dataset"):
        value = (filters or {}).get(key)
        if value is not None:
            match = MatchAny(any=[value]) if key in {"topic", "dataset"} else MatchValue(value=value)
            payload_key = {"topic": "topics", "dataset": "datasets"}.get(key, key)
            conditions.append(FieldCondition(key=payload_key, match=match))
    query_filter = Filter(must=conditions) if conditions else None
    hits = _with_qdrant_retry(
        "vector search",
        lambda: get_qdrant().search(
            collection_name=settings.qdrant_collection,
            query_vector=vector,
            limit=max(1, min(limit, 50)),
            query_filter=query_filter,
        ),
    )
    return [{"score": hit.score, **(hit.payload or {})} for hit in hits]
