from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.audit import AuditLog

def log_event(
    db: Session,
    *,
    actor: str,
    action: str,
    obj_type: Optional[str] = None,
    obj_id: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
):
    entry = AuditLog(
        actor=actor,
        action=action,
        obj_type=obj_type,
        obj_id=str(obj_id) if obj_id is not None else None,
        meta=meta or None,
    )
    db.add(entry)
    db.commit()
    return entry
