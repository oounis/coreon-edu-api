from __future__ import annotations
from typing import Dict, Any, List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import (
    CounselingCase,
    CounselingSession,
    CounselingNote,
)
from app.services.notification_service import NotificationService


class CounselingService:
    """
    Counseling & student wellbeing:
    - Case creation
    - Counseling sessions
    - Counselor notes
    - Escalations
    """

    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationService(db)

    def open_case(
        self,
        *,
        school_id: int,
        student_id: int,
        case_type: str,
        description: str,
        priority: str,
        meta: Dict[str, Any],
        created_by: int,
    ):
        case = CounselingCase(
            school_id=school_id,
            student_id=student_id,
            case_type=case_type,
            description=description,
            priority=priority,
            meta=meta or {},
            created_by=created_by,
            status="open",
        )
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
        return {"case": case}

    def add_session(
        self,
        *,
        school_id: int,
        case_id: int,
        counselor_id: int,
        notes: str,
        meta: Dict[str, Any],
        created_by: int,
    ):
        session = CounselingSession(
            school_id=school_id,
            case_id=case_id,
            counselor_id=counselor_id,
            notes=notes,
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return {"session": session}

    def add_note(
        self,
        *,
        school_id: int,
        case_id: int,
        note: str,
        created_by: int,
    ):
        n = CounselingNote(
            school_id=school_id,
            case_id=case_id,
            note=note,
            created_by=created_by,
        )
        self.db.add(n)
        self.db.commit()
        self.db.refresh(n)
        return {"note": n}

    def list_cases(self, *, school_id: int, student_id: Optional[int] = None):
        q = self.db.query(CounselingCase).filter(CounselingCase.school_id == school_id)
        if student_id:
            q = q.filter(CounselingCase.student_id == student_id)
        return {"cases": q.all()}
