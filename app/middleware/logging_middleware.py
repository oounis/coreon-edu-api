import time
import json
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.monitoring.metrics import metrics

logger = logging.getLogger("coreon.api")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response: Response | None = None
        try:
            response = await call_next(request)
            return response
        finally:
            duration_ms = (time.time() - start) * 1000.0
            status_code = getattr(response, "status_code", None)
            method = request.method
            path = request.url.path
            request_id = getattr(getattr(request, "state", None), "request_id", None)

            record = {
                "type": "http_request",
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": int(duration_ms),
                "request_id": request_id,
                "client_host": request.client.host if request.client else None,
            }
            # Log JSON for ingestion by log stack (ELK, Loki, etc.)
            try:
                logger.info(json.dumps(record))
            except Exception:
                logger.info(str(record))

            # Metrics: HTTP counters + latency histogram-ish
            try:
                labels = {
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                }
                metrics.inc("http_requests_total", labels=labels)
                metrics.observe("http_request_duration_ms", duration_ms, labels={
                    "method": method,
                    "path": path,
                })
            except Exception:
                # metrics must never break the request
                logger.debug("Metrics update failed", exc_info=True)
