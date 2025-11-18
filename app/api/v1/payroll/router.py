from typing import Dict, Any, Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role
from app.services.payroll.payroll_service import PayrollService

router = APIRouter(prefix="/payroll", tags=["Payroll"])


# Create payroll run (per month / fiscal year / school)
@router.post("/runs")
def create_run(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.HR, Role.ACCOUNTANT, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = PayrollService(db)

    fiscal_year = int(payload["fiscal_year"])
    month = int(payload["month"])
    currency = payload.get("currency", "USD")
    meta = payload.get("meta") or {}

    return svc.start_run(
        school_id=user.school_id,
        fiscal_year=fiscal_year,
        month=month,
        currency=currency,
        meta=meta,
        created_by=user.id,
    )


# Attach employee item to run
@router.post("/runs/{run_id}/items")
def add_run_item(
    run_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.HR, Role.ACCOUNTANT, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = PayrollService(db)

    employee_id = int(payload["employee_id"])
    base_salary = Decimal(str(payload["base_salary"]))
    allowances = Decimal(str(payload.get("allowances", "0")))
    deductions = Decimal(str(payload.get("deductions", "0")))
    currency = payload.get("currency", "USD")
    department_id: Optional[int] = payload.get("department_id")
    meta = payload.get("meta") or {}

    return svc.add_item(
        school_id=user.school_id,
        run_id=run_id,
        employee_id=employee_id,
        base_salary=base_salary,
        allowances=allowances,
        deductions=deductions,
        currency=currency,
        department_id=department_id,
        meta=meta,
        created_by=user.id,
    )


# Approve run & push total expense to Finance/Budget
@router.post("/runs/{run_id}/approve")
def approve_run(
    run_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.HR, Role.ACCOUNTANT, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = PayrollService(db)

    department_id = payload.get("department_id")  # department that carries payroll expense
    fiscal_year = int(payload["fiscal_year"])
    method = payload.get("method", "bank_transfer")
    category = payload.get("category", "payroll")

    return svc.approve_run(
        school_id=user.school_id,
        run_id=run_id,
        department_id=department_id,
        fiscal_year=fiscal_year,
        method=method,
        category=category,
        created_by=user.id,
    )


# Run summary (gross / net / count)
@router.get("/runs/{run_id}/summary")
def run_summary(
    run_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.HR,
        Role.ACCOUNTANT,
        Role.SCHOOL_ADMIN,
        Role.SUPER_ADMIN,
        Role.PRINCIPAL,
    )),
):
    svc = PayrollService(db)
    return svc.run_summary(
        school_id=user.school_id,
        run_id=run_id,
    )


# Employee payslips across runs
@router.get("/employees/{employee_id}/payslips")
def employee_payslips(
    employee_id: int,
    fiscal_year: int = Query(None, description="Optional fiscal year filter"),
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.HR,
        Role.ACCOUNTANT,
        Role.SCHOOL_ADMIN,
        Role.SUPER_ADMIN,
        Role.PRINCIPAL,
    )),
):
    svc = PayrollService(db)
    return svc.employee_payslips(
        school_id=user.school_id,
        employee_id=employee_id,
        fiscal_year=fiscal_year,
    )
