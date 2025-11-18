from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role
from app.services.analytics.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ----------------------------------------
# Attendance
# ----------------------------------------
@router.get("/attendance")
def attendance_summary(
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.SCHOOL_ADMIN, Role.SUPER_ADMIN, Role.PRINCIPAL)),
):
    svc = AnalyticsService(db)
    return svc.attendance_summary(
        school_id=user.school_id,
        date_from=date_from,
        date_to=date_to,
    )


# ----------------------------------------
# Grades
# ----------------------------------------
@router.get("/grades")
def grades_summary(
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.TEACHER, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = AnalyticsService(db)
    return svc.grade_distribution(school_id=user.school_id)


# ----------------------------------------
# Transport
# ----------------------------------------
@router.get("/transport")
def transport_kpis(
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.TRANSPORT, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN)),
):
    svc = AnalyticsService(db)
    return svc.transport_kpis(
        school_id=user.school_id,
        date_from=date_from,
        date_to=date_to,
    )


# ----------------------------------------
# Health
# ----------------------------------------
@router.get("/health")
def health_summary(
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.NURSE, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN
    )),
):
    svc = AnalyticsService(db)
    return svc.health_kpis(
        school_id=user.school_id,
        date_from=date_from,
        date_to=date_to,
    )


# ----------------------------------------
# Events
# ----------------------------------------
@router.get("/events/{event_id}")
def event_stats(
    event_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.TEACHER, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN, Role.PRINCIPAL
    )),
):
    svc = AnalyticsService(db)
    return svc.events_summary(
        school_id=user.school_id,
        event_id=event_id,
    )


# ----------------------------------------
# Early Warning System
# ----------------------------------------
@router.get("/early-warning")
def early_warning(
    db: Session = Depends(get_db),
    user=Depends(require_roles(
        Role.HR, Role.SCHOOL_ADMIN, Role.SUPER_ADMIN, Role.PRINCIPAL
    )),
):
    svc = AnalyticsService(db)
    return svc.early_warning(school_id=user.school_id)
