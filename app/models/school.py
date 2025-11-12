from sqlalchemy import Column, Integer, String, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.session import Base

# --- Link table: many-to-many Parent<->Student ---
parent_student = Table(
    "parent_student",
    Base.metadata,
    Column("parent_id", ForeignKey("parents.id"), primary_key=True),
    Column("student_id", ForeignKey("students.id"), primary_key=True),
    UniqueConstraint("parent_id", "student_id", name="uq_parent_student")
)

class School(Base):
    __tablename__ = "schools"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

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
    students = relationship("Student", back_populates="classroom")
    teachers = relationship("Teacher", back_populates="classroom")

    __table_args__ = (UniqueConstraint("grade_id", "name", name="uq_class_per_grade"),)

class Teacher(Base):
    __tablename__ = "teachers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    classroom_id: Mapped[int | None] = mapped_column(ForeignKey("classrooms.id"), nullable=True)

    classroom = relationship("Classroom", back_populates="teachers")

class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    classroom_id: Mapped[int] = mapped_column(ForeignKey("classrooms.id"), index=True)

    classroom = relationship("Classroom", back_populates="students")
    parents = relationship("Parent", secondary=parent_student, back_populates="students")

class Parent(Base):
    __tablename__ = "parents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)

    students = relationship("Student", secondary=parent_student, back_populates="parents")
