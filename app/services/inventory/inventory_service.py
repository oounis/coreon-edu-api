from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import (
    InventoryItem,
    InventoryTransaction,
)
from app.services.notification_service import NotificationService


class InventoryService:
    """
    Inventory & Stock Control:
    - Items
    - Adjustments
    - Stock in/out
    - Threshold alert notifications
    """

    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationService(db)

    def create_item(self, *, school_id: int, name: str, category: str,
                    qty: Decimal, threshold: Decimal, meta: Dict[str, Any],
                    created_by: int):
        item = InventoryItem(
            school_id=school_id,
            name=name,
            category=category,
            qty=qty,
            threshold=threshold,
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return {"item": item}

    def list_items(self, *, school_id: int):
        items = self.db.query(InventoryItem).filter(
            InventoryItem.school_id == school_id
        ).all()
        return {"items": items}

    def stock_in(self, *, school_id: int, item_id: int, qty: Decimal,
                 created_by: int, meta: Dict[str, Any]):
        item = self.db.query(InventoryItem).filter(
            InventoryItem.id == item_id,
            InventoryItem.school_id == school_id,
        ).first()
        item.qty += qty

        txn = InventoryTransaction(
            school_id=school_id,
            item_id=item_id,
            qty=qty,
            direction="in",
            created_by=created_by,
            meta=meta or {},
        )

        self.db.add(txn)
        self.db.commit()
        return {"transaction": txn, "item": item}

    def stock_out(self, *, school_id: int, item_id: int, qty: Decimal,
                  created_by: int, meta: Dict[str, Any]):
        item = self.db.query(InventoryItem).filter(
            InventoryItem.id == item_id,
            InventoryItem.school_id == school_id,
        ).first()
        item.qty -= qty

        txn = InventoryTransaction(
            school_id=school_id,
            item_id=item_id,
            qty=qty,
            direction="out",
            created_by=created_by,
            meta=meta or {},
        )
        self.db.add(txn)

        if item.qty < item.threshold:
            try:
                self.notifications.create(
                    user_id=created_by,
                    school_id=school_id,
                    key="inventory_low",
                    type="inventory",
                    category="alert",
                    data={"item": item.name, "qty": str(item.qty)},
                    priority="high",
                )
            except Exception:
                pass

        self.db.commit()
        return {"transaction": txn, "item": item}
