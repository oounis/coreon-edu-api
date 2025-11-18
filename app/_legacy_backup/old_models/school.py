from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
    Boolean,
    Date,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.session import Base


# ======================
# Core entities
# ======================

class School(Base):
    __tablename__ = "schools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    grades = relationship("Grade", back_populates="school", cascade="all,delete-orphan")


class Grade(Base):
    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), index=True)

    school = relationship("School", back_populates="grades")
    classrooms = relationship("Classroom", back_populates="grade", cascade="all,delete-orphan")

    __table_args__ = (UniqueConstraint("school_id", "name", name="uq_grade_per_school"),)


class Classroom(Base):
    __tablename__ = "classrooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    grade_id: Mapped[int] = mapped_column(ForeignKey("grades.id"), index=True)

    grade = relationship("Grade", back_populates="classrooms")
    teachers = relationship("Teacher", back_populates="classroom")
    students = relationship("Student", back_populates="classroom")


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # NEW FIELDS YOU MUST ADD:
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    classroom_id: Mapped[Optional[int]] = mapped_column(ForeignKey("classrooms.id"), nullable=True)
    classroom = relationship("Classroom", back_populates="teachers")



class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    classroom_id: Mapped[Optional[int]] = mapped_column(ForeignKey("classrooms.id"), nullable=True)

    # Enterprise fields
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    birthdate: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    national_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    admission_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    profile_photo_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    classroom = relationship("Classroom", back_populates="students")
	

# ======================================
# Departments & Staff Members (Enterprise)
# ======================================

class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), index=True)

    # e.g. "transport", "medical", "external_relations", "vendors"
    code: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Later we can add: type, description, etc.
    # relationships (optional, can be added later):
    # staff_members = relationship("StaffMember", back_populates="department")


class StaffMember(Base):
    __tablename__ = "staff_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), index=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), index=True)

    # e.g. "transport_manager", "nurse", "finance_officer"
    role_code: Mapped[str] = mapped_column(String, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # We can add relationships later if needed:
    # user = relationship("User")
    # school = relationship("School")
    # department = relationship("Department", back_populates="staff_members")

