from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role

from app.services.audit_intel.audit_intel_service import AuditIntelService

router = APIRouter(prefix="/audit-intel", tags=["AuditIntel"])

@router.get("/search")
def search(
    actor_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    since: Optional[str] = Query(None),
    until: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.SUPER_ADMIN, Role.SCHOOL_ADMIN)),
):
    svc = AuditIntelService(db)
    return svc.search(
        school_id=user.school_id,
        actor_id=actor_id,
        action=action,
        since=since,
        until=until,
    )
