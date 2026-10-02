from functools import lru_cache
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from app.core.config import settings


@lru_cache
def get_qdrant():
    from qdrant_client import QdrantClient
    return QdrantClient(url=settings.qdrant_url)

def ensure_collection(dimension: int) -> None:
    from qdrant_client.models import Distance, VectorParams
    client = get_qdrant()
    collections = {item.name for item in client.get_collections().collections}
    if settings.qdrant_collection not in collections:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
        )

def upsert_chunks(chunks: list[dict[str, Any]], vectors: list[list[float]]) -> int:
    if not chunks:
        return 0
    from qdrant_client.models import PointStruct
    ensure_collection(len(vectors[0]))
    points = []
    for index, (chunk, vector) in enumerate(zip(chunks, vectors)):
        points.append(PointStruct(
            id=str(uuid5(NAMESPACE_URL, f"discoveryai:{chunk['document_id']}:{chunk['chunk_id']}:{index}")),
            vector=vector,
            payload={
                "document_id": chunk["document_id"], "paper_id": chunk.get("paper_id"),
                "year": chunk.get("year"), "topics": chunk.get("topics", []),
                "datasets": chunk.get("datasets", []), "chunk_id": chunk["chunk_id"],
                "section": chunk.get("section"), "text": chunk.get("text", ""),
            },
        ))
    get_qdrant().upsert(collection_name=settings.qdrant_collection, points=points)
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
    hits = get_qdrant().search(collection_name=settings.qdrant_collection, query_vector=vector, limit=max(1, min(limit, 50)), query_filter=query_filter)
    return [{"score": hit.score, **(hit.payload or {})} for hit in hits]
