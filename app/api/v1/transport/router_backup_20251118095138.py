from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user
from app.services.transport.transport_service import TransportService

router = APIRouter(prefix="/transport", tags=["Transport"])

@router.post("/attendance")
def mark_attendance(data: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = TransportService(db)
    return svc.mark_bus_attendance(
        subscription_id=data["subscription_id"],
        school_id=user.school_id,
    )
