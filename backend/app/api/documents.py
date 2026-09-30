from pathlib import Path
import json
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models.document import Document
from app.models.paper import Paper
from app.models.user import User
from app.services.document_ingestion import DocumentIngestionError, checksum, process_pdf, store_pdf, validate_pdf

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
STORAGE_ROOT = Path("data/raw/papers")

@router.post("/upload", status_code=201)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    content = await file.read()
    try:
        validate_pdf(content, file.filename or "", file.content_type)
    except DocumentIngestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    digest = checksum(content)
    existing = db.query(Document).filter(Document.checksum == digest).first()
    if existing:
        return {"id": existing.id, "paper_id": existing.paper_id, "checksum": digest, "status": existing.status}
    path = store_pdf(content, STORAGE_ROOT, digest)
    try:
        parsed = process_pdf(path)
        paper = Paper(title=parsed["metadata"].get("title") or Path(file.filename or "paper.pdf").stem)
        db.add(paper)
        db.flush()
        document = Document(paper_id=paper.id, document_type="paper", storage_uri=str(path), checksum=digest, status="parsed", page_count=parsed["page_count"], extracted_text=parsed["text"], metadata_json=json.dumps({"metadata": parsed["metadata"], "sections": parsed["sections"], "references": parsed["references"], "tables": parsed["tables"], "figures": parsed["figures"], "chunks": parsed["chunks"]}))
        db.add(document)
        db.commit()
        db.refresh(document)
        return {"id": document.id, "paper_id": paper.id, "checksum": digest, "status": document.status, "page_count": document.page_count}
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=f"Document processing failed: {exc}") from exc

@router.get("/{document_id}")
def get_document(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"id": document.id, "paper_id": document.paper_id, "status": document.status, "page_count": document.page_count, "storage_uri": document.storage_uri}

@router.get("/{document_id}/parsed")
def get_parsed_document(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    payload = json.loads(document.metadata_json or "{}")
    return {"document_id": document.id, "page_count": document.page_count or 0, **payload}
