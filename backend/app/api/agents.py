from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.agents.coordinator import run_discovery_workflow

router = APIRouter(prefix="/api/v1/agents", tags=["multi-agent"])

class DiscoveryRequest(BaseModel):
    question: str = Field(min_length=5, max_length=2000)

@router.post("/discover")
def discover(payload: DiscoveryRequest, current_user: User = Depends(get_current_user)):
    return run_discovery_workflow(payload.question)
