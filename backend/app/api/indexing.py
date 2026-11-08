from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models.document import Document
from app.models.indexing_job import IndexingJob
from app.models.user import User
from datetime import datetime, timezone

from app.services.indexing import enqueue_indexing, recover_stale_job
from app.services.vector_store import check_qdrant_connection

router = APIRouter(prefix="/api/v1/documents", tags=["indexing"])
qdrant_router = APIRouter(prefix="/api/v1/diagnostics", tags=["diagnostics"])


@qdrant_router.get("/qdrant-health")
def qdrant_health(current_user: User = Depends(get_current_user)):
    """Read-only Qdrant connectivity check; never returns credentials."""
    try:
        return check_qdrant_connection()
    except Exception as exc:
        # Return only exception type/message; Qdrant credentials are never included.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unreachable", "error_type": type(exc).__name__, "message": str(exc)[:500]},
        ) from exc


def _job_response(job: IndexingJob) -> dict:
    return {
        "job_id": job.id,
        "document_id": job.document_id,
        "status": job.status,
        "attempts": job.attempts,
        "vector_index_status": job.vector_status,
        "knowledge_graph_status": job.graph_status,
        "last_error": job.last_error,
        "queued_at": job.queued_at,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
    }


@router.post("/{document_id}/index", status_code=status.HTTP_202_ACCEPTED)
def queue_indexing(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    job = enqueue_indexing(db, document_id)
    db.commit()

    # The dedicated worker polls PostgreSQL and claims queued jobs.
    # Never run ML indexing inside the web request process.
    return _job_response(job)


@router.get("/{document_id}/index-status")
def indexing_status(
    document_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not db.get(Document, document_id):
        raise HTTPException(status_code=404, detail="Document not found")
    job = recover_stale_job(db, document_id)
    if not job:
        raise HTTPException(status_code=404, detail="No indexing job exists for this document")

    # Status reads are side-effect free. The worker owns stale recovery/retries.
    return _job_response(job)
