from sqlalchemy import Column, Integer, String, ForeignKey, Time, Date, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.session import Base

class LessonStatus(str, enum.Enum):
    scheduled = "scheduled"
    in_class = "in_class"
    paused = "paused"
    finished = "finished"
    canceled = "canceled"

class TimetableSlot(Base):
    __tablename__ = "timetable_slots"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False, index=True)
    subject_id   = Column(Integer, ForeignKey("subjects.id"),   nullable=False, index=True)
    teacher_id   = Column(Integer, ForeignKey("teachers.id"),   nullable=True,  index=True)

    # 1 = Monday … 7 = Sunday (fits Bahrain: school week Sun–Thu if you prefer 7=Sat adjust later)
    day_of_week  = Column(Integer, nullable=False)  # 1..7
    period       = Column(Integer, nullable=True)   # Optional: 1st period, 2nd period ...
    start_time   = Column(Time, nullable=False)
    end_time     = Column(Time,  nullable=False)

    __table_args__ = (
        UniqueConstraint("classroom_id", "day_of_week", "start_time", name="uq_slot_class_day_start"),
    )

class LessonSession(Base):
    __tablename__ = "lesson_sessions"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False, index=True)
    subject_id   = Column(Integer, ForeignKey("subjects.id"),   nullable=False, index=True)
    teacher_id   = Column(Integer, ForeignKey("teachers.id"),   nullable=True,  index=True)

    date     = Column(Date, nullable=False, index=True)
    start_ts = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_ts   = Column(DateTime, nullable=True)

    status = Column(Enum(LessonStatus), nullable=False, default=LessonStatus.in_class)
    notes  = Column(String, nullable=True)
