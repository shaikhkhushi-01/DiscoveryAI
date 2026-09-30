import time
from fastapi import Request
from app.core.logging import get_logger

logger = get_logger(__name__)

async def request_logging_middleware(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - started) * 1000
    logger.info("request method=%s path=%s status=%s duration_ms=%.2f", request.method, request.url.path, response.status_code, duration_ms)
    return response
