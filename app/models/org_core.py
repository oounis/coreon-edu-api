from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    JSON,
    func,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class OrganizationType(Base):
    __tablename__ = "organization_types"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)


class ProductModule(Base):
    __tablename__ = "product_modules"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    description = Column(String(500), nullable=True)
    is_core = Column(Boolean, nullable=False, server_default="false")

    school_modules = relationship(
        "SchoolModule",
        back_populates="module",
        cascade="all, delete-orphan",
    )


class SchoolModule(Base):
    __tablename__ = "school_modules"
    __table_args__ = (
        UniqueConstraint("school_id", "module_id", name="uq_school_module"),
    )

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    module_id = Column(
        Integer,
        ForeignKey("product_modules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    enabled = Column(Boolean, nullable=False, server_default="true")
    config = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    school = relationship("School", back_populates="modules")
    module = relationship("ProductModule", back_populates="school_modules")


class DepartmentType(Base):
    __tablename__ = "department_types"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)

    departments = relationship(
        "Department",
        back_populates="department_type",
        cascade="all, delete-orphan",
    )


class Department(Base):
    __tablename__ = "departments"
    __table_args__ = (
        UniqueConstraint("school_id", "name", name="uq_department_school_name"),
    )

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    department_type_id = Column(
        Integer,
        ForeignKey("department_types.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    name = Column(String(150), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default="true")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    school = relationship("School", back_populates="departments")
    department_type = relationship("DepartmentType", back_populates="departments")
