from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.hypothesis_intelligence import generate_opportunity_plan
from app.services.research_synthesis import synthesize_research

router = APIRouter(prefix="/api/v1/intelligence", tags=["research-intelligence"])


class PlanRequest(BaseModel):
    question: str = Field(min_length=5, max_length=2000)
    limit: int = Field(default=5, ge=1, le=10)


class SynthesisRequest(BaseModel):
    query: str = Field(min_length=5, max_length=2000)
    mode: Literal["comparison", "literature_review"] = "literature_review"
    limit: int = Field(default=12, ge=2, le=30)
    paper_ids: list[int] | None = Field(default=None, max_length=20)


@router.post("/hypotheses")
async def hypotheses(payload: PlanRequest, current_user: User = Depends(get_current_user)):
    return await generate_opportunity_plan(payload.question, payload.limit)


@router.post("/compare")
async def compare_papers(payload: SynthesisRequest, current_user: User = Depends(get_current_user)):
    return await synthesize_research(
        payload.query, mode="comparison", limit=payload.limit, paper_ids=payload.paper_ids
    )


@router.post("/literature-review")
async def literature_review(payload: SynthesisRequest, current_user: User = Depends(get_current_user)):
    return await synthesize_research(
        payload.query, mode="literature_review", limit=payload.limit, paper_ids=payload.paper_ids
    )
