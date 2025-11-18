from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role
from app.services.behavior.behavior_service import BehaviorService

router = APIRouter(prefix="/behavior", tags=["Behavior"])


# -----------------------------
# Add incident
# -----------------------------
@router.post("/students/{student_id}/incidents")
def record_incident(
    student_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(
        require_roles(
            Role.TEACHER,
            Role.HR,
            Role.SCHOOL_ADMIN,
            Role.SUPER_ADMIN,
            Role.PRINCIPAL,
        )
    ),
):
    svc = BehaviorService(db)

    happened_raw = payload.get("happened_at")
    happened = datetime.fromisoformat(happened_raw) if happened_raw else None

    return svc.record_incident(
        school_id=user.school_id,
        student_id=student_id,
        title=payload["title"],
        description=payload.get("description", ""),
        type=payload.get("type", "negative"),
        severity=payload.get("severity", "low"),
        points=int(payload.get("points", -1)),
        happened_at=happened,
        meta=payload.get("meta") or {},
        created_by=user.id,
        notify_parent=bool(payload.get("notify_parent", True)),
    )


# -----------------------------
# Student history
# -----------------------------
@router.get("/students/{student_id}/history")
def student_history(
    student_id: int,
    db: Session = Depends(get_db),
    user=Depends(
        require_roles(
            Role.TEACHER,
            Role.HR,
            Role.PARENT,
            Role.SCHOOL_ADMIN,
            Role.SUPER_ADMIN,
            Role.PRINCIPAL,
        )
    ),
):
    svc = BehaviorService(db)
    return svc.student_history(
        school_id=user.school_id,
        student_id=student_id,
    )


# -----------------------------
# School summary
# -----------------------------
@router.get("/summary")
def school_summary(
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.SCHOOL_ADMIN, Role.SUPER_ADMIN, Role.PRINCIPAL
    )),
):
    svc = BehaviorService(db)
    return svc.school_summary(school_id=user.school_id)
