from typing import Dict, Any, Optional
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role
from app.services.facilities.facilities_service import FacilitiesService

router = APIRouter(prefix="/facilities", tags=["Facilities"])


# ----------------------
# Rooms
# ----------------------
@router.post("/rooms")
def create_room(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = FacilitiesService(db)
    return svc.create_room(
        school_id=user.school_id,
        name=payload["name"],
        building=payload.get("building", "Main"),
        floor=int(payload.get("floor", 0)),
        meta=payload.get("meta") or {},
        created_by=user.id,
    )


@router.get("/rooms")
def list_rooms(
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.SCHOOL_ADMIN, Role.SUPER_ADMIN, Role.TEACHER)),
):
    svc = FacilitiesService(db)
    return svc.list_rooms(school_id=user.school_id)


# ----------------------
# Assets
# ----------------------
@router.post("/assets")
def create_asset(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = FacilitiesService(db)

    purchase_date = (
        datetime.fromisoformat(payload["purchase_date"])
        if payload.get("purchase_date")
        else None
    )

    cost = Decimal(str(payload["cost"])) if payload.get("cost") else None

    return svc.create_asset(
        school_id=user.school_id,
        title=payload["title"],
        category=payload["category"],
        purchase_date=purchase_date,
        cost=cost,
        assigned_room_id=payload.get("assigned_room_id"),
        status=payload.get("status", "available"),
        meta=payload.get("meta") or {},
        created_by=user.id,
    )


@router.get("/assets")
def list_assets(
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.SCHOOL_ADMIN, Role.SUPER_ADMIN, Role.TEACHER
    )),
):
    svc = FacilitiesService(db)
    return svc.list_assets(school_id=user.school_id)


# ----------------------
# Maintenance
# ----------------------
@router.post("/maintenance")
def create_maintenance(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(
        require_roles(Role.SCHOOL_ADMIN, Role.SUPERVISOR, Role.SUPER_ADMIN, Role.HR)
    ),
):
    svc = FacilitiesService(db)
    return svc.create_maintenance_request(
        school_id=user.school_id,
        asset_id=payload.get("asset_id"),
        room_id=payload.get("room_id"),
        title=payload["title"],
        description=payload.get("description", ""),
        priority=payload.get("priority", "normal"),
        created_by=user.id,
        meta=payload.get("meta") or {},
    )


@router.get("/maintenance")
def list_maintenance(
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.SCHOOL_ADMIN, Role.SUPER_ADMIN, Role.SUPERVISOR, Role.HR
    )),
):
    svc = FacilitiesService(db)
    return svc.list_maintenance(school_id=user.school_id)
