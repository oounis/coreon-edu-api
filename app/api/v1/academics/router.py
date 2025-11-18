from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role
from app.services.academics.academics_service import AcademicsService

router = APIRouter(prefix="/academics", tags=["Academics"])

# SUBJECTS
@router.post("/subjects")
def create_subject(payload: Dict[str, Any], db: Session = Depends(get_db), user=Depends(require_roles(
    Role.SCHOOL_ADMIN, Role.SUPER_ADMIN
))):
    svc = AcademicsService(db)
    return svc.create_subject(
        school_id=user.school_id,
        title=payload["title"],
        code=payload["code"],
        level=payload["level"],
        meta=payload.get("meta") or {},
        created_by=user.id,
    )

@router.get("/subjects")
def list_subjects(db: Session = Depends(get_db), user=Depends(require_roles(
    Role.TEACHER, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN
))):
    svc = AcademicsService(db)
    return svc.list_subjects(school_id=user.school_id)


# CURRICULUM
@router.post("/curriculum")
def create_curriculum(payload: Dict[str, Any], db: Session = Depends(get_db), user=Depends(require_roles(
    Role.SCHOOL_ADMIN, Role.SUPER_ADMIN
))):
    svc = AcademicsService(db)
    return svc.create_curriculum(
        school_id=user.school_id,
        title=payload["title"],
        description=payload.get("description", ""),
        grade=payload["grade"],
        meta=payload.get("meta") or {},
        created_by=user.id,
    )

@router.get("/curriculum")
def list_curriculum(db: Session = Depends(get_db), user=Depends(require_roles(
    Role.TEACHER, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN
))):
    svc = AcademicsService(db)
    return svc.list_curriculum(school_id=user.school_id)


# TERMS
@router.post("/terms")
def create_term(payload: Dict[str, Any], db: Session = Depends(get_db), user=Depends(require_roles(
    Role.SCHOOL_ADMIN, Role.SUPER_ADMIN
))):
    svc = AcademicsService(db)
    return svc.create_term(
        school_id=user.school_id,
        title=payload["title"],
        start_date=datetime.fromisoformat(payload["start_date"]),
        end_date=datetime.fromisoformat(payload["end_date"]),
        meta=payload.get("meta") or {},
        created_by=user.id,
    )

@router.get("/terms")
def list_terms(db: Session = Depends(get_db), user=Depends(require_roles(
    Role.TEACHER, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN
))):
    svc = AcademicsService(db)
    return svc.list_terms(school_id=user.school_id)


# TEACHER ASSIGNMENT
@router.post("/assignments")
def assign_teacher(payload: Dict[str, Any], db: Session = Depends(get_db), user=Depends(require_roles(
    Role.SCHOOL_ADMIN, Role.SUPER_ADMIN
))):
    svc = AcademicsService(db)
    return svc.assign_teacher(
        school_id=user.school_id,
        subject_id=payload["subject_id"],
        teacher_id=payload["teacher_id"],
        class_id=payload["class_id"],
        meta=payload.get("meta") or {},
        created_by=user.id,
    )

@router.get("/assignments")
def list_assignments(
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.TEACHER, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = AcademicsService(db)
    return svc.list_assignments(school_id=user.school_id, class_id=class_id)


# LESSON PLANS
@router.post("/lesson-plans")
def create_lesson_plan(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.TEACHER, Role.SUPER_ADMIN)),
):
    svc = AcademicsService(db)
    return svc.create_lesson_plan(
        school_id=user.school_id,
        teacher_id=user.id,
        class_id=payload["class_id"],
        subject_id=payload["subject_id"],
        date=datetime.fromisoformat(payload["date"]),
        title=payload["title"],
        content=payload["content"],
        meta=payload.get("meta") or {},
        created_by=user.id,
    )

@router.get("/lesson-plans")
def list_lesson_plans(
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.TEACHER, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = AcademicsService(db)
    return svc.list_lesson_plans(school_id=user.school_id, class_id=class_id)

