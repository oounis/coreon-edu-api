from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import (
    FacilityAsset,
    FacilityRoom,
    FacilityMaintenance,
)
from app.services.workflow.workflow_service import WorkflowService
from app.services.notification_service import NotificationService


class FacilitiesService:
    """
    Facilities management:
    - Assets (IT, classroom equipment, furniture, etc.)
    - Rooms (classrooms, labs, halls...)
    - Maintenance tickets (workflow-enabled)
    """

    def __init__(self, db: Session):
        self.db = db
        self.workflow = WorkflowService(db)
        self.notifications = NotificationService(db)

    # ---------------------------
    # Rooms
    # ---------------------------
    def create_room(self, *, school_id: int, name: str, building: str, floor: int, meta: Dict[str, Any], created_by: int):
        room = FacilityRoom(
            school_id=school_id,
            name=name,
            building=building,
            floor=floor,
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(room)
        self.db.commit()
        self.db.refresh(room)
        return {"room": room}

    def list_rooms(self, *, school_id: int):
        rooms = (
            self.db.query(FacilityRoom)
            .filter(FacilityRoom.school_id == school_id)
            .all()
        )
        return {"rooms": rooms}

    # ---------------------------
    # Assets
    # ---------------------------
    def create_asset(
        self,
        *,
        school_id: int,
        title: str,
        category: str,
        purchase_date: Optional[datetime],
        cost: Optional[Decimal],
        assigned_room_id: Optional[int],
        status: str,
        meta: Optional[Dict[str, Any]],
        created_by: int,
    ):
        asset = FacilityAsset(
            school_id=school_id,
            title=title,
            category=category,
            purchase_date=purchase_date,
            cost=cost,
            assigned_room_id=assigned_room_id,
            status=status,
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return {"asset": asset}

    def list_assets(self, *, school_id: int):
        assets = (
            self.db.query(FacilityAsset)
            .filter(FacilityAsset.school_id == school_id)
            .all()
        )
        return {"assets": assets}

    # ---------------------------
    # Maintenance Tickets (Workflow + Notifications)
    # ---------------------------
    def create_maintenance_request(
        self,
        *,
        school_id: int,
        asset_id: Optional[int],
        room_id: Optional[int],
        title: str,
        description: str,
        priority: str,
        created_by: int,
        meta: Optional[Dict[str, Any]] = None,
    ):
        data = {
            "flow": "maintenance",
            "type": "maintenance_request",
            "asset_id": asset_id,
            "room_id": room_id,
            "title": title,
            "description": description,
            "priority": priority,
            "created_by": created_by,
        }

        req = self.workflow.submit_request(
            user_id=created_by,
            school_id=school_id,
            data=data,
        )

        maint = FacilityMaintenance(
            school_id=school_id,
            workflow_request_id=req.id,
            asset_id=asset_id,
            room_id=room_id,
            title=title,
            description=description,
            priority=priority,
            status="pending",
            meta=meta or {},
            created_by=created_by,
        )

        self.db.add(maint)
        self.db.commit()
        self.db.refresh(maint)

        try:
            self.notifications.create(
                user_id=created_by,
                school_id=school_id,
                key="maintenance_created",
                type="maintenance",
                category="facilities",
                data={"maintenance_id": maint.id},
                priority="high",
            )
        except Exception:
            pass

        return {"maintenance": maint, "workflow_request": req}

    def list_maintenance(self, *, school_id: int):
        items = (
            self.db.query(FacilityMaintenance)
            .filter(FacilityMaintenance.school_id == school_id)
            .all()
        )
        return {"maintenance": items}
