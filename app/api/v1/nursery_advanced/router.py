from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role

from app.services.nursery_advanced.nursery_advanced_service import NurseryAdvancedService

router = APIRouter(prefix="/nursery-advanced", tags=["NurseryAdvanced"])

@router.post("/{student_id}/logs")
def log(student_id: int, payload: Dict[str, Any], db: Session = Depends(get_db),
        user=Depends(require_roles(Role.TEACHER, Role.NURSERY, Role.SCHOOL_ADMIN))):
    svc = NurseryAdvancedService(db)
    return svc.log(
        school_id=user.school_id,
        student_id=student_id,
        log_type=payload["log_type"],
        details=payload.get("details") or {},
        created_by=user.id,
    )

@router.get("/{student_id}/logs")
def list_logs(student_id: int, db: Session = Depends(get_db),
              user=Depends(require_roles(Role.TEACHER, Role.NURSERY, Role.PARENT))):
    svc = NurseryAdvancedService(db)
    return svc.list(
        school_id=user.school_id,
        student_id=student_id,
    )
