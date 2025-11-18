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


class GuardShift(Base):
    """
    Guard shifts per security post.
    """

    __tablename__ = "guard_shifts"

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    guard_id = Column(
        Integer,
        ForeignKey("staff_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    security_post_id = Column(
        Integer,
        ForeignKey("security_posts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)

    notes = Column(String(2000), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    school = relationship("School")
    guard = relationship("StaffProfile")
    post = relationship("SecurityPost")
