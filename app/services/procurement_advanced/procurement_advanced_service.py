from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Vendor, RFQ, Quotation


class ProcurementAdvancedService:
    """
    Procurement Advanced:
    - Vendors
    - RFQ (Request for Quotations)
    - Vendor quotations
    """

    def __init__(self, db: Session):
        self.db = db

    def create_vendor(self, *, school_id: int, name: str, contact: Dict[str, Any], created_by: int):
        v = Vendor(
            school_id=school_id,
            name=name,
            contact=contact,
            created_by=created_by,
        )
        self.db.add(v)
        self.db.commit()
        self.db.refresh(v)
        return {"vendor": v}

    def create_rfq(self, *, school_id: int, title: str, description: str, meta: Dict[str, Any], created_by: int):
        r = RFQ(
            school_id=school_id,
            title=title,
            description=description,
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(r)
        self.db.commit()
        self.db.refresh(r)
        return {"rfq": r}

    def submit_quotation(self, *, school_id: int, rfq_id: int, vendor_id: int, amount: float, meta: Dict[str, Any], created_by: int):
        q = Quotation(
            school_id=school_id,
            rfq_id=rfq_id,
            vendor_id=vendor_id,
            amount=amount,
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(q)
        self.db.commit()
        self.db.refresh(q)
        return {"quotation": q}
