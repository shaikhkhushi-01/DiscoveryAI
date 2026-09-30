from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.services.document_ingestion import process_pdf
from app.services.embeddings.factory import get_embedding_provider
from app.services.vector_store import search_vectors, upsert_chunks

router = APIRouter(prefix="/api/v1/search", tags=["semantic-search"])


@router.post("/index/{document_id}")
def index_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if not document.storage_uri:
        raise HTTPException(status_code=422, detail="Document has no stored PDF")

    parsed = process_pdf(Path(document.storage_uri))
    chunks = [
        {**chunk, "document_id": document.id}
        for chunk in parsed.get("chunks", [])
        if chunk.get("text")
    ]
    provider = get_embedding_provider()
    vectors = provider.embed([chunk["text"] for chunk in chunks])
    indexed = upsert_chunks(chunks, vectors)
    return {
        "source": "qdrant",
        "document_id": document.id,
        "indexed_chunks": indexed,
        "collection": "scientific_chunks",
    }


@router.get("/semantic")
def semantic_search(
    q: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
):
    query = q.strip()
    if not query:
        return {"source": "qdrant", "items": []}

    provider = get_embedding_provider()
    vector = provider.embed([query])[0]
    return {
        "source": "qdrant",
        "query": query,
        "items": search_vectors(vector, limit=limit),
    }
