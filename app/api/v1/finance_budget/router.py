from typing import Dict, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from decimal import Decimal

from app.db.session import get_db
from app.core.security import get_current_user
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role
from app.services.finance.budget_service import BudgetService

router = APIRouter(prefix="/finance/budgets", tags=["FinanceBudgets"])


# Allocate / increase department budget
@router.post("/allocate")
def allocate_budget(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.ACCOUNTANT, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = BudgetService(db)

    department_id = int(payload["department_id"])
    fiscal_year = int(payload.get("fiscal_year"))
    amount = Decimal(str(payload["amount"]))
    currency = payload.get("currency", "USD")
    category = payload.get("category")
    meta = payload.get("meta") or {}

    return svc.allocate_budget(
        school_id=user.school_id,
        department_id=department_id,
        fiscal_year=fiscal_year,
        amount=amount,
        currency=currency,
        category=category,
        meta=meta,
        created_by=user.id,
    )


# Register expense / income
@router.post("/transaction")
def register_transaction(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.ACCOUNTANT, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = BudgetService(db)

    department_id = int(payload["department_id"])
    fiscal_year = int(payload.get("fiscal_year"))
    amount = Decimal(str(payload["amount"]))
    currency = payload.get("currency", "USD")
    kind = payload.get("kind", "expense")
    method = payload.get("method", "cash")
    category = payload.get("category")
    reference = payload.get("reference")
    source = payload.get("source")
    request_id = payload.get("request_id")
    meta = payload.get("meta") or {}

    return svc.register_transaction(
        school_id=user.school_id,
        department_id=department_id,
        fiscal_year=fiscal_year,
        amount=amount,
        currency=currency,
        kind=kind,
        method=method,
        category=category,
        reference=reference,
        source=source,
        request_id=request_id,
        created_by=user.id,
        meta=meta,
    )


# Get department budget summary
@router.get("/departments/{department_id}/summary")
def get_department_summary(
    department_id: int,
    fiscal_year: int = Query(..., description="Fiscal year e.g. 2025"),
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.ACCOUNTANT,
        Role.SCHOOL_ADMIN,
        Role.SUPER_ADMIN,
        Role.PRINCIPAL,
    )),
):
    svc = BudgetService(db)
    return svc.get_department_summary(
        school_id=user.school_id,
        department_id=department_id,
        fiscal_year=fiscal_year,
    )
