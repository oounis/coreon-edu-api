from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role
from app.services.homework.homework_service import HomeworkService

router = APIRouter(prefix="/homework", tags=["Homework"])


# --------------------------------
# Create homework
# --------------------------------
@router.post("/")
def create_homework(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.TEACHER, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = HomeworkService(db)

    return svc.create_homework(
        school_id=user.school_id,
        teacher_id=user.id,
        classroom_id=payload["classroom_id"],
        subject_id=payload["subject_id"],
        title=payload["title"],
        description=payload.get("description", ""),
        due_date=datetime.fromisoformat(payload["due_date"]),
        attachments=payload.get("attachments") or [],
        meta=payload.get("meta") or {},
    )


# --------------------------------
# List homework for classroom
# --------------------------------
@router.get("/{classroom_id}")
def list_homework(
    classroom_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TEACHER, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN,
        Role.PARENT, Role.STUDENT
    )),
):
    svc = HomeworkService(db)
    return svc.list_homework(
        school_id=user.school_id,
        classroom_id=classroom_id,
    )


# --------------------------------
# Submit homework
# --------------------------------
@router.post("/{homework_id}/submit")
def submit(
    homework_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.STUDENT)),
):
    svc = HomeworkService(db)

    submitted_at = (
        datetime.fromisoformat(payload["submitted_at"])
        if payload.get("submitted_at")
        else None
    )

    return svc.submit(
        school_id=user.school_id,
        homework_id=homework_id,
        student_id=user.id,
        content=payload.get("content"),
        attachments=payload.get("attachments") or [],
        submitted_at=submitted_at,
        meta=payload.get("meta") or {},
    )


# --------------------------------
# Review submission
# --------------------------------
@router.post("/{homework_id}/submissions/{submission_id}/review")
def review_submission(
    homework_id: int,
    submission_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.TEACHER, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = HomeworkService(db)

    return svc.review_submission(
        school_id=user.school_id,
        homework_id=homework_id,
        submission_id=submission_id,
        feedback=payload.get("feedback"),
        score=payload.get("score"),
        reviewed_by=user.id,
    )


# --------------------------------
# List submissions for homework
# --------------------------------
@router.get("/{homework_id}/submissions")
def list_submissions(
    homework_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TEACHER, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN
    )),
):
    svc = HomeworkService(db)
    return svc.list_submissions(
        school_id=user.school_id,
        homework_id=homework_id,
    )
