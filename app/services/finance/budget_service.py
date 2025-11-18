from __future__ import annotations
from typing import Optional, Dict, Any, List
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import (
    # NOTE: تأكد لاحقاً من أسماء الموديلات أو عدلها حسب سكيمتك
    Department,
    FinanceBudget,
    FinanceBudgetLine,
    FinanceTransaction,
)


class BudgetService:
    """
    Department-level budgeting & spending service.

    - Allocate yearly budgets to departments
    - Register expenses/incomes
    - Compute remaining budget per department / category
    """

    def __init__(self, db: Session):
        self.db = db

    # ---------- Internal helpers ----------

    def _get_or_create_budget(
        self,
        *,
        school_id: int,
        department_id: int,
        fiscal_year: int,
        currency: str = "USD",
    ) -> FinanceBudget:
        budget = (
            self.db.query(FinanceBudget)
            .filter(FinanceBudget.school_id == school_id)
            .filter(FinanceBudget.department_id == department_id)
            .filter(FinanceBudget.fiscal_year == fiscal_year)
            .first()
        )
        if budget:
            return budget

        budget = FinanceBudget(
            school_id=school_id,
            department_id=department_id,
            fiscal_year=fiscal_year,
            currency=currency,
            initial_amount=Decimal("0"),
            allocated_amount=Decimal("0"),
        )
        self.db.add(budget)
        self.db.flush()
        return budget

    # ---------- Public API ----------

    def allocate_budget(
        self,
        *,
        school_id: int,
        department_id: int,
        fiscal_year: int,
        amount: Decimal,
        currency: str = "USD",
        category: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        created_by: Optional[int] = None,
    ) -> Dict[str, Any]:
        budget = self._get_or_create_budget(
            school_id=school_id,
            department_id=department_id,
            fiscal_year=fiscal_year,
            currency=currency,
        )

        line = FinanceBudgetLine(
            budget_id=budget.id,
            category=category,
            amount=amount,
            currency=currency,
            meta=meta or {},
            created_by=created_by,
        )

        budget.allocated_amount = (budget.allocated_amount or Decimal("0")) + amount

        self.db.add(line)
        self.db.commit()
        self.db.refresh(budget)
        self.db.refresh(line)

        return {
            "budget": budget,
            "line": line,
        }

    def register_transaction(
        self,
        *,
        school_id: int,
        department_id: int,
        fiscal_year: int,
        amount: Decimal,
        currency: str = "USD",
        kind: str = "expense",  # "expense" | "income"
        method: str = "cash",   # "cash" | "card" | "bank_transfer" | "online" | ...
        category: Optional[str] = None,
        reference: Optional[str] = None,
        source: Optional[str] = None,      # e.g. "tuition", "canteen", "bus", ...
        request_id: Optional[int] = None,  # link to workflow request
        created_by: Optional[int] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        budget = self._get_or_create_budget(
            school_id=school_id,
            department_id=department_id,
            fiscal_year=fiscal_year,
            currency=currency,
        )

        if kind == "expense":
            signed_amount = -abs(Decimal(amount))
        else:
            signed_amount = abs(Decimal(amount))

        tx = FinanceTransaction(
            school_id=school_id,
            department_id=department_id,
            fiscal_year=fiscal_year,
            budget_id=budget.id,
            amount=signed_amount,
            currency=currency,
            kind=kind,
            method=method,
            category=category,
            reference=reference,
            source=source,
            request_id=request_id,
            created_by=created_by,
            meta=meta or {},
        )

        self.db.add(tx)
        self.db.flush()

        # Optionally: denormalized totals on budget
        # (depends on your real schema - adjust or remove)
        if hasattr(budget, "spent_amount"):
            budget.spent_amount = (budget.spent_amount or Decimal("0")) + (
                signed_amount if signed_amount < 0 else Decimal("0")
            )

        self.db.commit()
        self.db.refresh(tx)
        self.db.refresh(budget)

        return {
            "budget": budget,
            "transaction": tx,
        }

    def get_department_summary(
        self,
        *,
        school_id: int,
        department_id: int,
        fiscal_year: int,
    ) -> Dict[str, Any]:
        budget: FinanceBudget | None = (
            self.db.query(FinanceBudget)
            .filter(FinanceBudget.school_id == school_id)
            .filter(FinanceBudget.department_id == department_id)
            .filter(FinanceBudget.fiscal_year == fiscal_year)
            .first()
        )
        if not budget:
            return {
                "school_id": school_id,
                "department_id": department_id,
                "fiscal_year": fiscal_year,
                "currency": None,
                "allocated": "0",
                "spent": "0",
                "balance": "0",
                "by_category": {},
            }

        txs: List[FinanceTransaction] = (
            self.db.query(FinanceTransaction)
            .filter(FinanceTransaction.school_id == school_id)
            .filter(FinanceTransaction.department_id == department_id)
            .filter(FinanceTransaction.fiscal_year == fiscal_year)
            .all()
        )

        spent = Decimal("0")
        income = Decimal("0")
        by_category: Dict[str, Dict[str, str]] = {}

        for tx in txs:
            amt = Decimal(tx.amount)
            cat = tx.category or "uncategorized"
            if cat not in by_category:
                by_category[cat] = {"income": Decimal("0"), "expense": Decimal("0")}
            if amt < 0:
                spent += -amt
                by_category[cat]["expense"] += -amt
            else:
                income += amt
                by_category[cat]["income"] += amt

        # Convert Decimal -> str for JSON safety
        def _dec(v: Decimal) -> str:
            return str(v.quantize(Decimal("0.01")))

        by_category_str = {
            k: {"income": _dec(v["income"]), "expense": _dec(v["expense"])}
            for k, v in by_category.items()
        }

        allocated = budget.allocated_amount or Decimal("0")
        balance = allocated + income - spent

        return {
            "school_id": school_id,
            "department_id": department_id,
            "fiscal_year": fiscal_year,
            "currency": budget.currency,
            "allocated": _dec(allocated),
            "income": _dec(income),
            "spent": _dec(spent),
            "balance": _dec(balance),
            "by_category": by_category_str,
        }
