from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.session import Base


class Parent(Base):
    __tablename__ = "parents"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(50), nullable=True)

    is_active = Column(Boolean, nullable=False, default=True)

    # link rows ParentStudent
    links = relationship(
        "ParentStudent",
        back_populates="parent",
        cascade="all, delete-orphan",
    )


class ParentStudent(Base):
    """
    Many-to-many link between parents and students.
    One parent can have many students (children).
    One student can have many parents/guardians.
    """

    __tablename__ = "parent_students"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)

    relationship_type = Column(String(50), nullable=True)  # e.g. "father", "mother", "guardian"
    is_primary = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        UniqueConstraint("parent_id", "student_id", name="uq_parent_students_parent_id_student_id"),
    )

    parent = relationship("Parent", back_populates="links")
    # Student model will be extended later to have `parents` backref
    student = relationship("Student", backref="parent_links")
