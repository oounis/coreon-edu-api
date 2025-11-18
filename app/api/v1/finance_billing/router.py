from typing import Dict, Any, List
from decimal import Decimal
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role
from app.services.finance.billing_service import BillingService

router = APIRouter(prefix="/finance/billing", tags=["FinanceBilling"])


@router.post("/invoices")
def create_invoice(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.ACCOUNTANT, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = BillingService(db)

    student_id = int(payload["student_id"])
    fiscal_year = int(payload.get("fiscal_year"))
    due_date = date.fromisoformat(payload.get("due_date"))
    currency = payload.get("currency", "USD")
    items: List[Dict[str, Any]] = payload.get("items") or []
    meta = payload.get("meta") or {}

    return svc.create_invoice(
        school_id=user.school_id,
        student_id=student_id,
        fiscal_year=fiscal_year,
        due_date=due_date,
        currency=currency,
        items=items,
        meta=meta,
        created_by=user.id,
    )


@router.post("/invoices/{invoice_id}/pay")
def pay_invoice(
    invoice_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.ACCOUNTANT, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = BillingService(db)

    amount = Decimal(str(payload["amount"]))
    method = payload.get("method", "cash")
    reference = payload.get("reference")
    department_id = payload.get("department_id")  # finance dept id
    fiscal_year = payload.get("fiscal_year")
    meta = payload.get("meta") or {}

    return svc.add_payment(
        school_id=user.school_id,
        invoice_id=invoice_id,
        amount=amount,
        method=method,
        reference=reference,
        department_id=department_id,
        fiscal_year=fiscal_year,
        created_by=user.id,
        meta=meta,
    )


@router.get("/students/{student_id}/summary")
def student_summary(
    student_id: int,
    fiscal_year: int = Query(None, description="Optional fiscal year filter"),
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.ACCOUNTANT,
        Role.SCHOOL_ADMIN,
        Role.SUPER_ADMIN,
        Role.PRINCIPAL,
    )),
):
    svc = BillingService(db)
    return svc.student_summary(
        school_id=user.school_id,
        student_id=student_id,
        fiscal_year=fiscal_year,
    )
