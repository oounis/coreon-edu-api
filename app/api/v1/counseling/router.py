from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role
from app.services.counseling.counseling_service import CounselingService

router = APIRouter(prefix="/counseling", tags=["Counseling"])

@router.post("/cases")
def open_case(payload: Dict[str, Any], db: Session = Depends(get_db),
              user=Depends(require_roles(Role.COUNSELOR, Role.SCHOOL_ADMIN))):
    svc = CounselingService(db)
    return svc.open_case(
        school_id=user.school_id,
        student_id=payload["student_id"],
        case_type=payload["case_type"],
        description=payload["description"],
        priority=payload.get("priority", "normal"),
        meta=payload.get("meta") or {},
        created_by=user.id,
    )

@router.get("/cases")
def list_cases(student_id: Optional[int] = None, db: Session = Depends(get_db),
               user=Depends(require_roles(Role.COUNSELOR, Role.SCHOOL_ADMIN))):
    svc = CounselingService(db)
    return svc.list_cases(school_id=user.school_id, student_id=student_id)

@router.post("/cases/{case_id}/sessions")
def add_session(case_id: int, payload: Dict[str, Any], db: Session = Depends(get_db),
                user=Depends(require_roles(Role.COUNSELOR))):
    svc = CounselingService(db)
    return svc.add_session(
        school_id=user.school_id,
        case_id=case_id,
        counselor_id=user.id,
        notes=payload["notes"],
        meta=payload.get("meta") or {},
        created_by=user.id,
    )

@router.post("/cases/{case_id}/notes")
def add_note(case_id: int, payload: Dict[str, Any], db: Session = Depends(get_db),
             user=Depends(require_roles(Role.COUNSELOR))):
    svc = CounselingService(db)
    return svc.add_note(
        school_id=user.school_id,
        case_id=case_id,
        note=payload["note"],
        created_by=user.id,
    )
