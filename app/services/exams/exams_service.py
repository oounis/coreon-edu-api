from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import (
    Exam,
    ExamSession,
    ExamMark,
    Student,
    Subject,
)
from app.services.notification_service import NotificationService


class ExamsService:

    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationService(db)

    # ------------------------------
    # EXAMS
    # ------------------------------
    def create_exam(
        self,
        *,
        school_id: int,
        title: str,
        grade: str,
        term_id: int,
        description: Optional[str],
        meta: Optional[Dict[str, Any]],
        created_by: int,
    ):
        exam = Exam(
            school_id=school_id,
            title=title,
            grade=grade,
            term_id=term_id,
            description=description,
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return {"exam": exam}

    def list_exams(self, *, school_id: int, grade: Optional[str] = None):
        q = self.db.query(Exam).filter(Exam.school_id == school_id)
        if grade:
            q = q.filter(Exam.grade == grade)
        return {"exams": q.all()}

    # ------------------------------
    # EXAM SESSIONS
    # ------------------------------
    def create_session(
        self,
        *,
        school_id: int,
        exam_id: int,
        subject_id: int,
        date: datetime,
        start_time: datetime,
        end_time: datetime,
        room: Optional[str],
        meta: Optional[Dict[str, Any]],
        created_by: int,
    ):
        session = ExamSession(
            school_id=school_id,
            exam_id=exam_id,
            subject_id=subject_id,
            date=date,
            start_time=start_time,
            end_time=end_time,
            room=room,
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return {"session": session}

    def list_sessions(self, *, school_id: int, exam_id: int):
        sessions = (
            self.db.query(ExamSession)
            .filter(ExamSession.school_id == school_id)
            .filter(ExamSession.exam_id == exam_id)
            .all()
        )
        return {"sessions": sessions}

    # ------------------------------
    # MARKS
    # ------------------------------
    def enter_mark(
        self,
        *,
        school_id: int,
        exam_id: int,
        session_id: int,
        student_id: int,
        subject_id: int,
        score: Decimal,
        meta: Optional[Dict[str, Any]],
        created_by: int,
    ):
        """single mark insertion or update"""

        mark = (
            self.db.query(ExamMark)
            .filter(ExamMark.school_id == school_id)
            .filter(ExamMark.exam_id == exam_id)
            .filter(ExamMark.session_id == session_id)
            .filter(ExamMark.student_id == student_id)
            .first()
        )

        if not mark:
            mark = ExamMark(
                school_id=school_id,
                exam_id=exam_id,
                session_id=session_id,
                student_id=student_id,
                subject_id=subject_id,
                score=score,
                meta=meta or {},
                created_by=created_by,
            )
            self.db.add(mark)
        else:
            mark.score = score
            mark.meta = meta or {}
            mark.updated_by = created_by

        self.db.commit()
        self.db.refresh(mark)

        return {"mark": mark}

    def list_marks(self, *, school_id: int, exam_id: int, student_id: Optional[int] = None):
        q = (
            self.db.query(ExamMark)
            .filter(ExamMark.school_id == school_id)
            .filter(ExamMark.exam_id == exam_id)
        )
        if student_id:
            q = q.filter(ExamMark.student_id == student_id)

        return {"marks": q.all()}


    # ------------------------------
    # GRADEBOOK (auto)
    # ------------------------------
    def compute_gradebook(
        self,
        *,
        school_id: int,
        exam_id: int,
    ):
        items = (
            self.db.query(ExamMark)
            .filter(ExamMark.school_id == school_id)
            .filter(ExamMark.exam_id == exam_id)
            .all()
        )

        result: Dict[int, List[ExamMark]] = {}

        for item in items:
            result.setdefault(item.student_id, []).append(item)

        gradebook = []
        for student_id, marks in result.items():
            total = sum([m.score for m in marks])
            avg = total / Decimal(len(marks)) if marks else Decimal("0")

            gradebook.append({
                "student_id": student_id,
                "total": total,
                "average": avg,
                "subjects": marks,
            })

        return {"gradebook": gradebook}

