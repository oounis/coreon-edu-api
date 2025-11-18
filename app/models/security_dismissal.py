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


class StudentDismissalLog(Base):
    """
    Track student dismissal / early pickup.
    """

    __tablename__ = "student_dismissal_logs"

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    student_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    parent_id = Column(
        Integer,
        ForeignKey("parent_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    parent_name = Column(String(200), nullable=True)
    relation_to_student = Column(String(100), nullable=True)  # father / mother / guardian / driver / other

    reason = Column(String(1000), nullable=True)
    dismissal_type = Column(
        String(50),
        nullable=False,
        server_default="early",
    )  # early / normal / emergency

    requested_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    dismissal_time = Column(DateTime(timezone=True), nullable=True)

    verified_by_guard_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    school = relationship("School")
    student = relationship("StudentProfile")
    parent = relationship("ParentProfile")
    verified_by_guard = relationship("User")
