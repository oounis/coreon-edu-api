from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role
from app.services.parent_student.parent_student_service import ParentStudentService

router = APIRouter(prefix="/parent-student", tags=["ParentStudent"])


# ------------------------------------
# LINK parent to student
# ------------------------------------
@router.post("/link")
def link(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.SCHOOL_ADMIN, Role.SUPER_ADMIN, Role.HR)),
):
    svc = ParentStudentService(db)

    return svc.link(
        school_id=user.school_id,
        parent_id=payload["parent_id"],
        student_id=payload["student_id"],
        relation=payload.get("relation", "guardian"),
        meta=payload.get("meta") or {},
        created_by=user.id,
    )


# ------------------------------------
# UNLINK parent from student
# ------------------------------------
@router.post("/unlink")
def unlink(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = ParentStudentService(db)

    return svc.unlink(
        school_id=user.school_id,
        parent_id=payload["parent_id"],
        student_id=payload["student_id"],
        reason=payload.get("reason"),
        updated_by=user.id,
    )


# ------------------------------------
# Parent: list children
# ------------------------------------
@router.get("/parent/{parent_id}/children")
def parent_children(
    parent_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.PARENT, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN
    )),
):
    svc = ParentStudentService(db)
    return svc.parent_children(
        school_id=user.school_id,
        parent_id=parent_id,
    )


# ------------------------------------
# Student: list parents
# ------------------------------------
@router.get("/student/{student_id}/parents")
def student_parents(
    student_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.SCHOOL_ADMIN, Role.SUPER_ADMIN, Role.TEACHER
    )),
):
    svc = ParentStudentService(db)
    return svc.student_parents(
        school_id=user.school_id,
        student_id=student_id,
    )


# ------------------------------------
# Parent dashboard - student summary
# ------------------------------------
@router.get("/student/{student_id}/summary")
def student_summary(
    student_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.PARENT, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN, Role.PRINCIPAL
    )),
):
    svc = ParentStudentService(db)
    return svc.student_summary(
        school_id=user.school_id,
        student_id=student_id,
    )
