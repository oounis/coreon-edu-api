from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
router = APIRouter()

class HomeroomMark(BaseModel):
    class_id: str
    date: str
    present_ids: List[str] = []
    absent_ids: List[str] = []
    late_ids: List[str] = []

@router.post("/homeroom")
def homeroom_roll(mark: HomeroomMark):
    return {"ok": True, "processed": len(mark.present_ids)+len(mark.absent_ids)+len(mark.late_ids)}
