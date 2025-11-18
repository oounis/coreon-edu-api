from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.notification_service import NotificationService

def notification_handler(payload: dict):
    db: Session = SessionLocal()
    svc = NotificationService(db)

    svc.create(
        user_id=payload["user_id"],
        school_id=payload.get("school_id"),
        key=payload["event"],
        type=payload["event"],
        category=payload.get("category", "system"),
        data=payload.get("data"),
        request_id=payload.get("request_id"),
        priority=payload.get("priority", "normal"),
    )
    db.close()
