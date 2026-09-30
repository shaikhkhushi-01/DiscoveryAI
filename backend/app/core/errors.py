from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger

logger = get_logger(__name__)

class DiscoveryAIError(Exception):
    def __init__(self, message: str, code: str = "application_error"):
        self.message = message
        self.code = code
        super().__init__(message)

async def discoveryai_exception_handler(request: Request, exc: DiscoveryAIError) -> JSONResponse:
    logger.warning("application_error path=%s code=%s", request.url.path, exc.code)
    return JSONResponse(status_code=400, content={"error": {"code": exc.code, "message": exc.message}})

async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": "http_error", "message": str(exc.detail)}})

async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_error path=%s", request.url.path)
    return JSONResponse(status_code=500, content={"error": {"code": "internal_server_error", "message": "Internal server error"}})
