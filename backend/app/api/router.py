from fastapi import APIRouter

router = APIRouter(prefix="/api")

@router.get("/v1/health", tags=["system"])
def api_health():
    return {"status": "ok", "service": "DiscoveryAI", "api_version": "v1"}
