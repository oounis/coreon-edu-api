from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import AuditLog

def audit_handler(payload: dict):
    db: Session = SessionLocal()
    log = AuditLog(
        school_id=payload.get("school_id"),
        user_id=payload.get("user_id"),
        entity=payload.get("entity"),
        action=payload.get("action"),
        before=payload.get("before"),
        after=payload.get("after"),
        ip_address=payload.get("ip"),
    )
    db.add(log)
    db.commit()
    db.close()
