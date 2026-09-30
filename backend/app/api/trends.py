from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.trends.engine import analyze_all, analyze_topic

router = APIRouter(prefix="/api/v1/trends", tags=["trends"])

@router.get("")
def trends(limit: int = Query(30, ge=1, le=100), current_user: User = Depends(get_current_user)):
    return analyze_all(limit)

@router.get("/topic/{topic}")
def topic_trend(topic: str, current_user: User = Depends(get_current_user)):
    return analyze_topic(topic)
