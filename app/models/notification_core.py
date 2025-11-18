from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    JSON,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class Notification(Base):
    """
    In-app notification for a user.

    Examples:
    - workflow.approval.pending
    - finance.invoice.issued
    - security.incident.reported
    """

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # High-level grouping: workflow / finance / security / health / transport / nursery / hr / system
    category = Column(String(50), nullable=True)

    # Fine-grained type key, e.g. "workflow.approval.pending"
    type = Column(String(100), nullable=False)

    title = Column(String(255), nullable=False)
    body = Column(String(4000), nullable=True)

    # Optional: link to workflow request or other entity
    request_id = Column(
        Integer,
        ForeignKey("requests.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Extra payload (IDs, URLs, etc.)
    data = Column(JSON, nullable=True)

    priority = Column(
        String(20),
        nullable=False,
        server_default="normal",  # low / normal / high / critical
    )

    is_read = Column(Boolean, nullable=False, server_default="false")
    read_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    school = relationship("School")
    user = relationship("User")
    request = relationship("Request")


class NotificationPreference(Base):
    """
    Per-user channel preferences.

    Example rows:
    - (user, in_app) -> enabled
    - (user, email)  -> enabled
    - (user, sms)    -> disabled
    """

    __tablename__ = "notification_preferences"
    __table_args__ = (
        UniqueConstraint("user_id", "channel", name="uq_notification_pref_user_channel"),
    )

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # in_app / email / sms / push
    channel = Column(String(50), nullable=False)

    enabled = Column(Boolean, nullable=False, server_default="true")

    # Optional minimal priority to send for this channel
    min_priority = Column(String(20), nullable=True)  # e.g. "high" or "critical only"

    # Optional JSON config (language, daily summary, quiet hours, etc.)
    config = Column(JSON, nullable=True)

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

    user = relationship("User")


class NotificationTemplate(Base):
    """
    Reusable templates for notifications.

    Example keys:
    - workflow.approval.pending
    - finance.invoice.issued
    - security.incident.reported
    """

    __tablename__ = "notification_templates"
    __table_args__ = (
        UniqueConstraint("key", "school_id", name="uq_notification_template_key_school"),
    )

    id = Column(Integer, primary_key=True, index=True)

    # NULL = global default template; non-NULL = school override
    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    key = Column(String(150), nullable=False)  # e.g. "workflow.approval.pending"

    # Optional: default channel for this template (in_app / email / sms / push)
    default_channel = Column(String(50), nullable=True)

    title_template = Column(String(255), nullable=False)
    body_template = Column(String(4000), nullable=True)

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

    school = relationship("School")
