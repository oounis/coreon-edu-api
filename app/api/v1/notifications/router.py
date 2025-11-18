from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user
from app.models import Notification, NotificationPreference
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/")
def list_notifications(db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
    )
    return q.all()

@router.post("/{notification_id}/mark-read")
def mark_read(notification_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    notif = (
        db.query(Notification)
        .filter(Notification.id == notification_id)
        .filter(Notification.user_id == user.id)
        .first()
    )
    if notif:
        notif.is_read = True
        db.commit()
    return {"status": "ok"}

@router.get("/preferences")
def get_preferences(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return (
        db.query(NotificationPreference)
        .filter(NotificationPreference.user_id == user.id)
        .all()
    )
