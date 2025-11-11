from fastapi import APIRouter
from pydantic import BaseModel
router = APIRouter()

class ExamSession(BaseModel):
    class_id: str
    subject_id: str
    teacher_id: str
    start_ts: str

@router.post("/start")
def start_exam(e: ExamSession):
    return {"ok": True, "exam": "started"}
