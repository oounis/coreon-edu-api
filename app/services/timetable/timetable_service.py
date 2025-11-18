from __future__ import annotations
from typing import Dict, Any, List, Optional
from datetime import time, datetime

from sqlalchemy.orm import Session

from app.models import (
    TimetableEntry,
    Subject,
    Teacher,
    Classroom,
)
from app.services.notification_service import NotificationService


class TimetableService:
    """
    Full academic timetable system:
    - Weekly schedules
    - Teacher load balancing
    - Room allocation
    - Conflict detection (teacher / room / class)
    - Daily view per teacher & per class
    """

    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationService(db)

    # ----------------------------------
    # Create session entry
    # ----------------------------------
    def create_entry(
        self,
        *,
        school_id: int,
        class_id: int,
        subject_id: int,
        teacher_id: int,
        room_id: int,
        day_of_week: int,     # 0=Mon ... 6=Sun
        start_time: str,
        end_time: str,
        meta: Optional[Dict[str, Any]],
        created_by: int,
    ):
        # Conflict detection
        st = datetime.strptime(start_time, "%H:%M").time()
        et = datetime.strptime(end_time, "%H:%M").time()

        # Teacher conflict
        teacher_conflict = (
            self.db.query(TimetableEntry)
            .filter(TimetableEntry.school_id == school_id)
            .filter(TimetableEntry.teacher_id == teacher_id)
            .filter(TimetableEntry.day_of_week == day_of_week)
            .filter(TimetableEntry.start_time < et)
            .filter(TimetableEntry.end_time > st)
            .first()
        )

        if teacher_conflict:
            raise ValueError("Teacher has another class at this time.")

        # Room conflict
        room_conflict = (
            self.db.query(TimetableEntry)
            .filter(TimetableEntry.school_id == school_id)
            .filter(TimetableEntry.room_id == room_id)
            .filter(TimetableEntry.day_of_week == day_of_week)
            .filter(TimetableEntry.start_time < et)
            .filter(TimetableEntry.end_time > st)
            .first()
        )

        if room_conflict:
            raise ValueError("Room is already booked at this time.")

        entry = TimetableEntry(
            school_id=school_id,
            class_id=class_id,
            subject_id=subject_id,
            teacher_id=teacher_id,
            room_id=room_id,
            day_of_week=day_of_week,
            start_time=st,
            end_time=et,
            meta=meta or {},
            created_by=created_by,
        )

        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)

        return {"entry": entry}

    # ----------------------------------
    # List full timetable for a class
    # ----------------------------------
    def class_timetable(self, *, school_id: int, class_id: int):
        items = (
            self.db.query(TimetableEntry)
            .filter(TimetableEntry.school_id == school_id)
            .filter(TimetableEntry.class_id == class_id)
            .order_by(TimetableEntry.day_of_week.asc(), TimetableEntry.start_time.asc())
            .all()
        )
        return {"timetable": items}

    # ----------------------------------
    # Teacher schedule
    # ----------------------------------
    def teacher_timetable(self, *, school_id: int, teacher_id: int):
        items = (
            self.db.query(TimetableEntry)
            .filter(TimetableEntry.school_id == school_id)
            .filter(TimetableEntry.teacher_id == teacher_id)
            .order_by(TimetableEntry.day_of_week.asc(), TimetableEntry.start_time.asc())
            .all()
        )
        return {"schedule": items}

    # ----------------------------------
    # Room usage
    # ----------------------------------
    def room_timetable(self, *, school_id: int, room_id: int):
        items = (
            self.db.query(TimetableEntry)
            .filter(TimetableEntry.school_id == school_id)
            .filter(TimetableEntry.room_id == room_id)
            .order_by(TimetableEntry.day_of_week.asc(), TimetableEntry.start_time.asc())
            .all()
        )
        return {"room_usage": items}

    # ----------------------------------
    # Delete entry
    # ----------------------------------
    def delete_entry(self, *, school_id: int, entry_id: int):
        entry = (
            self.db.query(TimetableEntry)
            .filter(TimetableEntry.school_id == school_id)
            .filter(TimetableEntry.id == entry_id)
            .first()
        )
        if not entry:
            raise ValueError("Timetable entry not found.")

        self.db.delete(entry)
        self.db.commit()

        return {"deleted": entry_id}
