from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.rag import answer_question

router = APIRouter(prefix="/api/v1/rag", tags=["rag"])

class RAGRequest(BaseModel):
    query: str = Field(min_length=2, max_length=2000)
    limit: int = Field(default=8, ge=1, le=20)
    year: int | None = Field(default=None, ge=1900, le=2100)
    topic: str | None = None
    dataset: str | None = None

@router.post("/ask")
async def ask(payload: RAGRequest, current_user: User = Depends(get_current_user)):
    filters = {"year": payload.year, "topic": payload.topic, "dataset": payload.dataset}
    return await answer_question(payload.query, limit=payload.limit, filters=filters)
