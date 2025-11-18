from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Boolean,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class AcademicYear(Base):
    """
    Example: 2024-2025
    """

    __tablename__ = "academic_years"
    __table_args__ = (
        UniqueConstraint("school_id", "name", name="uq_academic_year_school_name"),
    )

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(50), nullable=False)   # "2024-2025"
    is_active = Column(Boolean, nullable=False, server_default="false")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    school = relationship("School")


class EducationalStage(Base):
    """
    Examples:
    - nursery
    - kindergarten
    - primary
    - middle
    - high
    """

    __tablename__ = "educational_stages"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)


class Grade(Base):
    """
    A grade belongs to a school + stage.
    """

    __tablename__ = "grades"
    __table_args__ = (
        UniqueConstraint("school_id", "name", name="uq_grade_school_name"),
    )

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    stage_id = Column(
        Integer,
        ForeignKey("educational_stages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    name = Column(String(100), nullable=False)

    school = relationship("School")
    stage = relationship("EducationalStage")

    classrooms = relationship(
        "Classroom",
        back_populates="grade",
        cascade="all, delete-orphan",
    )


class Classroom(Base):
    """
    Classroom within a grade.
    """

    __tablename__ = "classrooms"
    __table_args__ = (
        UniqueConstraint("grade_id", "name", name="uq_classroom_grade_name"),
    )

    id = Column(Integer, primary_key=True, index=True)

    grade_id = Column(
        Integer,
        ForeignKey("grades.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(100), nullable=False)
    capacity = Column(Integer, nullable=True)

    grade = relationship("Grade", back_populates="classrooms")


class StudentParent(Base):
    """
    Many-to-many: Student ↔ Parent
    """

    __tablename__ = "student_parents"
    __table_args__ = (
        UniqueConstraint("student_id", "parent_id", name="uq_student_parent"),
    )

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    parent_id = Column(
        Integer,
        ForeignKey("parent_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
