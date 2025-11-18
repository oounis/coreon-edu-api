from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    ForeignKey,
    Boolean,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class ActivityClub(Base):
    """
    Clubs like:
    - Football
    - Chess
    - Robotics
    - Music
    """

    __tablename__ = "activity_clubs"
    __table_args__ = (
        UniqueConstraint("school_id", "name", name="uq_club_name"),
    )

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(200), nullable=False)
    description = Column(String(2000), nullable=True)

    active = Column(Boolean, nullable=False, server_default="true")

    school = relationship("School")
    enrollments = relationship("ClubEnrollment", back_populates="club", cascade="all, delete-orphan")


class ClubEnrollment(Base):
    """
    Student enrolled in club.
    """

    __tablename__ = "club_enrollments"
    __table_args__ = (
        UniqueConstraint("student_id", "club_id", name="uq_club_enrollment"),
    )

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    club_id = Column(
        Integer,
        ForeignKey("activity_clubs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    student = relationship("StudentProfile")
    club = relationship("ActivityClub", back_populates="enrollments")


class ActivityEvent(Base):
    """
    Events of clubs:
    - competitions
    - training days
    - field trips
    """

    __tablename__ = "activity_events"

    id = Column(Integer, primary_key=True, index=True)

    club_id = Column(
        Integer,
        ForeignKey("activity_clubs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(String(200), nullable=False)
    description = Column(String(2000), nullable=True)
    date = Column(DateTime(timezone=True), nullable=False)

    club = relationship("ActivityClub")


class Achievement(Base):
    """
    Student achievements:
    - Medal
    - Trophy
    - Recognition
    """

    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title = Column(String(200), nullable=False)
    description = Column(String(2000), nullable=True)
    date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    student = relationship("StudentProfile")
