from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime

from sqlalchemy.orm import Session

from app.services.notification_service import NotificationService
from app.services.workflow.workflow_service import WorkflowService
from app.models import (
    CommunicationMessage,
    CommunicationAnnouncement,
)


class CommunicationService:
    """
    Central communication system:
    - Internal messaging (staff to staff)
    - Announcements (to students, parents, staff groups)
    - Multi-channel notifications (in-app, email, sms)
    """

    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationService(db)
        self.workflow = WorkflowService(db)

    # -------------------------
    # Internal Messages
    # -------------------------
    def send_message(
        self,
        *,
        school_id: int,
        sender_id: int,
        recipients: List[int],
        subject: str,
        content: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        items = []
        for rid in recipients:
            msg = CommunicationMessage(
                school_id=school_id,
                sender_id=sender_id,
                recipient_id=rid,
                subject=subject,
                content=content,
                meta=meta or {},
                sent_at=datetime.utcnow(),
            )
            self.db.add(msg)
            items.append(msg)

            # in-app notification
            try:
                self.notifications.create(
                    user_id=rid,
                    school_id=school_id,
                    key="internal_message",
                    type="communication",
                    category="message",
                    data={"subject": subject, "sender": sender_id},
                    priority="normal",
                )
            except Exception:
                pass

        self.db.commit()
        return {"messages": items}

    # -------------------------
    # Announcements (broadcast)
    # -------------------------
    def create_announcement(
        self,
        *,
        school_id: int,
        title: str,
        body: str,
        audience: str,
        attachments: Optional[List[Dict[str, Any]]] = None,
        meta: Optional[Dict[str, Any]] = None,
        created_by: int,
    ) -> Dict[str, Any]:

        ann = CommunicationAnnouncement(
            school_id=school_id,
            title=title,
            body=body,
            audience=audience,   # "all_parents" | "all_students" | "teachers" | "staff" ...
            attachments=attachments or [],
            meta=meta or {},
            created_by=created_by,
        )

        self.db.add(ann)
        self.db.commit()
        self.db.refresh(ann)

        # optional: push notifications
        try:
            self.notifications.broadcast(
                school_id=school_id,
                key="announcement",
                type="communication",
                category="announcement",
                data={"title": title},
                audience=audience,
            )
        except Exception:
            pass

        return {"announcement": ann}

    # -------------------------
    # List announcements
    # -------------------------
    def list_announcements(self, *, school_id: int) -> Dict[str, Any]:
        q = (
            self.db.query(CommunicationAnnouncement)
            .filter(CommunicationAnnouncement.school_id == school_id)
            .order_by(CommunicationAnnouncement.created_at.desc())
        )
        return {"announcements": q.all()}

