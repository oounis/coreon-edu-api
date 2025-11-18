from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role

from app.services.curriculum.curriculum_service import CurriculumService

router = APIRouter(prefix="/curriculum", tags=["Curriculum"])

@router.post("/plans")
def create_plan(payload: Dict[str, Any], db: Session = Depends(get_db),
                user=Depends(require_roles(Role.TEACHER, Role.SUPERVISOR))):
    svc = CurriculumService(db)
    return svc.create_plan(
        school_id=user.school_id,
        subject_id=payload["subject_id"],
        term=payload["term"],
        meta=payload.get("meta") or {},
        created_by=user.id,
    )

@router.post("/plans/{plan_id}/outcomes")
def add_outcome(plan_id: int, payload: Dict[str, Any], db: Session = Depends(get_db),
                user=Depends(require_roles(Role.TEACHER, Role.SUPERVISOR))):
    svc = CurriculumService(db)
    return svc.add_outcome(
        school_id=user.school_id,
        plan_id=plan_id,
        title=payload["title"],
        description=payload["description"],
        created_by=user.id,
    )

@router.post("/plans/{plan_id}/syllabus")
def add_syllabus(plan_id: int, payload: Dict[str, Any], db: Session = Depends(get_db),
                 user=Depends(require_roles(Role.TEACHER))):
    svc = CurriculumService(db)
    return svc.add_syllabus(
        school_id=user.school_id,
        plan_id=plan_id,
        title=payload["title"],
        content=payload["content"],
        created_by=user.id,
    )
