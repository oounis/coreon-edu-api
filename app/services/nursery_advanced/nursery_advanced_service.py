from __future__ import annotations
from typing import Dict, Any, List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import NurseryLog


class NurseryAdvancedService:
    """
    Nursery module:
    - Daily logs
    - Feeding reports
    - Sleep tracking
    """

    def __init__(self, db: Session):
        self.db = db

    def log(
        self,
        *,
        school_id: int,
        student_id: int,
        log_type: str,
        details: Dict[str, Any],
        created_by: int,
    ):
        l = NurseryLog(
            school_id=school_id,
            student_id=student_id,
            log_type=log_type,  # feeding | sleep | diaper | activity
            details=details or {},
            created_by=created_by,
        )
        self.db.add(l)
        self.db.commit()
        self.db.refresh(l)
        return {"log": l}

    def list(self, *, school_id: int, student_id: int):
        logs = self.db.query(NurseryLog).filter(
            NurseryLog.school_id == school_id,
            NurseryLog.student_id == student_id,
        ).order_by(NurseryLog.created_at.desc()).all()
        return {"logs": logs}
