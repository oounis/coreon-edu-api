from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user
from app.services.hr.hr_service import HRService

router = APIRouter(prefix="/hr", tags=["HR"])

@router.post("/leave-request")
def create_leave_request(body: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = HRService(db)
    return svc.create_leave_request(
        school_id=user.school_id,
        staff_id=user.id,
        data=body
    )
