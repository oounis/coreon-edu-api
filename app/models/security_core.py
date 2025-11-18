from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Boolean,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class SecurityPost(Base):
    """
    A security post / gate / checkpoint.
    """

    __tablename__ = "security_posts"

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(200), nullable=False)
    location = Column(String(255), nullable=True)
    active = Column(Boolean, nullable=False, server_default="true")

    school = relationship("School")
