from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import AuditLog


class AuditIntelService:
    """
    Audit intelligence:
    - Filtered logs
    - Actor-based search
    - Time-range analytics
    """

    def __init__(self, db: Session):
        self.db = db

    def search(self, *, school_id: int, actor_id: Optional[int], action: Optional[str], since: Optional[str], until: Optional[str]):
        q = self.db.query(AuditLog).filter(AuditLog.school_id == school_id)

        if actor_id:
            q = q.filter(AuditLog.actor_id == actor_id)
        if action:
            q = q.filter(AuditLog.action == action)
        if since:
            q = q.filter(AuditLog.created_at >= datetime.fromisoformat(since))
        if until:
            q = q.filter(AuditLog.created_at <= datetime.fromisoformat(until))

        q = q.order_by(AuditLog.created_at.desc())
        return {"logs": q.all()}
