from functools import lru_cache
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import settings


@lru_cache
def get_qdrant() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url)


def ensure_collection(dimension: int) -> None:
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
    ensure_collection(len(vectors[0]))
    points = []
    for index, (chunk, vector) in enumerate(zip(chunks, vectors)):
        points.append(
            PointStruct(
                id=f"{chunk['document_id']}:{chunk['chunk_id']}:{index}",
                vector=vector,
                payload={
                    "document_id": chunk["document_id"],
                    "chunk_id": chunk["chunk_id"],
                    "section": chunk.get("section"),
                    "text": chunk.get("text", ""),
                },
            )
        )
    get_qdrant().upsert(collection_name=settings.qdrant_collection, points=points)
    return len(points)


def search_vectors(vector: list[float], limit: int = 10) -> list[dict[str, Any]]:
    ensure_collection(len(vector))
    hits = get_qdrant().search(
        collection_name=settings.qdrant_collection,
        query_vector=vector,
        limit=max(1, min(limit, 50)),
    )
    return [{"score": hit.score, **(hit.payload or {})} for hit in hits]
