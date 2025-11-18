from datetime import datetime

from sqlalchemy import Column, Integer, String, Numeric, DateTime
from app.db.session import Base


class PayrollBonus(Base):
    __tablename__ = "payroll_bonus"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, index=True, nullable=False)
    employee_id = Column(Integer, index=True, nullable=False)
    reason = Column(String, nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    effective_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=True)


class PayrollDeduction(Base):
    __tablename__ = "payroll_deduction"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, index=True, nullable=False)
    employee_id = Column(Integer, index=True, nullable=False)
    reason = Column(String, nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    effective_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
