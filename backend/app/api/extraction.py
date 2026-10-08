from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.services.extraction import ScientificExtractor
from app.services.llm.factory import get_llm_provider
from app.services.paper_understanding import PaperUnderstandingPipeline
import json

router = APIRouter(prefix="/api/v1/documents", tags=["scientific-extraction"])


@router.post("/{document_id}/extract")
async def extract_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if not document.storage_uri:
        raise HTTPException(status_code=422, detail="Document has no stored PDF")

    # Render's local filesystem is ephemeral. The upload pipeline persists the
    # parsed scientific content in PostgreSQL, so extraction must not depend on
    # the original local PDF still existing after a redeploy/restart.
    try:
        metadata = json.loads(document.metadata_json or "{}")
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail="Stored document metadata is invalid",
        ) from exc

    parsed = {
        "document_id": document.id,
        "text": document.extracted_text or "",
        "page_count": document.page_count or 0,
        "metadata": metadata.get("metadata", {}),
        "sections": metadata.get("sections", []),
        "references": metadata.get("references", []),
        "tables": metadata.get("tables", []),
        "figures": metadata.get("figures", []),
        "chunks": metadata.get("chunks", []),
    }

    if not parsed["text"]:
        raise HTTPException(
            status_code=422,
            detail="No persisted extracted text is available for this document",
        )

    # Keep the HTTP extraction path lightweight and reliable on small Render
    # instances. Scientific extraction is the critical operation here.
    # SentenceTransformer/PyTorch and external vector/graph indexing are
    # intentionally not executed synchronously in this request because they
    # can consume hundreds of MB of RAM and previously caused the web process
    # to restart before returning the extraction response.
    try:
        result = await PaperUnderstandingPipeline(
            ScientificExtractor(get_llm_provider())
        ).run(parsed)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Scientific extraction failed: {exc}",
        ) from exc

    payload = json.loads(document.metadata_json or "{}")
    payload["extraction"] = result
    payload["vector_index_status"] = "deferred"
    payload["knowledge_graph_status"] = "deferred"

    document.metadata_json = json.dumps(payload)
    document.status = "extracted"
    db.commit()

    result["vector_index_status"] = "deferred"
    result["knowledge_graph_status"] = "deferred"
    return result
