from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class Visitor(Base):
    """
    Person visiting the school (not staff/parent/student).
    """

    __tablename__ = "visitors"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(200), nullable=False)
    id_document = Column(String(200), nullable=True)  # ID / CPR / Passport
    phone = Column(String(100), nullable=True)
    organization = Column(String(200), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    visits = relationship(
        "VisitorVisit",
        back_populates="visitor",
        cascade="all, delete-orphan",
    )


class VisitorVisit(Base):
    """
    Visit log for a visitor.
    """

    __tablename__ = "visitor_visits"

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    visitor_id = Column(
        Integer,
        ForeignKey("visitors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    host_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    purpose = Column(String(500), nullable=True)
    status = Column(
        String(50),
        nullable=False,
        server_default="pending",
    )  # pending / in / out / cancelled

    check_in_time = Column(DateTime(timezone=True), nullable=True)
    check_out_time = Column(DateTime(timezone=True), nullable=True)

    created_by_guard_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    visitor = relationship("Visitor", back_populates="visits")
    school = relationship("School")
    host_user = relationship("User", foreign_keys=[host_user_id])
    created_by_guard = relationship("User", foreign_keys=[created_by_guard_id])
