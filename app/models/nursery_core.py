from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    ForeignKey,
    String,
    JSON,
    func,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class NurseryDailyReport(Base):
    """
    Daily report for nursery students:
    - meals
    - naps
    - diapers
    - mood
    - activities
    """

    __tablename__ = "nursery_daily_reports"

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

    date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    meals = Column(JSON, nullable=True)        # breakfast/lunch/snacks
    naps = Column(JSON, nullable=True)         # nap times
    diapers = Column(JSON, nullable=True)      # diaper changes
    mood = Column(String(100), nullable=True)  # happy/sleepy/etc
    notes = Column(String(1000), nullable=True)

    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    student = relationship("StudentProfile")
    creator = relationship("User")


class NurseryIncident(Base):
    """
    Incidents in nursery:
    - falls
    - crying episodes
    - bite accident
    - etc
    """

    __tablename__ = "nursery_incidents"

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

    reported_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    description = Column(String(1000), nullable=False)
    severity = Column(String(50), nullable=True)     # low/medium/high
    action_taken = Column(String(1000), nullable=True)

    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    student = relationship("StudentProfile")
    reporter = relationship("User")
