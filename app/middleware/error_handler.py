import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger("coreon.api")

def _get_request_id(request: Request):
    return getattr(getattr(request, "state", None), "request_id", None)

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        payload = {
            "detail": exc.detail,
            "status_code": exc.status_code,
            "request_id": _get_request_id(request),
        }
        logger.warning(f"HTTPException: {payload}")
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        payload = {
            "detail": "Validation error",
            "errors": exc.errors(),
            "request_id": _get_request_id(request),
        }
        logger.warning(f"Validation error: {payload}")
        return JSONResponse(status_code=422, content=payload)

    @app.exception_handler(IntegrityError)
    async def integrity_exception_handler(request: Request, exc: IntegrityError):
        payload = {
            "detail": "Database integrity error",
            "request_id": _get_request_id(request),
        }
        logger.error("Integrity error", exc_info=True)
        return JSONResponse(status_code=400, content=payload)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        payload = {
            "detail": "Internal server error",
            "request_id": _get_request_id(request),
        }
        logger.error("Unhandled exception", exc_info=True)
        return JSONResponse(status_code=500, content=payload)
