from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    JSON,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class AuditLog(Base):
    """
    Full audit logging.

    Captures:
    - who did the action
    - which school
    - which entity/table
    - what changed (before/after)
    - IP address
    """

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    action = Column(String(200), nullable=False)
    entity = Column(String(200), nullable=False)
    entity_id = Column(String(100), nullable=True)

    before = Column(JSON, nullable=True)
    after = Column(JSON, nullable=True)

    ip_address = Column(String(200), nullable=True)
    user_agent = Column(String(500), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
