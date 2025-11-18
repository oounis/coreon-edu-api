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
    func,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class StaffContract(Base):
    """
    Employment contract for staff.
    """

    __tablename__ = "staff_contracts"

    id = Column(Integer, primary_key=True, index=True)

    staff_id = Column(
        Integer,
        ForeignKey("staff_profiles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    position_title = Column(String(200), nullable=True)
    salary = Column(Numeric(10,2), nullable=True)
    contract_type = Column(String(100), nullable=True)  # full_time / part_time / contractor
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    active = Column(Boolean, nullable=False, server_default="true")

    staff = relationship("StaffProfile")


class StaffAttendance(Base):
    """
    Staff daily attendance record.
    """

    __tablename__ = "staff_attendance"
    __table_args__ = (
        UniqueConstraint("staff_id", "date", name="uq_staff_attendance_day"),
    )

    id = Column(Integer, primary_key=True, index=True)

    staff_id = Column(
        Integer,
        ForeignKey("staff_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    date = Column(DateTime(timezone=True), nullable=False)
    check_in = Column(DateTime(timezone=True), nullable=True)
    check_out = Column(DateTime(timezone=True), nullable=True)

    staff = relationship("StaffProfile")


class LeaveRequest(Base):
    """
    Leave request for staff: sick, annual, emergency, etc.
    """

    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)

    staff_id = Column(
        Integer,
        ForeignKey("staff_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    leave_type = Column(String(100), nullable=False)  # sick / annual / maternity / emergency
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    reason = Column(String(2000), nullable=True)

    status = Column(String(50), nullable=False, server_default="pending")  # pending / approved / rejected

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    staff = relationship("StaffProfile")


class StaffDocument(Base):
    """
    Uploaded HR documents:
        - passport
        - ID
        - certificates
        - contracts (pdf)
    """

    __tablename__ = "staff_documents"

    id = Column(Integer, primary_key=True, index=True)

    staff_id = Column(
        Integer,
        ForeignKey("staff_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(String(200), nullable=False)
    file_url = Column(String(500), nullable=False)
    category = Column(String(100), nullable=True)

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    staff = relationship("StaffProfile")
