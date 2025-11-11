from fastapi import APIRouter
from pydantic import BaseModel
router = APIRouter()

class BehaviorEvent(BaseModel):
    student_id: str
    category: str
    delta: int
    context: str
    ts: str

@router.post("/event")
def post_event(ev: BehaviorEvent):
    return {"ok": True, "applied": ev.delta}
