from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.gap_detection.engine import detect_gaps
from app.services.evidence.engine import score_opportunities
from app.services.gap_detection.research_critic import critique_research_gap
from app.services.gap_detection.opportunity_report import build_research_opportunity_report

router = APIRouter(prefix="/api/v1/gaps", tags=["research-gaps"])


class ResearchCriticRequest(BaseModel):
    title: str = Field(min_length=3, max_length=500)
    description: str = Field(default="", max_length=4000)
    limit: int = Field(default=8, ge=1, le=12)


@router.get("")
def gaps(limit: int = Query(20, ge=1, le=100), current_user: User = Depends(get_current_user)):
    return detect_gaps(limit=limit)


@router.get("/scored")
def scored_gaps(limit: int = Query(20, ge=1, le=100), current_user: User = Depends(get_current_user)):
    return score_opportunities(limit=limit)


@router.post("/critic")
async def research_critic(
    payload: ResearchCriticRequest,
    current_user: User = Depends(get_current_user),
):
    return await critique_research_gap(
        payload.title,
        payload.description,
        payload.limit,
    )


@router.post("/report")
async def research_opportunity_report(
    payload: ResearchCriticRequest,
    current_user: User = Depends(get_current_user),
):
    return await build_research_opportunity_report(
        payload.title,
        payload.description,
        payload.limit,
    )
