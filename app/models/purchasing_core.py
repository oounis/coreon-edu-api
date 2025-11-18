from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    ForeignKey,
    Boolean,
    Numeric,
    JSON,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(200), nullable=False)
    contact_person = Column(String(200), nullable=True)
    phone = Column(String(100), nullable=True)
    email = Column(String(200), nullable=True)

    active = Column(Boolean, nullable=False, server_default="true")

    school = relationship("School")


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=True)


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    supplier_id = Column(
        Integer,
        ForeignKey("suppliers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    status = Column(
        String(50),
        nullable=False,
        server_default="pending",
    )  # pending/approved/rejected/ordered/received

    total_amount = Column(Numeric(10,2), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    supplier = relationship("Supplier")
    creator = relationship("User")
    items = relationship("PurchaseOrderItem", back_populates="order", cascade="all, delete-orphan")


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer,
        ForeignKey("purchase_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    item_id = Column(
        Integer,
        ForeignKey("purchase_items.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    qty = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10,2), nullable=True)

    order = relationship("PurchaseOrder", back_populates="items")
    item = relationship("PurchaseItem")


class PurchaseRequest(Base):
    """
    A staff member can request items before a purchase order is created.
    """

    __tablename__ = "purchase_requests"

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    requested_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    department_id = Column(
        Integer,
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    items = Column(JSON, nullable=True)  # [{"item": "paper", "qty": 10}, ...]

    status = Column(
        String(50),
        nullable=False,
        server_default="pending",
    )  # pending/approved/rejected

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    requester = relationship("User")
    department = relationship("Department")
