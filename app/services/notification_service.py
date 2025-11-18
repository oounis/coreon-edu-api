from __future__ import annotations
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session
from app.models import (
    Notification,
    NotificationPreference,
    NotificationTemplate,
)
from app.background.task_queue import task_queue


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def _render_template(self, template: NotificationTemplate, data: dict):
        title = template.title_template
        body = template.body_template or ""
        for key, value in (data or {}).items():
            placeholder = "{{" + key + "}}"
            title = title.replace(placeholder, str(value))
            body = body.replace(placeholder, str(value))
        return title, body

    def _get_template(self, key: str, school_id: Optional[int]):
        # 1) school-specific template
        tmpl = (
            self.db.query(NotificationTemplate)
            .filter(NotificationTemplate.key == key)
            .filter(NotificationTemplate.school_id == school_id)
            .first()
        )
        if tmpl:
            return tmpl

        # 2) global fallback
        return (
            self.db.query(NotificationTemplate)
            .filter(NotificationTemplate.key == key)
            .filter(NotificationTemplate.school_id.is_(None))
            .first()
        )

    def _check_preferences(self, user_id: int, priority: str) -> Dict[str, bool]:
        prefs = (
            self.db.query(NotificationPreference)
            .filter(NotificationPreference.user_id == user_id)
            .all()
        )

        allowed: Dict[str, bool] = {"in_app": True}
        levels = ["low", "normal", "high", "critical"]

        for p in prefs:
            if p.min_priority:
                if levels.index(priority) < levels.index(p.min_priority):
                    allowed[p.channel] = False
                    continue
            allowed[p.channel] = p.enabled

        return allowed

    def create(
        self,
        *,
        user_id: int,
        school_id: Optional[int],
        key: str,
        type: str,
        category: str,
        data: Optional[Dict[str, Any]] = None,
        request_id: Optional[int] = None,
        priority: str = "normal",
    ):
        # template
        template = self._get_template(key, school_id)
        if template:
            title, body = self._render_template(template, data or {})
        else:
            title = key
            body = None

        # channel prefs
        channels = self._check_preferences(user_id, priority)

        # in-app notification
        notification = Notification(
            user_id=user_id,
            school_id=school_id,
            type=type,
            category=category,
            title=title,
            body=body,
            data=data,
            request_id=request_id,
            priority=priority,
        )

        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)

        # async channels via background queue
        if channels.get("email"):
            task_queue.enqueue("send_email", {
                "user_id": user_id,
                "school_id": school_id,
                "notification_id": notification.id,
                "title": title,
                "body": body,
                "priority": priority,
            })

        if channels.get("sms"):
            task_queue.enqueue("send_sms", {
                "user_id": user_id,
                "school_id": school_id,
                "notification_id": notification.id,
                "body": body,
                "priority": priority,
            })

        if channels.get("push"):
            task_queue.enqueue("send_push", {
                "user_id": user_id,
                "school_id": school_id,
                "notification_id": notification.id,
                "title": title,
                "body": body,
                "priority": priority,
            })

        return notification
