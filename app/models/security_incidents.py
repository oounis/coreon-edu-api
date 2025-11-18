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


class SecurityIncident(Base):
    """
    Security or safety incident:
    - fire drill
    - fight
    - theft
    - lost item
    - hazard
    """

    __tablename__ = "security_incidents"

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    type = Column(String(100), nullable=False)      # fire_drill / fight / theft / lost_item / hazard / other
    severity = Column(String(50), nullable=True)   # low / medium / high / critical
    title = Column(String(200), nullable=False)
    description = Column(String(4000), nullable=True)

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

    reported_by_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    occurred_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    status = Column(
        String(50),
        nullable=False,
        server_default="open",
    )  # open / investigating / closed

    school = relationship("School")
    student = relationship("StudentProfile")
    staff = relationship("StaffProfile")
    reported_by = relationship("User")
