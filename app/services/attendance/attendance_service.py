from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.models import (
    AttendanceRecord,
    Student,
    Classroom,
)
from app.services.notification_service import NotificationService


class AttendanceService:
    """
    Attendance System:
    - Take attendance (manual or QR/RFID)
    - Bulk class attendance
    - Late/absent rules
    - Parent notifications
    """

    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationService(db)

    # --------------------------
    # Single scan
    # --------------------------
    def scan(
        self,
        *,
        school_id: int,
        student_id: int,
        status: str,     # present | absent | late | excused
        timestamp: Optional[datetime],
        meta: Optional[Dict[str, Any]],
        created_by: int,
        notify_parent: bool = True,
    ):
        rec = AttendanceRecord(
            school_id=school_id,
            student_id=student_id,
            status=status,
            timestamp=timestamp or datetime.utcnow(),
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(rec)
        self.db.commit()
        self.db.refresh(rec)

        # parent notifications on abnormal events
        if notify_parent and status in ("absent", "late"):
            try:
                self.notifications.create(
                    user_id=student_id,  # later link actual parent
                    school_id=school_id,
                    key="attendance_alert",
                    type="attendance",
                    category="alert",
                    data={"student_id": student_id, "status": status},
                    priority="high",
                )
            except Exception:
                pass

        return {"attendance": rec}

    # --------------------------
    # Bulk classroom attendance
    # --------------------------
    def bulk_class_attendance(
        self,
        *,
        school_id: int,
        classroom_id: int,
        items: List[Dict[str, Any]],
        created_by: int,
    ):
        saved = []
        for item in items:
            rec = AttendanceRecord(
                school_id=school_id,
                student_id=item["student_id"],
                status=item.get("status", "present"),
                timestamp=datetime.utcnow(),
                meta=item.get("meta") or {},
                created_by=created_by,
                classroom_id=classroom_id,
            )
            self.db.add(rec)
            saved.append(rec)

        self.db.commit()
        return {"saved": saved}

    # --------------------------
    # Student attendance history
    # --------------------------
    def student_history(
        self,
        *,
        school_id: int,
        student_id: int,
        limit: int = 50,
    ):
        q = (
            self.db.query(AttendanceRecord)
            .filter(AttendanceRecord.school_id == school_id)
            .filter(AttendanceRecord.student_id == student_id)
            .order_by(AttendanceRecord.timestamp.desc())
            .limit(limit)
        )
        return {"attendance": q.all()}
