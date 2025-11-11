from fastapi import FastAPI
from app.api.v1.attendance.router import router as attendance_router
from app.api.v1.sessions.router import router as sessions_router
from app.api.v1.behavior.router import router as behavior_router
from app.api.v1.requests.router import router as requests_router
from app.api.v1.exams.router import router as exams_router
from app.api.v1.events.router import router as events_router
from app.api.v1.homework.router import router as homework_router
from app.api.v1.finance.router import router as finance_router

app = FastAPI(title="KOGIA Coreon Education API", version="0.1.0")

app.include_router(attendance_router, prefix="/api/v1/attendance", tags=["attendance"])
app.include_router(sessions_router, prefix="/api/v1/sessions", tags=["sessions"])
app.include_router(behavior_router, prefix="/api/v1/behavior", tags=["behavior"])
app.include_router(requests_router, prefix="/api/v1/requests", tags=["requests"])
app.include_router(exams_router, prefix="/api/v1/exams", tags=["exams"])
app.include_router(events_router, prefix="/api/v1/events", tags=["events"])
app.include_router(homework_router, prefix="/api/v1/homework", tags=["homework"])
app.include_router(finance_router, prefix="/api/v1/finance", tags=["finance"])

@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
