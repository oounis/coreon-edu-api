from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class GateAccessLog(Base):
    """
    Gate access for people (students, staff, visitors, drivers).
    """

    __tablename__ = "gate_access_logs"

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    security_post_id = Column(
        Integer,
        ForeignKey("security_posts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    direction = Column(String(10), nullable=False)  # in / out
    person_type = Column(
        String(50),
        nullable=False,
    )  # student / staff / visitor / vendor / driver

    student_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    staff_id = Column(
        Integer,
        ForeignKey("staff_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    visitor_id = Column(
        Integer,
        ForeignKey("visitors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    vehicle_id = Column(
        Integer,
        ForeignKey("vehicle_accesses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    guard_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    school = relationship("School")
    post = relationship("SecurityPost")
    student = relationship("StudentProfile")
    staff = relationship("StaffProfile")
    visitor = relationship("Visitor")
    vehicle = relationship("VehicleAccess")
    guard = relationship("User")
