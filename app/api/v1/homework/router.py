from fastapi import APIRouter
from pydantic import BaseModel
router = APIRouter()

class Homework(BaseModel):
    class_id: str
    subject_id: str
    title: str
    due_date: str

@router.post("/")
def assign(hw: Homework):
    return {"ok": True, "assigned": hw.title}
