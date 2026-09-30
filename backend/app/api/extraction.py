from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.services.document_ingestion import parse_pdf
from app.services.extraction import ScientificExtractor
from app.services.llm.factory import get_llm_provider
from app.services.paper_understanding import PaperUnderstandingPipeline
import json

router=APIRouter(prefix="/api/v1/documents",tags=["scientific-extraction"])

@router.post("/{document_id}/extract")
async def extract_document(document_id:int, db:Session=Depends(get_db), current_user:User=Depends(get_current_user)):
    document=db.get(Document,document_id)
    if not document: raise HTTPException(status_code=404,detail="Document not found")
    if not document.storage_uri: raise HTTPException(status_code=422,detail="Document has no stored PDF")
    parsed=parse_pdf(__import__("pathlib").Path(document.storage_uri))
    parsed["document_id"]=document.id
    try:
        result=await PaperUnderstandingPipeline(ScientificExtractor(get_llm_provider())).run(parsed)
    except Exception as exc:
        raise HTTPException(status_code=502,detail=f"Scientific extraction failed: {exc}") from exc
    payload = json.loads(document.metadata_json or "{}")
    payload["extraction"] = result
    document.metadata_json = json.dumps(payload)
    document.status = "extracted"
    db.commit()
    return result
