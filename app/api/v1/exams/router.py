from typing import Dict, Any, Optional
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role
from app.services.exams.exams_service import ExamsService

router = APIRouter(prefix="/exams", tags=["Exams"])


# ------------------------------
# EXAMS
# ------------------------------
@router.post("/")
def create_exam(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.SCHOOL_ADMIN, Role.SUPER_ADMIN, Role.PRINCIPAL)),
):
    svc = ExamsService(db)
    return svc.create_exam(
        school_id=user.school_id,
        title=payload["title"],
        grade=payload["grade"],
        term_id=payload["term_id"],
        description=payload.get("description"),
        meta=payload.get("meta") or {},
        created_by=user.id,
    )


@router.get("/")
def list_exams(
    grade: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TEACHER, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN, Role.PRINCIPAL
    )),
):
    svc = ExamsService(db)
    return svc.list_exams(school_id=user.school_id, grade=grade)


# ------------------------------
# SESSIONS
# ------------------------------
@router.post("/{exam_id}/sessions")
def create_session(
    exam_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.TEACHER, Role.SUPER_ADMIN, Role.SCHOOL_ADMIN)),
):
    svc = ExamsService(db)

    return svc.create_session(
        school_id=user.school_id,
        exam_id=exam_id,
        subject_id=payload["subject_id"],
        date=datetime.fromisoformat(payload["date"]),
        start_time=datetime.fromisoformat(payload["start_time"]),
        end_time=datetime.fromisoformat(payload["end_time"]),
        room=payload.get("room"),
        meta=payload.get("meta") or {},
        created_by=user.id,
    )


@router.get("/{exam_id}/sessions")
def list_sessions(
    exam_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TEACHER, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN
    )),
):
    svc = ExamsService(db)
    return svc.list_sessions(school_id=user.school_id, exam_id=exam_id)


# ------------------------------
# MARKS
# ------------------------------
@router.post("/{exam_id}/sessions/{session_id}/marks")
def enter_mark(
    exam_id: int,
    session_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.TEACHER, Role.SUPER_ADMIN)),
):
    svc = ExamsService(db)

    return svc.enter_mark(
        school_id=user.school_id,
        exam_id=exam_id,
        session_id=session_id,
        student_id=payload["student_id"],
        subject_id=payload["subject_id"],
        score=Decimal(str(payload["score"])),
        meta=payload.get("meta") or {},
        created_by=user.id,
    )


@router.get("/{exam_id}/marks")
def list_marks(
    exam_id: int,
    student_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TEACHER, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN, Role.PARENT, Role.PRINCIPAL
    )),
):
    svc = ExamsService(db)
    return svc.list_marks(school_id=user.school_id, exam_id=exam_id, student_id=student_id)


# ------------------------------
# GRADEBOOK
# ------------------------------
@router.get("/{exam_id}/gradebook")
def gradebook(
    exam_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TEACHER, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN, Role.PRINCIPAL
    )),
):
    svc = ExamsService(db)
    return svc.compute_gradebook(school_id=user.school_id, exam_id=exam_id)

