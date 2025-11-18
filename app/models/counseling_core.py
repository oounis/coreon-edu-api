from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    ForeignKey,
    Boolean,
    JSON,
    func,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class CounselingSession(Base):
    """
    1-to-1 session with a counselor or psychologist.
    """

    __tablename__ = "counseling_sessions"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    counselor_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    topic = Column(String(500), nullable=True)
    notes = Column(String(2000), nullable=True)

    session_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    student = relationship("StudentProfile")
    counselor = relationship("User")


class BehaviorNote(Base):
    """
    Teacher or counselor behavior note.
    """

    __tablename__ = "behavior_notes"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    staff_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    category = Column(String(100), nullable=True)   # positive / negative / neutral
    description = Column(String(2000), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    student = relationship("StudentProfile")
    staff = relationship("User")


class CounselingReferral(Base):
    """
    Referral to counselor/psychologist.
    """

    __tablename__ = "counseling_referrals"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    referred_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    reason = Column(String(2000), nullable=False)
    status = Column(String(100), nullable=False, server_default="pending")  # pending/accepted/rejected

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    student = relationship("StudentProfile")
    referrer = relationship("User")
