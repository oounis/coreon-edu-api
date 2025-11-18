import app.events
import app.background
import app.scheduler

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.router_loader import load_all_routers
from app.core import logging_config  # noqa: F401
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.tenant_middleware import TenantMiddleware
from app.middleware.error_handler import register_exception_handlers


app = FastAPI(title="Coreon EDU API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middlewares
app.add_middleware(RequestIDMiddleware)
app.add_middleware(TenantMiddleware)
app.add_middleware(LoggingMiddleware)

# Health
@app.get("/api/v1/health/", include_in_schema=False)
def health_slash():
    return {"status": "ok"}

# Load all routers automatically
load_all_routers(app)

# Exception handlers
register_exception_handlers(app)
