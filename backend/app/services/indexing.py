from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.document import Document
from app.models.indexing_job import IndexingJob
from app.services.embeddings.factory import get_embedding_provider
from app.services.knowledge_graph.ingest import index_extraction
from app.services.vector_store import upsert_chunks

MAX_ATTEMPTS = 3
EMBED_BATCH_SIZE = 8


def enqueue_indexing(db: Session, document_id: int) -> IndexingJob:
    job = db.scalar(select(IndexingJob).where(IndexingJob.document_id == document_id))
    now = datetime.now(timezone.utc)
    if job is None:
        job = IndexingJob(document_id=document_id)
        db.add(job)
    else:
        job.status = "queued"
        job.attempts = 0
        job.vector_status = "pending"
        job.graph_status = "pending"
        job.last_error = None
        job.queued_at = now
        job.started_at = None
        job.completed_at = None
    db.flush()
    return job


def get_indexing_job(db: Session, document_id: int) -> IndexingJob | None:
    return db.scalar(select(IndexingJob).where(IndexingJob.document_id == document_id))


def claim_next_job(db: Session) -> int | None:
    job = db.scalar(
        select(IndexingJob)
        .where(IndexingJob.status.in_(["queued", "retry"]))
        .where(IndexingJob.attempts < MAX_ATTEMPTS)
        .order_by(IndexingJob.queued_at, IndexingJob.id)
        .with_for_update(skip_locked=True)
    )
    if job is None:
        return None
    job.status = "running"
    job.attempts += 1
    job.started_at = datetime.now(timezone.utc)
    job.updated_at = datetime.now(timezone.utc)
    db.commit()
    return job.id


def _load_payload(document: Document) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    try:
        metadata = json.loads(document.metadata_json or "{}")
    except json.JSONDecodeError as exc:
        raise ValueError("Stored document metadata is invalid") from exc

    extraction = metadata.get("extraction")
    if not isinstance(extraction, dict):
        raise ValueError("Document has no scientific extraction to index")

    chunks = metadata.get("chunks") or []
    if not isinstance(chunks, list):
        raise ValueError("Stored document chunks are invalid")

    paper = document.paper
    year = extraction.get("year") or (paper.publication_date.year if paper and paper.publication_date else None)
    authors = extraction.get("authors") or []
    if not authors and paper:
        authors = [author.name for author in paper.authors if getattr(author, "name", None)]

    enriched = []
    for chunk in chunks:
        if not isinstance(chunk, dict) or not chunk.get("text"):
            continue
        enriched.append(
            {
                **chunk,
                "document_id": document.id,
                "paper_id": paper.id if paper else document.paper_id,
                "year": year,
                "topics": extraction.get("topics", []),
                "datasets": extraction.get("datasets", []),
            }
        )

    graph_extraction = {
        **extraction,
        "title": extraction.get("title") or (paper.title if paper else f"Document {document.id}"),
        "doi": extraction.get("doi") or (paper.doi if paper else None),
        "year": year,
        "authors": authors,
    }
    return graph_extraction, enriched


def _index_vectors(chunks: list[dict[str, Any]]) -> int:
    if not chunks:
        return 0
    provider = get_embedding_provider()
    total = 0
    for start in range(0, len(chunks), EMBED_BATCH_SIZE):
        batch = chunks[start : start + EMBED_BATCH_SIZE]
        vectors = provider.embed([chunk["text"] for chunk in batch])
        total += upsert_chunks(batch, vectors)
    return total


def process_job(job_id: int) -> dict[str, Any]:
    db = SessionLocal()
    try:
        job = db.get(IndexingJob, job_id)
        if job is None:
            return {"job_id": job_id, "status": "missing"}
        document = db.get(Document, job.document_id)
        if document is None:
            raise ValueError("Document not found")

        extraction, chunks = _load_payload(document)
        errors: list[str] = []

        try:
            indexed_chunks = _index_vectors(chunks)
            job.vector_status = "completed"
        except Exception as exc:
            indexed_chunks = 0
            job.vector_status = "failed"
            errors.append(f"vector: {exc}")

        try:
            graph_result = index_extraction(document.id, extraction)
            job.graph_status = "completed"
        except Exception as exc:
            graph_result = {}
            job.graph_status = "failed"
            errors.append(f"graph: {exc}")

        if not errors:
            job.status = "completed"
            job.last_error = None
            job.completed_at = datetime.now(timezone.utc)
            document.status = "indexed"
        elif job.attempts < MAX_ATTEMPTS:
            job.status = "retry"
            job.last_error = " | ".join(errors)
        else:
            job.status = "failed"
            job.last_error = " | ".join(errors)
            document.status = "indexing_failed"

        payload = json.loads(document.metadata_json or "{}")
        payload["vector_index_status"] = job.vector_status
        payload["knowledge_graph_status"] = job.graph_status
        payload["indexing_job_id"] = job.id
        payload["indexing_error"] = job.last_error
        document.metadata_json = json.dumps(payload)
        db.commit()

        return {
            "job_id": job.id,
            "document_id": document.id,
            "status": job.status,
            "attempts": job.attempts,
            "vector_status": job.vector_status,
            "knowledge_graph_status": job.graph_status,
            "indexed_chunks": indexed_chunks,
            "graph": graph_result,
            "error": job.last_error,
        }
    except Exception as exc:
        job = db.get(IndexingJob, job_id)
        if job is not None:
            job.status = "retry" if job.attempts < MAX_ATTEMPTS else "failed"
            job.last_error = str(exc)
            job.completed_at = datetime.now(timezone.utc) if job.status == "failed" else None
            db.commit()
        return {"job_id": job_id, "status": "failed", "error": str(exc)}
    finally:
        db.close()


def run_once() -> dict[str, Any] | None:
    db = SessionLocal()
    try:
        job_id = claim_next_job(db)
    finally:
        db.close()
    if job_id is None:
        return None
    return process_job(job_id)
