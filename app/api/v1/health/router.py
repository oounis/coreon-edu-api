from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role
from app.services.health.health_service import HealthService

router = APIRouter(prefix="/health", tags=["Health"])


# Upsert student health profile
@router.post("/students/{student_id}/profile")
def upsert_profile(
    student_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(
        require_roles(
            Role.NURSE,
            Role.HR,
            Role.SCHOOL_ADMIN,
            Role.SUPER_ADMIN,
        )
    ),
):
    svc = HealthService(db)

    allergies = payload.get("allergies") or []
    chronic_diseases = payload.get("chronic_diseases") or []
    medications = payload.get("medications") or []
    blood_type = payload.get("blood_type")
    emergency_contacts = payload.get("emergency_contacts") or []
    doctor_info = payload.get("doctor_info") or {}
    notes = payload.get("notes")
    meta = payload.get("meta") or {}

    return svc.upsert_profile(
        school_id=user.school_id,
        student_id=student_id,
        allergies=allergies,
        chronic_diseases=chronic_diseases,
        medications=medications,
        blood_type=blood_type,
        emergency_contacts=emergency_contacts,
        doctor_info=doctor_info,
        notes=notes,
        meta=meta,
        updated_by=user.id,
    )


# Register clinic visit
@router.post("/students/{student_id}/visits")
def add_visit(
    student_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(
        require_roles(
            Role.NURSE,
            Role.SCHOOL_ADMIN,
            Role.SUPER_ADMIN,
        )
    ),
):
    svc = HealthService(db)

    reason = payload["reason"]
    diagnosis = payload.get("diagnosis")
    treatment = payload.get("treatment")
    vitals = payload.get("vitals") or {}
    visit_time_raw = payload.get("visit_time")
    visit_time = (
        datetime.fromisoformat(visit_time_raw)
        if visit_time_raw
        else None
    )
    meta = payload.get("meta") or {}

    return svc.add_visit(
        school_id=user.school_id,
        student_id=student_id,
        reason=reason,
        diagnosis=diagnosis,
        treatment=treatment,
        vitals=vitals,
        visit_time=visit_time,
        meta=meta,
        created_by=user.id,
    )


# Report health incident (injury, accident, etc.)
@router.post("/students/{student_id}/incidents")
def report_incident(
    student_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(
        require_roles(
            Role.NURSE,
            Role.HR,
            Role.SCHOOL_ADMIN,
            Role.SUPER_ADMIN,
        )
    ),
):
    svc = HealthService(db)

    title = payload["title"]
    description = payload.get("description", "")
    location = payload.get("location")
    severity = payload.get("severity", "normal")
    happened_at_raw = payload.get("happened_at")
    happened_at = (
        datetime.fromisoformat(happened_at_raw)
        if happened_at_raw
        else None
    )
    notify_parent = bool(payload.get("notify_parent", True))
    meta = payload.get("meta") or {}

    return svc.report_incident(
        school_id=user.school_id,
        student_id=student_id,
        title=title,
        description=description,
        location=location,
        severity=severity,
        happened_at=happened_at,
        meta=meta,
        created_by=user.id,
        notify_parent=notify_parent,
    )


# Student health summary
@router.get("/students/{student_id}/summary")
def student_summary(
    student_id: int,
    limit_visits: int = Query(10, ge=1, le=100),
    limit_incidents: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user=Depends(
        require_roles(
            Role.NURSE,
            Role.HR,
            Role.SCHOOL_ADMIN,
            Role.SUPER_ADMIN,
            Role.PRINCIPAL,
        )
    ),
):
    svc = HealthService(db)
    return svc.student_summary(
        school_id=user.school_id,
        student_id=student_id,
        limit_visits=limit_visits,
        limit_incidents=limit_incidents,
    )
