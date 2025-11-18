from __future__ import annotations
from typing import List, Dict, Any, Optional
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import (
    Student,
    FinanceInvoice,
    FinanceInvoiceLine,
    FinancePayment,
)
from app.services.finance.budget_service import BudgetService


class BillingService:
    """
    Student-centric billing:

    - Issue invoices (tuition, transport, canteen, activities...)
    - Register payments (cash, bank, online...)
    - Compute student balance (per school / per year)
    """

    def __init__(self, db: Session):
        self.db = db
        self.budgets = BudgetService(db)

    # ------------ Invoices ------------

    def create_invoice(
        self,
        *,
        school_id: int,
        student_id: int,
        fiscal_year: int,
        due_date,
        currency: str = "USD",
        items: List[Dict[str, Any]],
        meta: Optional[Dict[str, Any]] = None,
        created_by: Optional[int] = None,
    ) -> Dict[str, Any]:
        # basic student check
        student = (
            self.db.query(Student)
            .filter(Student.id == student_id)
            .filter(Student.school_id == school_id)
            .first()
        )
        if not student:
            raise ValueError("Student not found in this school")

        invoice = FinanceInvoice(
            school_id=school_id,
            student_id=student_id,
            fiscal_year=fiscal_year,
            currency=currency,
            due_date=due_date,
            meta=meta or {},
            status="pending",
            total_amount=Decimal("0"),
            created_by=created_by,
        )
        self.db.add(invoice)
        self.db.flush()  # get invoice.id

        total = Decimal("0")
        lines: list[FinanceInvoiceLine] = []

        for item in items:
            unit_price = Decimal(str(item.get("unit_price", "0")))
            qty = Decimal(str(item.get("qty", "1")))
            line_total = unit_price * qty

            line = FinanceInvoiceLine(
                invoice_id=invoice.id,
                title=item.get("title", "Item"),
                description=item.get("description"),
                category=item.get("category"),  # "tuition" | "transport" | ...
                unit_price=unit_price,
                qty=qty,
                total=line_total,
                meta=item.get("meta") or {},
            )
            self.db.add(line)
            lines.append(line)
            total += line_total

        invoice.total_amount = total

        self.db.commit()
        self.db.refresh(invoice)

        return {
            "invoice": invoice,
            "lines": lines,
        }

    # ------------ Payments ------------

    def add_payment(
        self,
        *,
        school_id: int,
        invoice_id: int,
        amount: Decimal,
        method: str = "cash",   # "cash" | "bank_transfer" | "card" | "online"
        reference: Optional[str] = None,
        department_id: Optional[int] = None,  # finance dept for income
        fiscal_year: Optional[int] = None,
        created_by: Optional[int] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        invoice = (
            self.db.query(FinanceInvoice)
            .filter(FinanceInvoice.id == invoice_id)
            .filter(FinanceInvoice.school_id == school_id)
            .first()
        )
        if not invoice:
            raise ValueError("Invoice not found in this school")

        payment = FinancePayment(
            invoice_id=invoice.id,
            school_id=school_id,
            student_id=invoice.student_id,
            amount=amount,
            method=method,
            reference=reference,
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(payment)

        # update invoice paid/remaining
        paid_sum = (
            self.db.query(FinancePayment)
            .filter(FinancePayment.invoice_id == invoice.id)
            .with_entities(FinancePayment.amount)
            .all()
        )
        total_paid = sum([p[0] for p in paid_sum]) + amount
        remaining = (invoice.total_amount or Decimal("0")) - total_paid

        if remaining <= 0:
            invoice.status = "paid"
        elif total_paid > 0:
            invoice.status = "partial"
        else:
            invoice.status = "pending"

        # (optional) register income into department budget
        if department_id and fiscal_year:
            try:
                self.budgets.register_transaction(
                    school_id=school_id,
                    department_id=department_id,
                    fiscal_year=fiscal_year,
                    amount=amount,
                    currency=invoice.currency,
                    kind="income",
                    method=method,
                    category="tuition",
                    reference=reference,
                    source="tuition",
                    request_id=None,
                    created_by=created_by,
                    meta={
                        "invoice_id": invoice.id,
                        "student_id": invoice.student_id,
                        **(meta or {}),
                    },
                )
            except Exception:
                # finance integration must not break core billing
                pass

        self.db.commit()
        self.db.refresh(invoice)
        self.db.refresh(payment)

        return {
            "invoice": invoice,
            "payment": payment,
            "remaining": remaining,
        }

    # ------------ Student balance ------------

    def student_summary(
        self,
        *,
        school_id: int,
        student_id: int,
        fiscal_year: Optional[int] = None,
    ) -> Dict[str, Any]:
        q_invoices = (
            self.db.query(FinanceInvoice)
            .filter(FinanceInvoice.school_id == school_id)
            .filter(FinanceInvoice.student_id == student_id)
        )
        if fiscal_year:
            q_invoices = q_invoices.filter(FinanceInvoice.fiscal_year == fiscal_year)

        invoices = q_invoices.all()

        invoice_ids = [inv.id for inv in invoices] or [0]

        payments = (
            self.db.query(FinancePayment)
            .filter(FinancePayment.school_id == school_id)
            .filter(FinancePayment.student_id == student_id)
            .filter(FinancePayment.invoice_id.in_(invoice_ids))
            .all()
        )

        total_invoices = sum([(inv.total_amount or Decimal("0")) for inv in invoices])
        total_paid = sum([p.amount for p in payments])
        remaining = total_invoices - total_paid

        return {
            "student_id": student_id,
            "fiscal_year": fiscal_year,
            "total_invoices": total_invoices,
            "total_paid": total_paid,
            "remaining": remaining,
            "invoices_count": len(invoices),
            "payments_count": len(payments),
        }
