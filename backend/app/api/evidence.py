from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.evidence.engine import score_opportunities
from app.services.evidence.validator import validate_evidence
from app.services.gap_detection.candidates import generate_graph_candidates

router = APIRouter(prefix="/api/v1/evidence", tags=["evidence"])

@router.get("/opportunities")
def opportunities(limit: int = Query(20, ge=1, le=100), current_user: User = Depends(get_current_user)):
    return score_opportunities(limit)

@router.get("/gap/{gap_index}")
def gap_evidence(gap_index: int, current_user: User = Depends(get_current_user)):
    candidates = generate_graph_candidates(max(gap_index + 1, 1))
    if gap_index < 0 or gap_index >= len(candidates):
        return {"error": "gap index out of range"}
    return validate_evidence(candidates[gap_index])
