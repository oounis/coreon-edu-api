from fastapi import APIRouter
from pydantic import BaseModel
router = APIRouter()

class Request(BaseModel):
    req_type: str
    actor_id: str
    payload: dict

@router.post("/")
def create_request(r: Request):
    return {"ok": True, "status": "pending", "type": r.req_type}
