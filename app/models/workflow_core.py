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


class WorkflowDefinition(Base):
    """
    Defines a workflow for a request type in a school.

    Example:
    request_type = "finance.discount"
    steps:
      1. secretary
      2. finance_officer
      3. director
    """

    __tablename__ = "workflow_definitions"
    __table_args__ = (
        UniqueConstraint("school_id", "request_type", name="uq_workflow_school_type"),
    )

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    request_type = Column(String(200), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    active = Column(Boolean, nullable=False, server_default="true")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    steps = relationship(
        "WorkflowStep",
        back_populates="workflow",
        cascade="all, delete-orphan",
    )


class WorkflowStep(Base):
    """
    Individual steps of a workflow.

    - step_order: 1, 2, 3...
    - approver_role_id: which role approves this step
    """

    __tablename__ = "workflow_steps"
    __table_args__ = (
        UniqueConstraint("workflow_id", "step_order", name="uq_workflow_step_order"),
    )

    id = Column(Integer, primary_key=True, index=True)

    workflow_id = Column(
        Integer,
        ForeignKey("workflow_definitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    step_order = Column(Integer, nullable=False)
    approver_role_id = Column(
        Integer,
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    min_approvals = Column(Integer, nullable=False, server_default="1")
    auto_advance = Column(Boolean, nullable=False, server_default="true")

    workflow = relationship("WorkflowDefinition", back_populates="steps")
    approver_role = relationship("Role")


class Request(Base):
    """
    A workflow instance (a request).

    - request_type: "finance.discount"
    - payload: details about the request
    - current_step: which workflow step it's in
    - status: pending/approved/rejected/cancelled
    """

    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_by_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    request_type = Column(String(200), nullable=False, index=True)
    payload = Column(JSON, nullable=True)

    current_step = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False, server_default="pending")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    approvals = relationship(
        "RequestApproval",
        back_populates="request",
        cascade="all, delete-orphan",
    )


class RequestApproval(Base):
    """
    Approval actions on a request.

    - step_order: which step this approval belongs to
    - approver_id: user performing the action
    - decision: approved/rejected
    """

    __tablename__ = "request_approvals"

    id = Column(Integer, primary_key=True, index=True)

    request_id = Column(
        Integer,
        ForeignKey("requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    step_order = Column(Integer, nullable=False)

    approver_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    decision = Column(String(50), nullable=False)
    comment = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    request = relationship("Request", back_populates="approvals")
