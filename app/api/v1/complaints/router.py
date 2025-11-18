from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.services.complaints.complaints_service import ComplaintsService

router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.post("/")
def submit_complaint(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    svc = ComplaintsService(db)
    return svc.submit_complaint(user=user, payload=payload)
