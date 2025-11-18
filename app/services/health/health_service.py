from __future__ import annotations
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import (
    # NOTE: تأكد لاحقاً من أسماء الموديلات أو عدلها حسب سكيمتك
    Student,
    HealthProfile,
    HealthVisit,
    HealthIncident,
)
from app.services.notification_service import NotificationService


class HealthService:
    """
    Student medical & health records:
    - Core health profile (allergies, chronic diseases, medications...)
    - Clinic / nurse visits
    - Incident reports (injury, accident, etc.)
    - Optional notifications for critical incidents
    """

    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationService(db)

    # ---------- Profiles ----------

    def upsert_profile(
        self,
        *,
        school_id: int,
        student_id: int,
        allergies: Optional[List[str]] = None,
        chronic_diseases: Optional[List[str]] = None,
        medications: Optional[List[str]] = None,
        blood_type: Optional[str] = None,
        emergency_contacts: Optional[List[Dict[str, Any]]] = None,
        doctor_info: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        updated_by: Optional[int] = None,
    ) -> Dict[str, Any]:
        profile = (
            self.db.query(HealthProfile)
            .filter(HealthProfile.school_id == school_id)
            .filter(HealthProfile.student_id == student_id)
            .first()
        )

        if not profile:
            profile = HealthProfile(
                school_id=school_id,
                student_id=student_id,
            )
            self.db.add(profile)

        profile.allergies = allergies or []
        profile.chronic_diseases = chronic_diseases or []
        profile.medications = medications or []
        profile.blood_type = blood_type
        profile.emergency_contacts = emergency_contacts or []
        profile.doctor_info = doctor_info or {}
        profile.notes = notes
        profile.meta = meta or {}
        profile.updated_by = updated_by
        profile.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(profile)

        return {"profile": profile}

    # ---------- Visits (clinic) ----------

    def add_visit(
        self,
        *,
        school_id: int,
        student_id: int,
        reason: str,
        diagnosis: Optional[str] = None,
        treatment: Optional[str] = None,
        vitals: Optional[Dict[str, Any]] = None,
        visit_time: Optional[datetime] = None,
        meta: Optional[Dict[str, Any]] = None,
        created_by: Optional[int] = None,
    ) -> Dict[str, Any]:
        visit = HealthVisit(
            school_id=school_id,
            student_id=student_id,
            reason=reason,
            diagnosis=diagnosis,
            treatment=treatment,
            vitals=vitals or {},
            visit_time=visit_time or datetime.utcnow(),
            meta=meta or {},
            created_by=created_by,
        )

        self.db.add(visit)
        self.db.commit()
        self.db.refresh(visit)

        return {"visit": visit}

    # ---------- Incidents ----------

    def report_incident(
        self,
        *,
        school_id: int,
        student_id: int,
        title: str,
        description: str,
        location: Optional[str] = None,
        severity: str = "normal",  # normal | high | critical
        happened_at: Optional[datetime] = None,
        meta: Optional[Dict[str, Any]] = None,
        created_by: Optional[int] = None,
        notify_parent: bool = True,
    ) -> Dict[str, Any]:
        incident = HealthIncident(
            school_id=school_id,
            student_id=student_id,
            title=title,
            description=description,
            location=location,
            severity=severity,
            happened_at=happened_at or datetime.utcnow(),
            meta=meta or {},
            created_by=created_by,
        )

        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)

        # Notifications (very simple version — can be extended later)
        if notify_parent and severity in ("high", "critical"):
            try:
                # مبدئياً نبعت نوتيفيكايشن للشخص اللي سجّل الحادثة
                # لاحقاً تنجم تربطها بالأولياء + الإدارة + القائد
                self.notifications.create(
                    user_id=created_by or 0,
                    school_id=school_id,
                    key="health_incident_critical",
                    type="health",
                    category="incidents",
                    data={
                        "incident_id": incident.id,
                        "student_id": student_id,
                        "severity": severity,
                        "title": title,
                    },
                    priority="critical",
                )
            except Exception:
                # health incidents must never fail because of notifications
                pass

        return {"incident": incident}

    # ---------- Summary ----------

    def student_summary(
        self,
        *,
        school_id: int,
        student_id: int,
        limit_visits: int = 10,
        limit_incidents: int = 10,
    ) -> Dict[str, Any]:
        profile = (
            self.db.query(HealthProfile)
            .filter(HealthProfile.school_id == school_id)
            .filter(HealthProfile.student_id == student_id)
            .first()
        )

        visits = (
            self.db.query(HealthVisit)
            .filter(HealthVisit.school_id == school_id)
            .filter(HealthVisit.student_id == student_id)
            .order_by(HealthVisit.visit_time.desc())
            .limit(limit_visits)
            .all()
        )

        incidents = (
            self.db.query(HealthIncident)
            .filter(HealthIncident.school_id == school_id)
            .filter(HealthIncident.student_id == student_id)
            .order_by(HealthIncident.happened_at.desc())
            .limit(limit_incidents)
            .all()
        )

        return {
            "profile": profile,
            "recent_visits": visits,
            "recent_incidents": incidents,
        }
