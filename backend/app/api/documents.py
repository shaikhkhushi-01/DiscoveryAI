from pathlib import Path
from datetime import date
import json
import re

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models.document import Document
from app.models.paper import Paper
from app.models.user import User
from app.services.document_ingestion import DocumentIngestionError, checksum, process_pdf, store_pdf, validate_pdf
from app.services.extraction import ScientificExtractor, infer_paper_title
from app.services.llm.factory import get_llm_provider

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
STORAGE_ROOT = Path("data/raw/papers")


def build_scientific_extraction(
    text: str,
    pdf_metadata: dict,
    extracted_fields: dict,
    filename: str,
    sections: list[dict] | None = None,
) -> dict:
    """Combine LLM-extracted scientific fields with deterministic PDF metadata."""
    raw_title = str(pdf_metadata.get("title") or "").strip()
    title = infer_paper_title(text, raw_title, filename)

    raw_authors = str(pdf_metadata.get("author") or "").strip()
    authors = [author.strip() for author in re.split(r"\s*;\s*", raw_authors) if author.strip()]

    creation_date = str(pdf_metadata.get("creationDate") or "")
    year_match = re.search(r"(?:D:)?(19\d{2}|20\d{2})", creation_date)
    year = int(year_match.group(1)) if year_match else None

    doi_match = re.search(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", text, re.IGNORECASE)
    doi = doi_match.group(0).rstrip(".,;") if doi_match else None
    abstract_section = next(
        (section.get("text", "").strip() for section in (sections or []) if section.get("type") == "abstract"),
        "",
    )

    return {
        "title": title,
        "authors": authors,
        "year": year,
        "doi": doi,
        "abstract": abstract_section or None,
        **{key: value if isinstance(value, list) else [] for key, value in extracted_fields.items()},
    }


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
        # Parsing creates text/chunks, but indexing also requires a scientific
        # extraction object. Persist that extraction during upload.
        extracted_fields = await ScientificExtractor(get_llm_provider()).extract(parsed["text"])
        extraction = build_scientific_extraction(
            parsed["text"],
            parsed["metadata"],
            extracted_fields,
            file.filename or "paper.pdf",
            parsed["sections"],
        )
        paper = Paper(
            title=extraction["title"],
            doi=extraction["doi"],
            abstract=extraction["abstract"],
            publication_date=date(extraction["year"], 1, 1) if extraction["year"] else None,
        )
        db.add(paper)
        db.flush()
        metadata_payload = {
            "metadata": parsed["metadata"],
            "extraction": extraction,
            "sections": parsed["sections"],
            "references": parsed["references"],
            "tables": parsed["tables"],
            "figures": parsed["figures"],
            "chunks": parsed["chunks"],
        }
        document = Document(
            paper_id=paper.id,
            document_type="paper",
            storage_uri=str(path),
            checksum=digest,
            status="parsed",
            page_count=parsed["page_count"],
            extracted_text=parsed["text"],
            metadata_json=json.dumps(metadata_payload),
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return {"id": document.id, "paper_id": paper.id, "checksum": digest, "status": document.status, "page_count": document.page_count}
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=f"Document processing failed: {exc}") from exc


@router.post("/{document_id}/extract")
async def reprocess_scientific_extraction(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Repair extraction metadata for previously parsed documents."""
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if not document.extracted_text or not document.extracted_text.strip():
        raise HTTPException(status_code=422, detail="Document has no extracted PDF text")

    try:
        payload = json.loads(document.metadata_json or "{}")
        extracted_fields = await ScientificExtractor(get_llm_provider()).extract(document.extracted_text)
        extraction = build_scientific_extraction(
            document.extracted_text,
            payload.get("metadata") or {},
            extracted_fields,
            Path(document.storage_uri or "paper.pdf").name,
            payload.get("sections") or [],
        )
        payload["extraction"] = extraction
        document.metadata_json = json.dumps(payload)
        paper = db.get(Paper, document.paper_id)
        if paper:
            paper.title = extraction["title"]
            paper.doi = extraction["doi"]
            paper.abstract = extraction["abstract"]
            paper.publication_date = date(extraction["year"], 1, 1) if extraction["year"] else None
        db.commit()
        return {"document_id": document.id, "paper_id": document.paper_id, "status": "extraction_completed"}
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=f"Scientific extraction failed: {exc}") from exc


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
