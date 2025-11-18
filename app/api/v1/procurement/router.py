from typing import Dict, Any, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role
from app.services.purchasing.purchasing_service import PurchasingService

router = APIRouter(prefix="/procurement", tags=["Procurement"])


# ---------------- Vendors ----------------
@router.post("/vendors")
def create_vendor(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.ACCOUNTANT, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = PurchasingService(db)
    return svc.create_vendor(
        school_id=user.school_id,
        payload=payload,
        created_by=user.id,
    )


# ---------------- Purchase Requests ----------------
@router.post("/purchase-requests")
def create_pr(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.ACCOUNTANT, Role.DEPARTMENT_HEAD, Role.SCHOOL_ADMIN)),
):
    svc = PurchasingService(db)

    return svc.create_purchase_request(
        school_id=user.school_id,
        department_id=int(payload["department_id"]),
        fiscal_year=int(payload["fiscal_year"]),
        items=payload.get("items") or [],
        meta=payload.get("meta") or {},
        created_by=user.id,
    )


# ---------------- Purchase Orders ----------------
@router.post("/purchase-orders")
def create_po(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.ACCOUNTANT, Role.SCHOOL_ADMIN)),
):
    svc = PurchasingService(db)

    return svc.create_purchase_order(
        school_id=user.school_id,
        vendor_id=int(payload["vendor_id"]),
        pr_id=int(payload["pr_id"]),
        items=payload.get("items") or [],
        fiscal_year=int(payload["fiscal_year"]),
        department_id=int(payload["department_id"]),
        created_by=user.id,
        meta=payload.get("meta") or {},
    )
