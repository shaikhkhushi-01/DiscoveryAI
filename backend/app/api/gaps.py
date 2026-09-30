from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.gap_detection.engine import detect_gaps

router = APIRouter(prefix="/api/v1/gaps", tags=["research-gaps"])

@router.get("")
def gaps(limit: int = Query(20, ge=1, le=100), current_user: User = Depends(get_current_user)):
    return detect_gaps(limit=limit)
