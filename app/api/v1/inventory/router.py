from typing import Dict, Any
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role

from app.services.inventory.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.post("/")
def create_item(payload: Dict[str, Any], db: Session = Depends(get_db),
                user=Depends(require_roles(Role.STOCK_MANAGER, Role.SCHOOL_ADMIN))):
    svc = InventoryService(db)
    return svc.create_item(
        school_id=user.school_id,
        name=payload["name"],
        category=payload["category"],
        qty=Decimal(str(payload["qty"])),
        threshold=Decimal(str(payload["threshold"])),
        meta=payload.get("meta") or {},
        created_by=user.id,
    )

@router.get("/")
def list_items(db: Session = Depends(get_db),
               user=Depends(require_roles(Role.STOCK_MANAGER, Role.TEACHER))):
    svc = InventoryService(db)
    return svc.list_items(school_id=user.school_id)

@router.post("/{item_id}/in")
def stock_in(item_id: int, payload: Dict[str, Any], db: Session = Depends(get_db),
             user=Depends(require_roles(Role.STOCK_MANAGER))):
    svc = InventoryService(db)
    return svc.stock_in(
        school_id=user.school_id,
        item_id=item_id,
        qty=Decimal(str(payload["qty"])),
        created_by=user.id,
        meta=payload.get("meta") or {},
    )

@router.post("/{item_id}/out")
def stock_out(item_id: int, payload: Dict[str, Any], db: Session = Depends(get_db),
              user=Depends(require_roles(Role.STOCK_MANAGER))):
    svc = InventoryService(db)
    return svc.stock_out(
        school_id=user.school_id,
        item_id=item_id,
        qty=Decimal(str(payload["qty"])),
        created_by=user.id,
        meta=payload.get("meta") or {},
    )
