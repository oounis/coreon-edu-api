from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role

from app.services.behavior_advanced.behavior_advanced_service import BehaviorAdvancedService

router = APIRouter(prefix="/behavior-advanced", tags=["BehaviorAdvanced"])

@router.post("/incidents")
def report(payload: Dict[str, Any], db: Session = Depends(get_db),
           user=Depends(require_roles(Role.TEACHER, Role.SUPERVISOR))):
    svc = BehaviorAdvancedService(db)
    return svc.report(
        school_id=user.school_id,
        student_id=payload["student_id"],
        severity=payload["severity"],
        description=payload["description"],
        meta=payload.get("meta") or {},
        location=payload.get("location"),
        created_by=user.id,
    )

@router.post("/incidents/{incident_id}/plans")
def create_plan(incident_id: int, payload: Dict[str, Any], db: Session = Depends(get_db),
                user=Depends(require_roles(Role.SUPERVISOR, Role.SCHOOL_ADMIN))):
    svc = BehaviorAdvancedService(db)
    return svc.create_plan(
        school_id=user.school_id,
        incident_id=incident_id,
        steps=payload["steps"],
        duration_days=int(payload["duration_days"]),
        created_by=user.id,
    )
