from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role
from app.services.attendance.attendance_service import AttendanceService

router = APIRouter(prefix="/attendance", tags=["Attendance"])


# --------------------------
# Single scan
# --------------------------
@router.post("/scan")
def scan(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TEACHER, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN
    )),
):
    svc = AttendanceService(db)

    ts_raw = payload.get("timestamp")
    ts = datetime.fromisoformat(ts_raw) if ts_raw else None

    return svc.scan(
        school_id=user.school_id,
        student_id=payload["student_id"],
        status=payload.get("status", "present"),
        timestamp=ts,
        meta=payload.get("meta") or {},
        created_by=user.id,
        notify_parent=bool(payload.get("notify_parent", True)),
    )


# --------------------------
# Bulk class attendance
# --------------------------
@router.post("/classrooms/{classroom_id}/bulk")
def bulk_class_attendance(
    classroom_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TEACHER, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN
    )),
):
    svc = AttendanceService(db)
    return svc.bulk_class_attendance(
        school_id=user.school_id,
        classroom_id=classroom_id,
        items=payload["items"],
        created_by=user.id,
    )


# --------------------------
# Student history
# --------------------------
@router.get("/students/{student_id}/history")
def student_history(
    student_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TEACHER, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN, Role.PARENT
    )),
):
    svc = AttendanceService(db)
    return svc.student_history(
        school_id=user.school_id,
        student_id=student_id,
    )
