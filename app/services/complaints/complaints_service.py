from __future__ import annotations
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.services.workflow.workflow_service import WorkflowService
from app.services.notification_service import NotificationService


class ComplaintsService:
    def __init__(self, db: Session):
        self.db = db
        self.workflow = WorkflowService(db)
        self.notifications = NotificationService(db)

    def submit_complaint(self, *, user, payload: Dict[str, Any]):
        data: Dict[str, Any] = dict(payload or {})
        data.setdefault("type", "complaint")
        data.setdefault("submitted_by", user.id)
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
                key="complaint_submitted",
                type="complaint",
                category="complaints",
                data={"request_id": getattr(request, "id", None)},
                priority="normal",
            )
        except Exception:
            # notifications must never break core flow
            pass

        return {"request": request}
