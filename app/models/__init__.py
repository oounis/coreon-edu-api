# app/models/__init__.py
# Register all model classes here so SQLAlchemy Base.metadata knows every table

from app.db.session import Base

# import in correct dependency order
from app.models.user import User
from app.models.school import School, Grade, Classroom, Teacher, Student, Parent
from app.models.academic import Subject, Attendance

__all__ = [
from app.models.audit import AuditLog
    "Base",
    "User",
    "School", "Grade", "Classroom", "Teacher", "Student", "Parent",
    "Subject", "Attendance",
]

# Timetable & sessions
from app.models.timetable import TimetableSlot, LessonSession, LessonStatus
__all__ += ["TimetableSlot", "LessonSession", "LessonStatus"]
