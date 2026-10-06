from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.services.document_ingestion import DocumentIngestionError, parse_pdf
from app.services.extraction import ScientificExtractor
from app.services.llm.factory import get_llm_provider
from app.services.paper_understanding import PaperUnderstandingPipeline
from app.services.embeddings.factory import get_embedding_provider
from app.services.vector_store import upsert_chunks
from app.services.knowledge_graph.ingest import index_extraction
import json

router=APIRouter(prefix="/api/v1/documents",tags=["scientific-extraction"])

@router.post("/{document_id}/extract")
async def extract_document(document_id:int, db:Session=Depends(get_db), current_user:User=Depends(get_current_user)):
    document=db.get(Document,document_id)
    if not document: raise HTTPException(status_code=404,detail="Document not found")
    if not document.storage_uri: raise HTTPException(status_code=422,detail="Document has no stored PDF")
    # Render's local filesystem is ephemeral. The upload pipeline persists the
    # parsed scientific content in PostgreSQL, so extraction must not depend on
    # the original local PDF still existing after a redeploy/restart.
    try:
        metadata = json.loads(document.metadata_json or "{}")
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=500, detail="Stored document metadata is invalid") from exc

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
        raise HTTPException(status_code=422, detail="No persisted extracted text is available for this document")
    try:
        result=await PaperUnderstandingPipeline(ScientificExtractor(get_llm_provider())).run(parsed)
    except Exception as exc:
        raise HTTPException(status_code=502,detail=f"Scientific extraction failed: {exc}") from exc
    payload = json.loads(document.metadata_json or "{}")
    payload["extraction"] = result
    vector_status = "not_indexed"
    try:
        chunks = [{**chunk, "document_id": document.id} for chunk in parsed.get("chunks", []) if chunk.get("text")]
        vectors = get_embedding_provider().embed([chunk["text"] for chunk in chunks])
        indexed = upsert_chunks(chunks, vectors)
        vector_status = f"indexed:{indexed}"
    except Exception:
        vector_status = "unavailable"
    payload["vector_index_status"] = vector_status
    graph_status = "not_indexed"
    try:
        graph_result = index_extraction(document.id, result)
        graph_status = graph_result
    except Exception:
        graph_status = "unavailable"
    payload["knowledge_graph_status"] = graph_status
    document.metadata_json = json.dumps(payload)
    document.status = "extracted"
    db.commit()
    result["vector_index_status"] = vector_status
    result["knowledge_graph_status"] = graph_status
    return result
