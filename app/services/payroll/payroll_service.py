from __future__ import annotations
from typing import Dict, Any, Optional, List
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import (
    # NOTE: تأكد من أسماء الموديلات في models.py أو عدّلها لاحقاً
    Employee,
    PayrollRun,
    PayrollItem,
)
from app.services.finance.budget_service import BudgetService
from app.services.notification_service import NotificationService


class PayrollService:
    """
    Core payroll engine:
    - Create payroll runs (per month / year / school)
    - Attach employee items (salary + allowances + deductions)
    - Approve run -> push expense into Finance/Budget
    - Expose summaries & employee payslips
    """

    def __init__(self, db: Session):
        self.db = db
        self.budgets = BudgetService(db)
        self.notifications = NotificationService(db)

    # ---------- Runs ----------

    def start_run(
        self,
        *,
        school_id: int,
        fiscal_year: int,
        month: int,
        currency: str = "USD",
        meta: Optional[Dict[str, Any]] = None,
        created_by: Optional[int] = None,
    ) -> Dict[str, Any]:
        run = PayrollRun(
            school_id=school_id,
            fiscal_year=fiscal_year,
            month=month,
            currency=currency,
            status="draft",  # draft | approved | closed
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)

        return {"run": run}

    # ---------- Items (employees in a run) ----------

    def add_item(
        self,
        *,
        school_id: int,
        run_id: int,
        employee_id: int,
        base_salary: Decimal,
        allowances: Decimal = Decimal("0"),
        deductions: Decimal = Decimal("0"),
        currency: str = "USD",
        department_id: Optional[int] = None,
        meta: Optional[Dict[str, Any]] = None,
        created_by: Optional[int] = None,
    ) -> Dict[str, Any]:
        run = (
            self.db.query(PayrollRun)
            .filter(PayrollRun.id == run_id)
            .filter(PayrollRun.school_id == school_id)
            .first()
        )
        if not run:
            raise ValueError("Payroll run not found for this school")

        employee = (
            self.db.query(Employee)
            .filter(Employee.id == employee_id)
            .filter(Employee.school_id == school_id)
            .first()
        )
        if not employee:
            raise ValueError("Employee not found in this school")

        gross = base_salary + allowances
        net = gross - deductions

        item = PayrollItem(
            run_id=run.id,
            employee_id=employee_id,
            department_id=department_id,
            school_id=school_id,
            base_salary=base_salary,
            total_allowances=allowances,
            total_deductions=deductions,
            gross_amount=gross,
            net_amount=net,
            currency=currency or run.currency,
            meta=meta or {},
            created_by=created_by,
        )

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)

        return {
            "run": run,
            "item": item,
        }

    # ---------- Approve run (push to Finance/Budget) ----------

    def approve_run(
        self,
        *,
        school_id: int,
        run_id: int,
        department_id: Optional[int],
        fiscal_year: int,
        method: str = "bank_transfer",  # bank_transfer | cash | card | online
        category: str = "payroll",
        created_by: Optional[int] = None,
    ) -> Dict[str, Any]:
        run = (
            self.db.query(PayrollRun)
            .filter(PayrollRun.id == run_id)
            .filter(PayrollRun.school_id == school_id)
            .first()
        )
        if not run:
            raise ValueError("Payroll run not found for this school")

        items: List[PayrollItem] = (
            self.db.query(PayrollItem)
            .filter(PayrollItem.run_id == run.id)
            .all()
        )

        total_net = sum([(i.net_amount or Decimal("0")) for i in items]) if items else Decimal("0")

        # Finance integration (as expense on department budget)
        if department_id and total_net > 0:
            try:
                self.budgets.register_transaction(
                    school_id=school_id,
                    department_id=department_id,
                    fiscal_year=fiscal_year,
                    amount=total_net,
                    currency=run.currency,
                    kind="expense",
                    method=method,
                    category=category,
                    reference=f"payroll-run-{run.id}",
                    source="payroll",
                    request_id=None,
                    created_by=created_by,
                    meta={"payroll_run_id": run.id},
                )
            except Exception:
                # مالازمش الفينانس تطيّح السيستام
                pass

        run.status = "approved"
        self.db.commit()
        self.db.refresh(run)

        # Optional: notify HR / admins
        try:
            self.notifications.create(
                user_id=created_by or 0,
                school_id=school_id,
                key="payroll_run_approved",
                type="finance",
                category="payroll",
                data={"run_id": run.id, "total_net": str(total_net)},
                priority="high",
            )
        except Exception:
            pass

        return {
            "run": run,
            "total_net": total_net,
            "items_count": len(items),
        }

    # ---------- Summaries ----------

    def run_summary(
        self,
        *,
        school_id: int,
        run_id: int,
    ) -> Dict[str, Any]:
        run = (
            self.db.query(PayrollRun)
            .filter(PayrollRun.id == run_id)
            .filter(PayrollRun.school_id == school_id)
            .first()
        )
        if not run:
            raise ValueError("Payroll run not found for this school")

        items: List[PayrollItem] = (
            self.db.query(PayrollItem)
            .filter(PayrollItem.run_id == run.id)
            .all()
        )

        total_gross = sum([(i.gross_amount or Decimal("0")) for i in items]) if items else Decimal("0")
        total_net = sum([(i.net_amount or Decimal("0")) for i in items]) if items else Decimal("0")

        return {
            "run": run,
            "items": items,
            "total_gross": total_gross,
            "total_net": total_net,
            "count": len(items),
        }

    def employee_payslips(
        self,
        *,
        school_id: int,
        employee_id: int,
        fiscal_year: Optional[int] = None,
    ) -> Dict[str, Any]:
        q = (
            self.db.query(PayrollItem, PayrollRun)
            .join(PayrollRun, PayrollItem.run_id == PayrollRun.id)
            .filter(PayrollItem.employee_id == employee_id)
            .filter(PayrollRun.school_id == school_id)
        )
        if fiscal_year is not None:
            q = q.filter(PayrollRun.fiscal_year == fiscal_year)

        rows = q.all()

        payslips: List[Dict[str, Any]] = []
        for item, run in rows:
            payslips.append(
                {
                    "run_id": run.id,
                    "fiscal_year": run.fiscal_year,
                    "month": run.month,
                    "status": run.status,
                    "currency": item.currency or run.currency,
                    "base_salary": item.base_salary,
                    "total_allowances": item.total_allowances,
                    "total_deductions": item.total_deductions,
                    "gross_amount": item.gross_amount,
                    "net_amount": item.net_amount,
                    "meta": item.meta,
                }
            )

        return {
            "employee_id": employee_id,
            "fiscal_year": fiscal_year,
            "payslips": payslips,
        }
