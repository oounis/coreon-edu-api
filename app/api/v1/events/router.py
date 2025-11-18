from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role
from app.services.events.events_service import EventsService

router = APIRouter(prefix="/events", tags=["Events"])


# ---------------------------
# Create Event
# ---------------------------
@router.post("/")
def create_event(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.SCHOOL_ADMIN, Role.SUPER_ADMIN, Role.PRINCIPAL
    )),
):
    svc = EventsService(db)

    start = datetime.fromisoformat(payload["start_time"])
    end = datetime.fromisoformat(payload["end_time"])

    return svc.create_event(
        school_id=user.school_id,
        title=payload["title"],
        type=payload["type"],
        start_time=start,
        end_time=end,
        location=payload.get("location"),
        description=payload.get("description"),
        requires_permission=bool(payload.get("requires_permission", False)),
        meta=payload.get("meta") or {},
        created_by=user.id,
    )


@router.get("/")
def list_events(
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TEACHER, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN,
        Role.PARENT, Role.STUDENT, Role.PRINCIPAL
    )),
):
    svc = EventsService(db)
    return svc.list_events(school_id=user.school_id)


# ---------------------------
# Registrations
# ---------------------------
@router.post("/{event_id}/register")
def register_student(
    event_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TEACHER, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN
    )),
):
    svc = EventsService(db)
    return svc.register_student(
        school_id=user.school_id,
        event_id=event_id,
        student_id=payload["student_id"],
        meta=payload.get("meta") or {},
        created_by=user.id,
    )


@router.get("/{event_id}/registrations")
def list_registrations(
    event_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TEACHER, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN,
        Role.PRINCIPAL
    )),
):
    svc = EventsService(db)
    return svc.list_registrations(
        school_id=user.school_id,
        event_id=event_id,
    )


# ---------------------------
# Attendance
# ---------------------------
@router.post("/{event_id}/attendance")
def record_attendance(
    event_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TEACHER, Role.SUPER_ADMIN, Role.SCHOOL_ADMIN
    )),
):
    svc = EventsService(db)

    scanned_at_raw = payload.get("scanned_at")
    scanned_at = (
        datetime.fromisoformat(scanned_at_raw)
        if scanned_at_raw else None
    )

    return svc.record_attendance(
        school_id=user.school_id,
        event_id=event_id,
        student_id=payload["student_id"],
        status=payload.get("status", "present"),
        scanned_at=scanned_at,
        meta=payload.get("meta") or {},
        created_by=user.id,
    )


@router.get("/{event_id}/summary")
def event_summary(
    event_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TEACHER, Role.SUPER_ADMIN, Role.SCHOOL_ADMIN, Role.PRINCIPAL
    )),
):
    svc = EventsService(db)
    return svc.event_summary(
        school_id=user.school_id,
        event_id=event_id,
    )
