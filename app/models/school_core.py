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


class School(Base):
    """
    Central tenant entity.

    A school can be:
    - nursery_only
    - k12 school
    - school_with_nursery
    """

    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, nullable=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)

    organization_type_id = Column(
        Integer,
        ForeignKey("organization_types.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    is_active = Column(Boolean, nullable=False, server_default="true")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relations
    organization_type = relationship("OrganizationType")

    modules = relationship(
        "SchoolModule",
        back_populates="school",
        cascade="all, delete-orphan",
    )

    departments = relationship(
        "Department",
        back_populates="school",
        cascade="all, delete-orphan",
    )

    # Future expansions
    # campuses = relationship("Campus", back_populates="school")
    # academic_years = relationship("AcademicYear", back_populates="school")
