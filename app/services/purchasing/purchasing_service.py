from __future__ import annotations
from typing import Dict, Any, List, Optional
from decimal import Decimal

from sqlalchemy.orm import Session

from app.services.workflow.workflow_service import WorkflowService
from app.services.finance.budget_service import BudgetService
from app.services.notification_service import NotificationService

from app.models import (
    Vendor,
    PurchaseRequest,
    PurchaseRequestItem,
    PurchaseOrder,
    PurchaseOrderItem,
)


class PurchasingService:
    """
    Procurement module:
    - Vendors
    - Purchase Requests (PR)
    - Purchase Orders (PO)
    - Quotes (future)
    """

    def __init__(self, db: Session):
        self.db = db
        self.workflow = WorkflowService(db)
        self.budget = BudgetService(db)
        self.notifications = NotificationService(db)

    # ---------------- Vendors ----------------

    def create_vendor(self, *, school_id: int, payload: Dict[str, Any], created_by: int):
        vendor = Vendor(
            school_id=school_id,
            name=payload["name"],
            email=payload.get("email"),
            phone=payload.get("phone"),
            address=payload.get("address"),
            meta=payload.get("meta") or {},
            created_by=created_by,
        )
        self.db.add(vendor)
        self.db.commit()
        self.db.refresh(vendor)
        return vendor

    # ---------------- Purchase Requests (PR) ----------------

    def create_purchase_request(
        self,
        *,
        school_id: int,
        department_id: int,
        items: List[Dict[str, Any]],
        fiscal_year: int,
        created_by: int,
        meta: Optional[Dict[str, Any]] = None,
    ):
        pr = PurchaseRequest(
            school_id=school_id,
            department_id=department_id,
            fiscal_year=fiscal_year,
            status="pending",
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(pr)
        self.db.flush()

        for item in items:
            line = PurchaseRequestItem(
                pr_id=pr.id,
                title=item["title"],
                qty=item.get("qty", 1),
                unit_price=Decimal(str(item.get("unit_price", "0"))),
                category=item.get("category"),
                meta=item.get("meta") or {},
            )
            self.db.add(line)

        # workflow event
        data = {
            "type": "purchase_request",
            "request_id": pr.id,
            "department_id": department_id,
            "fiscal_year": fiscal_year,
        }
        self.workflow.submit_request(
            user_id=created_by,
            school_id=school_id,
            data=data,
        )

        try:
            self.notifications.create(
                user_id=created_by,
                school_id=school_id,
                key="pr_created",
                type="purchasing",
                category="purchase_request",
                data={"pr_id": pr.id},
                priority="normal",
            )
        except:
            pass

        self.db.commit()
        self.db.refresh(pr)
        return pr

    # ---------------- Purchase Orders (PO) ----------------

    def create_purchase_order(
        self,
        *,
        school_id: int,
        vendor_id: int,
        pr_id: int,
        items: List[Dict[str, Any]],
        fiscal_year: int,
        department_id: int,
        created_by: int,
        meta: Optional[Dict[str, Any]] = None,
    ):
        po = PurchaseOrder(
            school_id=school_id,
            vendor_id=vendor_id,
            pr_id=pr_id,
            fiscal_year=fiscal_year,
            department_id=department_id,
            status="pending",
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(po)
        self.db.flush()

        total = Decimal("0")

        for item in items:
            qty = Decimal(str(item.get("qty", "1")))
            price = Decimal(str(item.get("unit_price", "0")))
            line_total = qty * price

            line = PurchaseOrderItem(
                po_id=po.id,
                title=item["title"],
                qty=qty,
                unit_price=price,
                total=line_total,
                category=item.get("category"),
                meta=item.get("meta") or {},
            )
            self.db.add(line)
            total += line_total

        # link PO to budget as EXPENSE
        try:
            self.budget.register_transaction(
                school_id=school_id,
                department_id=department_id,
                fiscal_year=fiscal_year,
                amount=total,
                currency="USD",
                kind="expense",
                method="internal",
                category="procurement",
                reference=f"PO-{po.id}",
                created_by=created_by,
                meta={"po_id": po.id},
            )
        except:
            pass

        self.db.commit()
        self.db.refresh(po)
        return po
