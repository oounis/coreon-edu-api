from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user
from app.services.security.security_service import SecurityService

router = APIRouter(prefix="/security", tags=["Security"])

@router.post("/incident")
def report_incident(body: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = SecurityService(db)
    return svc.report_incident(
        school_id=user.school_id,
        reporter_id=user.id,
        input_data=body
    )
