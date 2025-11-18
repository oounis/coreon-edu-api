from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import (
    # NOTE: تأكد من أسماء الموديلات في models.py وعدّلها إذا يلزم
    Student,
    TransportBus,
    TransportRoute,
    TransportStop,
    TransportAssignment,
    TransportTripScan,
)
from app.services.notification_service import NotificationService


class TransportService:
    """
    Transport management:
    - Buses
    - Routes & stops
    - Student assignments
    - Daily check-in / check-out (scans) + notifications
    """

    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationService(db)

    # ---------------------------
    # Buses
    # ---------------------------
    def create_bus(
        self,
        *,
        school_id: int,
        name: str,
        plate_number: str,
        capacity: Optional[int],
        driver_name: Optional[str],
        meta: Optional[Dict[str, Any]],
        created_by: int,
    ) -> Dict[str, Any]:
        bus = TransportBus(
            school_id=school_id,
            name=name,
            plate_number=plate_number,
            capacity=capacity,
            driver_name=driver_name,
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(bus)
        self.db.commit()
        self.db.refresh(bus)
        return {"bus": bus}

    def list_buses(self, *, school_id: int) -> Dict[str, Any]:
        buses = (
            self.db.query(TransportBus)
            .filter(TransportBus.school_id == school_id)
            .all()
        )
        return {"buses": buses}

    # ---------------------------
    # Routes
    # ---------------------------
    def create_route(
        self,
        *,
        school_id: int,
        name: str,
        code: str,
        direction: str,
        meta: Optional[Dict[str, Any]],
        created_by: int,
    ) -> Dict[str, Any]:
        route = TransportRoute(
            school_id=school_id,
            name=name,
            code=code,
            direction=direction,  # "pickup" | "dropoff" | "both"
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(route)
        self.db.commit()
        self.db.refresh(route)
        return {"route": route}

    def list_routes(self, *, school_id: int) -> Dict[str, Any]:
        routes = (
            self.db.query(TransportRoute)
            .filter(TransportRoute.school_id == school_id)
            .all()
        )
        return {"routes": routes}

    # ---------------------------
    # Stops
    # ---------------------------
    def add_stop(
        self,
        *,
        school_id: int,
        route_id: int,
        name: str,
        latitude: Optional[float],
        longitude: Optional[float],
        sequence: int,
        meta: Optional[Dict[str, Any]],
        created_by: int,
    ) -> Dict[str, Any]:
        stop = TransportStop(
            school_id=school_id,
            route_id=route_id,
            name=name,
            latitude=latitude,
            longitude=longitude,
            sequence=sequence,
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(stop)
        self.db.commit()
        self.db.refresh(stop)
        return {"stop": stop}

    def list_stops(self, *, school_id: int, route_id: int) -> Dict[str, Any]:
        stops = (
            self.db.query(TransportStop)
            .filter(TransportStop.school_id == school_id)
            .filter(TransportStop.route_id == route_id)
            .order_by(TransportStop.sequence.asc())
            .all()
        )
        return {"stops": stops}

    # ---------------------------
    # Student assignments
    # ---------------------------
    def assign_student(
        self,
        *,
        school_id: int,
        student_id: int,
        route_id: int,
        stop_id: int,
        direction: str,
        effective_from: Optional[datetime],
        meta: Optional[Dict[str, Any]],
        created_by: int,
    ) -> Dict[str, Any]:
        # basic student check
        student = (
            self.db.query(Student)
            .filter(Student.id == student_id)
            .filter(Student.school_id == school_id)
            .first()
        )
        if not student:
            raise ValueError("Student not found in this school")

        assignment = TransportAssignment(
            school_id=school_id,
            student_id=student_id,
            route_id=route_id,
            stop_id=stop_id,
            direction=direction,  # "pickup" | "dropoff" | "both"
            status="active",
            effective_from=effective_from or datetime.utcnow(),
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)

        return {"assignment": assignment}

    def list_assignments(
        self,
        *,
        school_id: int,
        student_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        q = (
            self.db.query(TransportAssignment)
            .filter(TransportAssignment.school_id == school_id)
        )
        if student_id:
            q = q.filter(TransportAssignment.student_id == student_id)

        assignments = q.all()
        return {"assignments": assignments}

    # ---------------------------
    # Trip scans (check-in / check-out)
    # ---------------------------
    def _record_scan(
        self,
        *,
        school_id: int,
        student_id: int,
        route_id: Optional[int],
        stop_id: Optional[int],
        bus_id: Optional[int],
        direction: str,
        scan_type: str,  # "check_in" | "check_out"
        scanned_at: Optional[datetime],
        meta: Optional[Dict[str, Any]],
        created_by: int,
    ) -> Dict[str, Any]:
        scan = TransportTripScan(
            school_id=school_id,
            student_id=student_id,
            route_id=route_id,
            stop_id=stop_id,
            bus_id=bus_id,
            direction=direction,
            scan_type=scan_type,
            scanned_at=scanned_at or datetime.utcnow(),
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(scan)
        self.db.commit()
        self.db.refresh(scan)

        key = "transport_check_in" if scan_type == "check_in" else "transport_check_out"

        try:
            self.notifications.create(
                user_id=created_by,
                school_id=school_id,
                key=key,
                type="transport",
                category="transport_trips",
                data={
                    "scan_id": scan.id,
                    "student_id": student_id,
                    "direction": direction,
                    "scan_type": scan_type,
                },
                priority="normal",
            )
        except Exception:
            # notifications must not break transport flow
            pass

        return {"scan": scan}

    def check_in(
        self,
        *,
        school_id: int,
        student_id: int,
        route_id: Optional[int],
        stop_id: Optional[int],
        bus_id: Optional[int],
        direction: str,
        scanned_at: Optional[datetime],
        meta: Optional[Dict[str, Any]],
        created_by: int,
    ) -> Dict[str, Any]:
        return self._record_scan(
            school_id=school_id,
            student_id=student_id,
            route_id=route_id,
            stop_id=stop_id,
            bus_id=bus_id,
            direction=direction,
            scan_type="check_in",
            scanned_at=scanned_at,
            meta=meta,
            created_by=created_by,
        )

    def check_out(
        self,
        *,
        school_id: int,
        student_id: int,
        route_id: Optional[int],
        stop_id: Optional[int],
        bus_id: Optional[int],
        direction: str,
        scanned_at: Optional[datetime],
        meta: Optional[Dict[str, Any]],
        created_by: int,
    ) -> Dict[str, Any]:
        return self._record_scan(
            school_id=school_id,
            student_id=student_id,
            route_id=route_id,
            stop_id=stop_id,
            bus_id=bus_id,
            direction=direction,
            scan_type="check_out",
            scanned_at=scanned_at,
            meta=meta,
            created_by=created_by,
        )
