from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class User(Base):
    """
    Core system user (login account).

    NOT a student or parent — those are profiles linked to this table.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    email = Column(String(200), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    password_hash = Column(String(500), nullable=False)

    is_active = Column(Boolean, nullable=False, server_default="true")
    is_superuser = Column(Boolean, nullable=False, server_default="false")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    school = relationship("School")

    roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")

    staff_profile = relationship(
        "StaffProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    parent_profile = relationship(
        "ParentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    student_profile = relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )


class StaffProfile(Base):
    """
    Staff profile linked to a system user.
    """

    __tablename__ = "staff_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    department_id = Column(
        Integer,
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    position = Column(String(200), nullable=True)   # e.g. "Math Teacher", "Finance Officer"

    user = relationship("User", back_populates="staff_profile")
    department = relationship("Department")


class ParentProfile(Base):
    """
    Parent profile linked to user.
    """

    __tablename__ = "parent_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    phone = Column(String(100), nullable=True)

    user = relationship("User", back_populates="parent_profile")


class StudentProfile(Base):
    """
    Student profile.
    """

    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    grade_id = Column(
        Integer,
        ForeignKey("grades.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    classroom_id = Column(
        Integer,
        ForeignKey("classrooms.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    user = relationship("User", back_populates="student_profile")
