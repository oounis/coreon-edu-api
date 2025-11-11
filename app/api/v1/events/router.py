from fastapi import APIRouter
from pydantic import BaseModel
router = APIRouter()

class Trip(BaseModel):
    title: str
    date: str
    classes: list[str]

@router.post("/trip")
def create_trip(t: Trip):
    return {"ok": True, "trip": t.title}
