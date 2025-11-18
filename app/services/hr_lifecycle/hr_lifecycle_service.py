from __future__ import annotations
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.services.workflow.workflow_service import WorkflowService
from app.services.notification_service import NotificationService


class HRLifecycleService:
    """
    High-level HR workflows orchestrated via the generic workflow engine.
    - Hiring
    - Termination / resignation
    - Internal transfer
    """

    def __init__(self, db: Session):
        self.db = db
        self.workflow = WorkflowService(db)
        self.notifications = NotificationService(db)

    def start_hiring(self, *, user, payload: Dict[str, Any]):
        data: Dict[str, Any] = dict(payload or {})
        data.setdefault("flow", "hiring")
        data.setdefault("action", "hire")
        data.setdefault("requested_by", user.id)
        data.setdefault("school_id", user.school_id)

        request = self.workflow.submit_request(
            user_id=user.id,
            school_id=user.school_id,
            data=data,
        )

        # Notify requester (and later managers via templates / preferences)
        try:
            self.notifications.create(
                user_id=user.id,
                school_id=user.school_id,
                key="hr_hiring_started",
                type="hr",
                category="hr_lifecycle",
                data={"request_id": getattr(request, "id", None)},
                priority="high",
            )
        except Exception:
            # don't break business flow on notification failure
            pass

        return {"request": request}

    def start_termination(self, *, user, payload: Dict[str, Any]):
        data: Dict[str, Any] = dict(payload or {})
        data.setdefault("flow", "termination")
        data.setdefault("action", "terminate")
        data.setdefault("requested_by", user.id)
        data.setdefault("school_id", user.school_id)

        request = self.workflow.submit_request(
            user_id=user.id,
            school_id=user.school_id,
            data=data,
        )

        try:
            self.notifications.create(
                user_id=user.id,
                school_id=user.school_id,
                key="hr_termination_started",
                type="hr",
                category="hr_lifecycle",
                data={"request_id": getattr(request, "id", None)},
                priority="critical",
            )
        except Exception:
            pass

        return {"request": request}

    def start_transfer(self, *, user, payload: Dict[str, Any]):
        data: Dict[str, Any] = dict(payload or {})
        data.setdefault("flow", "transfer")
        data.setdefault("action", "transfer")
        data.setdefault("requested_by", user.id)
        data.setdefault("school_id", user.school_id)

        request = self.workflow.submit_request(
            user_id=user.id,
            school_id=user.school_id,
            data=data,
        )

        try:
            self.notifications.create(
                user_id=user.id,
                school_id=user.school_id,
                key="hr_transfer_started",
                type="hr",
                category="hr_lifecycle",
                data={"request_id": getattr(request, "id", None)},
                priority="normal",
            )
        except Exception:
            pass

        return {"request": request}
