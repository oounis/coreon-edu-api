from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role
from app.services.hr_lifecycle.hr_lifecycle_service import HRLifecycleService

router = APIRouter(prefix="/hr/lifecycle", tags=["HRLifecycle"])


@router.post("/hire")
def start_hiring(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.HR, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = HRLifecycleService(db)
    return svc.start_hiring(user=user, payload=payload)


@router.post("/terminate")
def start_termination(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.HR, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = HRLifecycleService(db)
    return svc.start_termination(user=user, payload=payload)


@router.post("/transfer")
def start_transfer(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.HR, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = HRLifecycleService(db)
    return svc.start_transfer(user=user, payload=payload)
