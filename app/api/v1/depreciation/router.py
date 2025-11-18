from typing import Dict, Any
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role
from app.services.depreciation.depreciation_service import DepreciationService

router = APIRouter(prefix="/depreciation", tags=["Depreciation"])

@router.post("/{asset_id}")
def run(asset_id: int, payload: Dict[str, Any], db: Session = Depends(get_db),
        user=Depends(require_roles(Role.ACCOUNTANT, Role.SCHOOL_ADMIN))):
    svc = DepreciationService(db)
    return svc.run_for_asset(
        school_id=user.school_id,
        asset_id=asset_id,
        useful_life_years=int(payload["useful_life_years"]),
        created_by=user.id,
    )

@router.get("/{asset_id}")
def list_records(asset_id: int, db: Session = Depends(get_db),
                 user=Depends(require_roles(Role.ACCOUNTANT, Role.SUPER_ADMIN))):
    svc = DepreciationService(db)
    return svc.list(school_id=user.school_id, asset_id=asset_id)
