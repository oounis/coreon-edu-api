from typing import Dict, Any, Optional

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role
from app.services.transport.transport_service import TransportService

router = APIRouter(prefix="/transport", tags=["Transport"])


# ----------------------
# Buses
# ----------------------
@router.post("/buses")
def create_bus(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.TRANSPORT, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = TransportService(db)
    return svc.create_bus(
        school_id=user.school_id,
        name=payload["name"],
        plate_number=payload["plate_number"],
        capacity=int(payload.get("capacity", 0)) if payload.get("capacity") is not None else None,
        driver_name=payload.get("driver_name"),
        meta=payload.get("meta") or {},
        created_by=user.id,
    )


@router.get("/buses")
def list_buses(
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TRANSPORT, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN, Role.TEACHER
    )),
):
    svc = TransportService(db)
    return svc.list_buses(school_id=user.school_id)


# ----------------------
# Routes
# ----------------------
@router.post("/routes")
def create_route(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.TRANSPORT, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = TransportService(db)
    return svc.create_route(
        school_id=user.school_id,
        name=payload["name"],
        code=payload.get("code", payload["name"]),
        direction=payload.get("direction", "both"),
        meta=payload.get("meta") or {},
        created_by=user.id,
    )


@router.get("/routes")
def list_routes(
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TRANSPORT, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN, Role.TEACHER
    )),
):
    svc = TransportService(db)
    return svc.list_routes(school_id=user.school_id)


# ----------------------
# Stops
# ----------------------
@router.post("/routes/{route_id}/stops")
def add_stop(
    route_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.TRANSPORT, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = TransportService(db)

    latitude = float(payload["latitude"]) if payload.get("latitude") is not None else None
    longitude = float(payload["longitude"]) if payload.get("longitude") is not None else None

    return svc.add_stop(
        school_id=user.school_id,
        route_id=route_id,
        name=payload["name"],
        latitude=latitude,
        longitude=longitude,
        sequence=int(payload.get("sequence", 0)),
        meta=payload.get("meta") or {},
        created_by=user.id,
    )


@router.get("/routes/{route_id}/stops")
def list_stops(
    route_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TRANSPORT, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN, Role.TEACHER
    )),
):
    svc = TransportService(db)
    return svc.list_stops(
        school_id=user.school_id,
        route_id=route_id,
    )


# ----------------------
# Assignments
# ----------------------
@router.post("/assignments")
def assign_student(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TRANSPORT, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN
    )),
):
    svc = TransportService(db)

    effective_from_raw = payload.get("effective_from")
    effective_from = (
        datetime.fromisoformat(effective_from_raw)
        if effective_from_raw
        else None
    )

    return svc.assign_student(
        school_id=user.school_id,
        student_id=int(payload["student_id"]),
        route_id=int(payload["route_id"]),
        stop_id=int(payload["stop_id"]),
        direction=payload.get("direction", "both"),
        effective_from=effective_from,
        meta=payload.get("meta") or {},
        created_by=user.id,
    )


@router.get("/assignments")
def list_assignments(
    student_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TRANSPORT, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN, Role.TEACHER
    )),
):
    svc = TransportService(db)
    return svc.list_assignments(
        school_id=user.school_id,
        student_id=student_id,
    )


@router.get("/students/{student_id}/assignments")
def list_student_assignments(
    student_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TRANSPORT,
        Role.SCHOOL_ADMIN,
        Role.SUPER_ADMIN,
        Role.TEACHER,
        Role.PARENT,
    )),
):
    svc = TransportService(db)
    return svc.list_assignments(
        school_id=user.school_id,
        student_id=student_id,
    )


# ----------------------
# Trip scans (check-in / check-out)
# ----------------------
@router.post("/trips/check-in")
def check_in(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TRANSPORT, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN
    )),
):
    svc = TransportService(db)

    scanned_at_raw = payload.get("scanned_at")
    scanned_at = (
        datetime.fromisoformat(scanned_at_raw)
        if scanned_at_raw
        else None
    )

    return svc.check_in(
        school_id=user.school_id,
        student_id=int(payload["student_id"]),
        route_id=payload.get("route_id"),
        stop_id=payload.get("stop_id"),
        bus_id=payload.get("bus_id"),
        direction=payload.get("direction", "pickup"),
        scanned_at=scanned_at,
        meta=payload.get("meta") or {},
        created_by=user.id,
    )


@router.post("/trips/check-out")
def check_out(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TRANSPORT, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN
    )),
):
    svc = TransportService(db)

    scanned_at_raw = payload.get("scanned_at")
    scanned_at = (
        datetime.fromisoformat(scanned_at_raw)
        if scanned_at_raw
        else None
    )

    return svc.check_out(
        school_id=user.school_id,
        student_id=int(payload["student_id"]),
        route_id=payload.get("route_id"),
        stop_id=payload.get("stop_id"),
        bus_id=payload.get("bus_id"),
        direction=payload.get("direction", "dropoff"),
        scanned_at=scanned_at,
        meta=payload.get("meta") or {},
        created_by=user.id,
    )
