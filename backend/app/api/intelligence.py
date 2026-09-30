from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.hypothesis_intelligence import generate_opportunity_plan

router = APIRouter(prefix="/api/v1/intelligence", tags=["hypothesis-experiments"])

class PlanRequest(BaseModel):
    question: str = Field(min_length=5, max_length=2000)
    limit: int = Field(default=5, ge=1, le=10)

@router.post("/hypotheses")
async def hypotheses(payload: PlanRequest, current_user: User = Depends(get_current_user)):
    return await generate_opportunity_plan(payload.question, payload.limit)
