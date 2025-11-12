from fastapi import FastAPI, Request
from time import perf_counter

from app.monitoring.metrics import metrics

# Routers
from app.api.v1.attendance.router import router as attendance_router
from app.api.v1.sessions.router import router as sessions_router
from app.api.v1.behavior.router import router as behavior_router
from app.api.v1.requests.router import router as requests_router
from app.api.v1.exams.router import router as exams_router
from app.api.v1.events.router import router as events_router
from app.api.v1.homework.router import router as homework_router
from app.api.v1.finance.router import router as finance_router
from app.api.v1.auth.router import router as auth_router
from app.api.v1.org.router import router as org_router
from app.api.v1.people.router import router as people_router
from app.api.v1.academic.router import router as academic_router
from app.api.v1.timetable.router import router as timetable_router
from app.api.v1.metrics.router import router as metrics_router

app = FastAPI(title="KOGIA Coreon Education API", version="0.1.0")

# --- simple metrics middleware ---
@app.middleware("http")
async def _metrics_mw(request: Request, call_next):
    metrics.inc("http_requests_total")
    start = perf_counter()
    try:
        resp = await call_next(request)
        return resp
    finally:
        dur_ms = int((perf_counter() - start) * 1000)
        metrics.inc("http_requests_ms_total", dur_ms)

# --- health ---
@app.get("/health", tags=["health"])
def health():
    metrics.inc("health_hits")
    return {"status": "ok"}

# --- Routers ---
app.include_router(attendance_router, prefix="/api/v1/attendance", tags=["attendance"])
app.include_router(sessions_router,   prefix="/api/v1/sessions",   tags=["sessions"])
app.include_router(behavior_router,   prefix="/api/v1/behavior",   tags=["behavior"])
app.include_router(requests_router,   prefix="/api/v1/requests",   tags=["requests"])
app.include_router(exams_router,      prefix="/api/v1/exams",      tags=["exams"])
app.include_router(events_router,     prefix="/api/v1/events",     tags=["events"])
app.include_router(homework_router,   prefix="/api/v1/homework",   tags=["homework"])
app.include_router(finance_router,    prefix="/api/v1/finance",    tags=["finance"])
app.include_router(auth_router,       prefix="/api/v1/auth",       tags=["auth"])
app.include_router(org_router,        prefix="/api/v1/org",        tags=["org"])
app.include_router(people_router,     prefix="/api/v1/people",     tags=["people"])
app.include_router(academic_router,   prefix="/api/v1/academic",   tags=["academic"])
app.include_router(timetable_router,  prefix="/api/v1/timetable",  tags=["timetable"])

# metrics (root level, like /metrics)
app.include_router(metrics_router, tags=["metrics"])
