"""
Audit Logging Middleware
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.logger import logger
import time


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = (time.time() - start) * 1000
        if request.url.path.startswith("/api"):
            logger.info(
                f"{request.method} {request.url.path} -> {response.status_code} ({duration:.1f}ms)"
            )
        return response
