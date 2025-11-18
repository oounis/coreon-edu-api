from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    ForeignKey,
    Boolean,
    Numeric,
    JSON,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class FeeStructure(Base):
    """
    Fee plan for a school.
    Example rows:
        - tuition (monthly or yearly)
        - transport
        - books
    """

    __tablename__ = "fee_structures"
    __table_args__ = (
        UniqueConstraint("school_id", "name", name="uq_fee_structure_name"),
    )

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(200), nullable=False)
    details = Column(JSON, nullable=True)   # {"monthly": 150, "yearly": 1500, ...}

    active = Column(Boolean, nullable=False, server_default="true")

    school = relationship("School")


class StudentFee(Base):
    """
    Assigned fee structure per student.
    """

    __tablename__ = "student_fees"
    __table_args__ = (
        UniqueConstraint("student_id", "fee_structure_id", name="uq_student_fee"),
    )

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    fee_structure_id = Column(
        Integer,
        ForeignKey("fee_structures.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    school = relationship("School")
    student = relationship("StudentProfile")
    fee_structure = relationship("FeeStructure")


class Discount(Base):
    """
    Discount types:
        - sibling
        - staff child
        - excellence scholarship
        - custom
    """

    __tablename__ = "discounts"

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(200), nullable=False)
    percentage = Column(Numeric(5,2), nullable=True)
    fixed_amount = Column(Numeric(10,2), nullable=True)


class StudentDiscount(Base):
    """
    Discount applied to student.
    """

    __tablename__ = "student_discounts"
    __table_args__ = (
        UniqueConstraint("student_id", "discount_id", name="uq_student_discount"),
    )

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    discount_id = Column(
        Integer,
        ForeignKey("discounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )


class Invoice(Base):
    """
    Monthly/Yearly invoice for student.
    """

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    amount = Column(Numeric(10,2), nullable=False)
    status = Column(String(50), nullable=False, server_default="unpaid")  # paid/unpaid/partial
    due_date = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Payment(Base):
    """
    Payment entries for invoices.
    """

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    invoice_id = Column(
        Integer,
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    amount = Column(Numeric(10,2), nullable=False)
    method = Column(String(50), nullable=True)  # cash/bank/card/etc
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    invoice = relationship("Invoice")
