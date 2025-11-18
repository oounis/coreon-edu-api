
# ===============================
# Coreon Education school models
# ===============================

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    code = Column(String(50), nullable=True, unique=True, index=True)
    city = Column(String(255), nullable=True)
    country = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)

    grades = relationship("Grade", back_populates="school", cascade="all, delete-orphan")
    classes = relationship("Classroom", back_populates="school", cascade="all, delete-orphan")
    students = relationship("Student", back_populates="school", cascade="all, delete-orphan")
    teachers = relationship("Teacher", back_populates="school", cascade="all, delete-orphan")

class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    level = Column(Integer, nullable=True)
    school_id = Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)

    school = relationship("School", back_populates="grades")
    classes = relationship("Classroom", back_populates="grade", cascade="all, delete-orphan")


class Classroom(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    section = Column(String(50), nullable=True)
    grade_id = Column(Integer, ForeignKey("grades.id", ondelete="CASCADE"), nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    homeroom_teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True)

    grade = relationship("Grade", back_populates="classes")
    school = relationship("School", back_populates="classes")
    homeroom_teacher = relationship("Teacher", back_populates="classes")
    students = relationship("Student", back_populates="classroom", cascade="all, delete-orphan")


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    school_id = Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)

    school = relationship("School", back_populates="teachers")
    classes = relationship("Classroom", back_populates="homeroom_teacher")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    school_id = Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="SET NULL"), nullable=True)
    enrollment_number = Column(String(50), unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True)

    school = relationship("School", back_populates="students")
    classroom = relationship("Classroom", back_populates="students")

class SchoolAdmin(Base):
    __tablename__ = "school_admins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    school_id = Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)

    # Simple relationships (no back_populates needed for now)
    # You can navigate via joins in queries.

# --- Patch: Add missing columns to School model ---
from sqlalchemy import Boolean, String, Column

if not hasattr(School, "city"):
    School.city = Column(String(255), nullable=True)

if not hasattr(School, "country"):
    School.country = Column(String(255), nullable=True)

if not hasattr(School, "is_active"):
    School.is_active = Column(Boolean, default=True)
