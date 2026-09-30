from fastapi import APIRouter, Depends, HTTPException, Query
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.knowledge_graph.ingest import index_extraction
from app.services.knowledge_graph.query import graph_overview, paper_neighborhood, related_topics
from app.services.knowledge_graph.neo4j import run

router = APIRouter(prefix="/api/v1/knowledge-graph", tags=["knowledge-graph"])

@router.get("/overview")
def overview(current_user: User = Depends(get_current_user)):
    return graph_overview()

@router.get("/papers/{paper_id}/neighborhood")
def neighborhood(paper_id: int, limit: int = Query(50, ge=1, le=200), current_user: User = Depends(get_current_user)):
    return {"paper_id": paper_id, "items": paper_neighborhood(paper_id, limit)}

@router.get("/topics/{topic}/related")
def topics(topic: str, limit: int = Query(20, ge=1, le=100), current_user: User = Depends(get_current_user)):
    return {"topic": topic, "items": related_topics(topic, limit)}

@router.get("/health")
def graph_health(current_user: User = Depends(get_current_user)):
    try:
        run("RETURN 1 AS ok")
        return {"status": "ok", "service": "neo4j"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Neo4j unavailable: {exc}") from exc
