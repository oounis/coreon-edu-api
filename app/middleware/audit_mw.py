from time import perf_counter
from typing import Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.monitoring.metrics import metrics
from app.core.security import decode_token_or_none

class MetricsAuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # increment total hits
        metrics.inc("http_requests_total")

        # try to extract actor from Authorization header for downstream debug
        authorization: Optional[str] = request.headers.get("authorization")
        actor = "anonymous"
        if authorization and authorization.lower().startswith("bearer "):
            token = authorization.split(" ", 1)[1]
            claims = decode_token_or_none(token)
            if claims and "sub" in claims:
                actor = claims["sub"]

        request.state.actor = actor  # available to routes if needed

        # measure latency
        start = perf_counter()
        try:
            response = await call_next(request)
            return response
        finally:
            dur_ms = int((perf_counter() - start) * 1000)
            metrics.inc("http_requests_ms_total", dur_ms)
