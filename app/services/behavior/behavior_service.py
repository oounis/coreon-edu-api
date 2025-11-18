from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import (
    BehaviorIncident,
    BehaviorPointLedger,
    Student,
)
from app.services.notification_service import NotificationService
from app.services.workflow.workflow_service import WorkflowService


class BehaviorService:
    """
    Behavior & Discipline Management:
    - Record behavior incidents (positive & negative)
    - Points system (merit/demerit)
    - Escalation workflow (if severity high)
    - Notifications to parents
    """

    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationService(db)
        self.workflow = WorkflowService(db)

    # -------------------------------
    # Incidents
    # -------------------------------
    def record_incident(
        self,
        *,
        school_id: int,
        student_id: int,
        title: str,
        description: str,
        type: str,  # positive | negative
        severity: str,  # low | medium | high | critical
        points: int,
        happened_at: Optional[datetime],
        meta: Optional[Dict[str, Any]],
        created_by: int,
        notify_parent: bool = True,
    ):
        incident = BehaviorIncident(
            school_id=school_id,
            student_id=student_id,
            title=title,
            description=description,
            type=type,
            severity=severity,
            points=points,
            happened_at=happened_at or datetime.utcnow(),
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)

        # ledger entry
        ledger = BehaviorPointLedger(
            school_id=school_id,
            student_id=student_id,
            incident_id=incident.id,
            points=points,
            created_by=created_by,
        )
        self.db.add(ledger)
        self.db.commit()

        # escalation workflow (optional)
        if severity in ("high", "critical"):
            try:
                self.workflow.start(
                    school_id=school_id,
                    flow="behavior_escalation",
                    type="discipline_review",
                    reference_id=incident.id,
                    created_by=created_by,
                    data={"severity": severity, "student_id": student_id},
                )
            except Exception:
                pass

        # notify parent
        if notify_parent:
            try:
                self.notifications.create(
                    user_id=student_id,  # later: link real parent_id
                    school_id=school_id,
                    key="behavior_incident",
                    type="behavior",
                    category="incident",
                    data={
                        "incident_id": incident.id,
                        "severity": severity,
                        "points": points,
                    },
                    priority="high" if severity != "low" else "normal",
                )
            except Exception:
                pass

        return {"incident": incident, "points": points}

    # -------------------------------
    # History per student
    # -------------------------------
    def student_history(
        self,
        *,
        school_id: int,
        student_id: int,
        limit: int = 50,
    ):
        incidents = (
            self.db.query(BehaviorIncident)
            .filter(BehaviorIncident.school_id == school_id)
            .filter(BehaviorIncident.student_id == student_id)
            .order_by(BehaviorIncident.happened_at.desc())
            .limit(limit)
            .all()
        )

        points = (
            self.db.query(BehaviorPointLedger)
            .filter(BehaviorPointLedger.school_id == school_id)
            .filter(BehaviorPointLedger.student_id == student_id)
            .order_by(BehaviorPointLedger.created_at.desc())
            .limit(limit)
            .all()
        )

        total_points = sum([x.points for x in points])

        return {
            "incidents": incidents,
            "ledger": points,
            "total_points": total_points,
        }

    # -------------------------------
    # Behavior summary per school
    # -------------------------------
    def school_summary(self, *, school_id: int):
        from sqlalchemy import func

        positive = (
            self.db.query(func.sum(BehaviorIncident.points))
            .filter(BehaviorIncident.school_id == school_id)
            .filter(BehaviorIncident.type == "positive")
            .scalar()
            or 0
        )

        negative = (
            self.db.query(func.sum(BehaviorIncident.points))
            .filter(BehaviorIncident.school_id == school_id)
            .filter(BehaviorIncident.type == "negative")
            .scalar()
            or 0
        )

        incidents = (
            self.db.query(BehaviorIncident)
            .filter(BehaviorIncident.school_id == school_id)
            .order_by(BehaviorIncident.happened_at.desc())
            .limit(100)
            .all()
        )

        return {
            "positive_points": positive,
            "negative_points": negative,
            "recent_incidents": incidents,
        }
