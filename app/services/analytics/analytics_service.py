from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime, date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import (
    Student,
    Attendance,
    Grade,
    EventAttendance,
    TransportTripScan,
    HealthVisit,
)
from app.services.notification_service import NotificationService


class AnalyticsService:
    """
    Enterprise Analytics Engine:
    - Attendance insights
    - Academic performance analytics
    - Transport KPIs
    - Health center statistics
    - Event participation analytics
    - Early warning indicators
    """

    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationService(db)

    # -----------------------------------------------------
    # 1) Attendance summary
    # -----------------------------------------------------
    def attendance_summary(self, school_id: int, date_from: date, date_to: date):
        total = (
            self.db.query(func.count(Attendance.id))
            .filter(Attendance.school_id == school_id)
            .filter(Attendance.date >= date_from)
            .filter(Attendance.date <= date_to)
            .scalar()
        )
        present = (
            self.db.query(func.count(Attendance.id))
            .filter(Attendance.school_id == school_id)
            .filter(Attendance.date >= date_from)
            .filter(Attendance.date <= date_to)
            .filter(Attendance.status == "present")
            .scalar()
        )
        absent = total - present

        return {
            "total_records": total,
            "present": present,
            "absent": absent,
            "attendance_rate": round((present / total) * 100, 2) if total else 0,
        }

    # -----------------------------------------------------
    # 2) Academic performance breakdown
    # -----------------------------------------------------
    def grade_distribution(self, school_id: int):
        q = (
            self.db.query(
                Grade.subject_id,
                func.avg(Grade.score).label("avg_score"),
                func.min(Grade.score).label("min_score"),
                func.max(Grade.score).label("max_score"),
            )
            .filter(Grade.school_id == school_id)
            .group_by(Grade.subject_id)
            .all()
        )

        return {"subjects": [dict(row._mapping) for row in q]}

    # -----------------------------------------------------
    # 3) Transport KPIs
    # -----------------------------------------------------
    def transport_kpis(self, school_id: int, date_from: date, date_to: date):
        total_scans = (
            self.db.query(func.count(TransportTripScan.id))
            .filter(TransportTripScan.school_id == school_id)
            .filter(TransportTripScan.scanned_at >= date_from)
            .filter(TransportTripScan.scanned_at <= date_to)
            .scalar()
        )

        pickup_scans = (
            self.db.query(func.count(TransportTripScan.id))
            .filter(TransportTripScan.school_id == school_id)
            .filter(TransportTripScan.direction == "pickup")
            .scalar()
        )

        dropoff_scans = (
            self.db.query(func.count(TransportTripScan.id))
            .filter(TransportTripScan.school_id == school_id)
            .filter(TransportTripScan.direction == "dropoff")
            .scalar()
        )

        return {
            "total_scans": total_scans,
            "pickup_scans": pickup_scans,
            "dropoff_scans": dropoff_scans,
        }

    # -----------------------------------------------------
    # 4) Health center analytics
    # -----------------------------------------------------
    def health_kpis(self, school_id: int, date_from: date, date_to: date):
        visits = (
            self.db.query(func.count(HealthVisit.id))
            .filter(HealthVisit.school_id == school_id)
            .filter(HealthVisit.visit_time >= date_from)
            .filter(HealthVisit.visit_time <= date_to)
            .scalar()
        )

        return {"total_visits": visits}

    # -----------------------------------------------------
    # 5) Events attendance stats
    # -----------------------------------------------------
    def events_summary(self, school_id: int, event_id: int):
        attendance = (
            self.db.query(func.count(EventAttendance.id))
            .filter(EventAttendance.school_id == school_id)
            .filter(EventAttendance.event_id == event_id)
            .scalar()
        )

        return {"event_id": event_id, "attendance_count": attendance}

    # -----------------------------------------------------
    # 6) Early Warning System (AI-driven later)
    # -----------------------------------------------------
    def early_warning(self, school_id: int):
        # simple version: students with too many absences or clinic visits
        absences = (
            self.db.query(
                Attendance.student_id,
                func.count(Attendance.id).label("absent_days")
            )
            .filter(Attendance.school_id == school_id)
            .filter(Attendance.status == "absent")
            .group_by(Attendance.student_id)
            .having(func.count(Attendance.id) >= 5)
            .all()
        )

        health_issues = (
            self.db.query(
                HealthVisit.student_id,
                func.count(HealthVisit.id).label("visits")
            )
            .filter(HealthVisit.school_id == school_id)
            .group_by(HealthVisit.student_id)
            .having(func.count(HealthVisit.id) >= 3)
            .all()
        )

        return {
            "absentee_risk": [dict(row._mapping) for row in absences],
            "health_risk": [dict(row._mapping) for row in health_issues],
        }

