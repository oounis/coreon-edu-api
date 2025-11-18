from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role
from app.services.timetable.timetable_service import TimetableService

router = APIRouter(prefix="/timetable", tags=["Timetable"])


# -------------------------------------
# Create timetable entry
# -------------------------------------
@router.post("/")
def create_entry(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.SCHOOL_ADMIN,
        Role.SUPER_ADMIN,
        Role.PRINCIPAL,
    )),
):
    svc = TimetableService(db)
    return svc.create_entry(
        school_id=user.school_id,
        class_id=payload["class_id"],
        subject_id=payload["subject_id"],
        teacher_id=payload["teacher_id"],
        room_id=payload["room_id"],
        day_of_week=payload["day_of_week"],
        start_time=payload["start_time"],
        end_time=payload["end_time"],
        meta=payload.get("meta") or {},
        created_by=user.id,
    )


# -------------------------------------
# Class timetable
# -------------------------------------
@router.get("/class/{class_id}")
def class_timetable(
    class_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TEACHER,
        Role.STUDENT,
        Role.PARENT,
        Role.SCHOOL_ADMIN,
        Role.SUPER_ADMIN,
    )),
):
    svc = TimetableService(db)
    return svc.class_timetable(
        school_id=user.school_id,
        class_id=class_id,
    )


# -------------------------------------
# Teacher schedule
# -------------------------------------
@router.get("/teacher/{teacher_id}")
def teacher_timetable(
    teacher_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TEACHER,
        Role.SCHOOL_ADMIN,
        Role.SUPER_ADMIN,
        Role.PRINCIPAL,
    )),
):
    svc = TimetableService(db)
    return svc.teacher_timetable(
        school_id=user.school_id,
        teacher_id=teacher_id,
    )


# -------------------------------------
# Room timetable
# -------------------------------------
@router.get("/room/{room_id}")
def room_timetable(
    room_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.SCHOOL_ADMIN,
        Role.SUPER_ADMIN,
        Role.PRINCIPAL,
    )),
):
    svc = TimetableService(db)
    return svc.room_timetable(
        school_id=user.school_id,
        room_id=room_id,
    )


# -------------------------------------
# Delete entry
# -------------------------------------
@router.delete("/{entry_id}")
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = TimetableService(db)
    return svc.delete_entry(
        school_id=user.school_id,
        entry_id=entry_id,
    )
