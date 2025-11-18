from __future__ import annotations
from typing import Dict, Any, List, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import (
    Event,
    EventRegistration,
    EventAttendance,
)
from app.services.workflow.workflow_service import WorkflowService
from app.services.notification_service import NotificationService


class EventsService:
    """
    Events & Activities:
    - Create/manage events
    - Register students
    - Permission workflow
    - Attendance tracking
    - Announcements + notifications
    """

    def __init__(self, db: Session):
        self.db = db
        self.workflow = WorkflowService(db)
        self.notifications = NotificationService(db)

    # -----------------------
    # Events
    # -----------------------
    def create_event(
        self,
        *,
        school_id: int,
        title: str,
        type: str,
        start_time: datetime,
        end_time: datetime,
        location: Optional[str],
        description: Optional[str],
        requires_permission: bool,
        meta: Optional[Dict[str, Any]],
        created_by: int,
    ):
        event = Event(
            school_id=school_id,
            title=title,
            type=type,  # "trip" | "competition" | "party" | "sport" | ...
            start_time=start_time,
            end_time=end_time,
            location=location,
            description=description,
            requires_permission=requires_permission,
            meta=meta or {},
            created_by=created_by,
        )

        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        return {"event": event}

    def list_events(self, *, school_id: int):
        items = (
            self.db.query(Event)
            .filter(Event.school_id == school_id)
            .order_by(Event.start_time.desc())
            .all()
        )
        return {"events": items}

    # -----------------------
    # Registrations
    # -----------------------
    def register_student(
        self,
        *,
        school_id: int,
        event_id: int,
        student_id: int,
        meta: Optional[Dict[str, Any]],
        created_by: int,
    ):
        event = (
            self.db.query(Event)
            .filter(Event.id == event_id)
            .filter(Event.school_id == school_id)
            .first()
        )
        if not event:
            raise ValueError("Event not found for this school")

        registration = EventRegistration(
            school_id=school_id,
            event_id=event_id,
            student_id=student_id,
            status="pending" if event.requires_permission else "approved",
            meta=meta or {},
            created_by=created_by,
        )

        self.db.add(registration)
        self.db.commit()
        self.db.refresh(registration)

        # Permission workflow
        if event.requires_permission:
            try:
                self.workflow.start(
                    school_id=school_id,
                    flow="event_permission",
                    type="parent_approval",
                    reference_id=registration.id,
                    created_by=created_by,
                    data={"student_id": student_id, "event_id": event_id},
                )
            except Exception:
                pass

        return {"registration": registration}

    def list_registrations(
        self,
        *,
        school_id: int,
        event_id: int,
    ):
        items = (
            self.db.query(EventRegistration)
            .filter(EventRegistration.school_id == school_id)
            .filter(EventRegistration.event_id == event_id)
            .all()
        )
        return {"registrations": items}

    # -----------------------
    # Attendance
    # -----------------------
    def record_attendance(
        self,
        *,
        school_id: int,
        event_id: int,
        student_id: int,
        status: str,
        scanned_at: Optional[datetime],
        meta: Optional[Dict[str, Any]],
        created_by: int,
    ):
        attendance = EventAttendance(
            school_id=school_id,
            event_id=event_id,
            student_id=student_id,
            status=status,  # present | absent | late
            scanned_at=scanned_at or datetime.utcnow(),
            meta=meta or {},
            created_by=created_by,
        )

        self.db.add(attendance)
        self.db.commit()
        self.db.refresh(attendance)

        return {"attendance": attendance}

    def event_summary(
        self,
        *,
        school_id: int,
        event_id: int,
    ):
        regs = (
            self.db.query(EventRegistration)
            .filter(EventRegistration.school_id == school_id)
            .filter(EventRegistration.event_id == event_id)
            .all()
        )

        attendance = (
            self.db.query(EventAttendance)
            .filter(EventAttendance.school_id == school_id)
            .filter(EventAttendance.event_id == event_id)
            .all()
        )

        return {
            "registrations_count": len(regs),
            "attendance_count": len(attendance),
            "registrations": regs,
            "attendance": attendance,
        }
