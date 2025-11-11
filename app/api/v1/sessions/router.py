from fastapi import APIRouter
from pydantic import BaseModel
router = APIRouter()

class SessionPing(BaseModel):
    class_id: str
    subject_id: str
    teacher_id: str
    status: str  # "in_class" | "break" | "exam" | "interrupted"

@router.post("/status")
def session_status(ping: SessionPing):
    return {"ok": True, "status": ping.status}
