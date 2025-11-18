from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user
from app.services.activities.activities_service import ActivitiesService

router = APIRouter(prefix="/activities", tags=["Activities"])

@router.post("/event")
def create_event(data: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = ActivitiesService(db)
    return svc.create_club_event(
        club_id=data["club_id"],
        school_id=user.school_id,
        data=data
    )
