from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import BehaviorIncident, BehaviorActionPlan
from app.services.notification_service import NotificationService


class BehaviorAdvancedService:
    """
    Advanced discipline:
    - Incident grading
    - Action plans (corrective)
    - Parent & admin escalation
    """

    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationService(db)

    def report(
        self,
        *,
        school_id: int,
        student_id: int,
        severity: str,
        description: str,
        created_by: int,
        meta: Dict[str, Any],
        location: Optional[str],
    ):
        inc = BehaviorIncident(
            school_id=school_id,
            student_id=student_id,
            severity=severity,
            description=description,
            meta=meta or {},
            location=location,
            created_by=created_by,
        )
        self.db.add(inc)
        self.db.commit()
        self.db.refresh(inc)

        if severity in ("high", "critical"):
            try:
                self.notifications.create(
                    user_id=created_by,
                    school_id=school_id,
                    key="behavior_critical",
                    type="behavior",
                    category="incident",
                    priority="high",
                    data={"student_id": student_id, "severity": severity},
                )
            except Exception:
                pass

        return {"incident": inc}

    def create_plan(
        self,
        *,
        school_id: int,
        incident_id: int,
        steps: List[str],
        duration_days: int,
        created_by: int,
    ):
        plan = BehaviorActionPlan(
            school_id=school_id,
            incident_id=incident_id,
            steps=steps,
            duration_days=duration_days,
            created_by=created_by,
        )
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return {"plan": plan}
