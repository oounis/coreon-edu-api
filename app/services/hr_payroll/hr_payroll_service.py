from __future__ import annotations
from typing import Dict, Any, List
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import PayrollBonus, PayrollDeduction


class HRPayrollService:
    """
    Extensions for payroll:
    - Bonuses
    - Deductions
    - Annual adjustments
    """

    def __init__(self, db: Session):
        self.db = db

    def add_bonus(self, *, school_id: int, employee_id: int, amount: Decimal,
                  reason: str, created_by: int):
        b = PayrollBonus(
            school_id=school_id,
            employee_id=employee_id,
            amount=amount,
            reason=reason,
            created_by=created_by,
        )
        self.db.add(b)
        self.db.commit()
        self.db.refresh(b)
        return {"bonus": b}

    def add_deduction(self, *, school_id: int, employee_id: int, amount: Decimal,
                      reason: str, created_by: int):
        d = PayrollDeduction(
            school_id=school_id,
            employee_id=employee_id,
            amount=amount,
            reason=reason,
            created_by=created_by,
        )
        self.db.add(d)
        self.db.commit()
        self.db.refresh(d)
        return {"deduction": d}
