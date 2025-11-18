from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role

from app.services.procurement_advanced.procurement_advanced_service import ProcurementAdvancedService

router = APIRouter(prefix="/procurement-advanced", tags=["ProcurementAdvanced"])

@router.post("/vendors")
def create_vendor(payload: Dict[str, Any], db: Session = Depends(get_db),
                  user=Depends(require_roles(Role.PURCHASING, Role.SCHOOL_ADMIN))):
    svc = ProcurementAdvancedService(db)
    return svc.create_vendor(
        school_id=user.school_id,
        name=payload["name"],
        contact=payload.get("contact") or {},
        created_by=user.id,
    )

@router.post("/rfq")
def create_rfq(payload: Dict[str, Any], db: Session = Depends(get_db),
               user=Depends(require_roles(Role.PURCHASING))):
    svc = ProcurementAdvancedService(db)
    return svc.create_rfq(
        school_id=user.school_id,
        title=payload["title"],
        description=payload["description"],
        meta=payload.get("meta") or {},
        created_by=user.id,
    )

@router.post("/rfq/{rfq_id}/quotations")
def submit_quotation(rfq_id: int, payload: Dict[str, Any], db: Session = Depends(get_db),
                     user=Depends(require_roles(Role.PURCHASING))):
    svc = ProcurementAdvancedService(db)
    return svc.submit_quotation(
        school_id=user.school_id,
        rfq_id=rfq_id,
        vendor_id=payload["vendor_id"],
        amount=float(payload["amount"]),
        meta=payload.get("meta") or {},
        created_by=user.id,
    )
