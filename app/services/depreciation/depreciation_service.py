from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import (
    FacilityAsset,
    DepreciationRecord,
)


class DepreciationService:
    """
    Asset Depreciation:
    - Straight-line depreciation
    - Record monthly depreciation
    """

    def __init__(self, db: Session):
        self.db = db

    def calculate_monthly(self, cost: Decimal, useful_life_years: int):
        months = useful_life_years * 12
        return cost / months

    def run_for_asset(self, *, school_id: int, asset_id: int,
                      useful_life_years: int, created_by: int):
        asset = self.db.query(FacilityAsset).filter(
            FacilityAsset.id == asset_id,
            FacilityAsset.school_id == school_id,
        ).first()

        monthly = self.calculate_monthly(asset.cost, useful_life_years)

        record = DepreciationRecord(
            school_id=school_id,
            asset_id=asset_id,
            amount=monthly,
            method="straight_line",
            created_at=datetime.utcnow(),
            created_by=created_by,
        )

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return {"depreciation": record}

    def list(self, *, school_id: int, asset_id: int):
        items = self.db.query(DepreciationRecord).filter(
            DepreciationRecord.school_id == school_id,
            DepreciationRecord.asset_id == asset_id,
        ).all()
        return {"records": items}
