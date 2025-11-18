from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user
from app.services.nursery.nursery_service import NurseryService

router = APIRouter(prefix="/nursery", tags=["Nursery"])

@router.post("/daily-report")
def submit_daily_report(data: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = NurseryService(db)
    return svc.submit_daily_report(
        school_id=user.school_id,
        staff_id=user.id,
        student_id=data["student_id"],
        notes=data["notes"]
    )
