from typing import Dict, Any
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role

from app.services.hr_payroll.hr_payroll_service import HRPayrollService

router = APIRouter(prefix="/hr-payroll", tags=["HRPayroll"])

@router.post("/bonus")
def add_bonus(payload: Dict[str, Any], db: Session = Depends(get_db),
              user=Depends(require_roles(Role.HR, Role.SCHOOL_ADMIN))):
    svc = HRPayrollService(db)
    return svc.add_bonus(
        school_id=user.school_id,
        employee_id=payload["employee_id"],
        amount=Decimal(str(payload["amount"])),
        reason=payload["reason"],
        created_by=user.id,
    )

@router.post("/deduction")
def add_deduction(payload: Dict[str, Any], db: Session = Depends(get_db),
                  user=Depends(require_roles(Role.HR, Role.SCHOOL_ADMIN))):
    svc = HRPayrollService(db)
    return svc.add_deduction(
        school_id=user.school_id,
        employee_id=payload["employee_id"],
        amount=Decimal(str(payload["amount"])),
        reason=payload["reason"],
        created_by=user.id,
    )
