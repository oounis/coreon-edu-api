from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import (
    Subject,
    Curriculum,
    AcademicTerm,
    TeacherAssignment,
    LessonPlan,
)
from app.services.notification_service import NotificationService


class AcademicsService:

    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationService(db)

    # SUBJECTS
    def create_subject(self, *, school_id: int, title: str, code: str, level: str, meta: Dict[str, Any], created_by: int):
        subject = Subject(
            school_id=school_id,
            title=title,
            code=code,
            level=level,
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)
        return {"subject": subject}

    def list_subjects(self, *, school_id: int):
        subs = self.db.query(Subject).filter(Subject.school_id == school_id).all()
        return {"subjects": subs}

    # CURRICULUM
    def create_curriculum(
        self,
        *,
        school_id: int,
        title: str,
        description: str,
        grade: str,
        meta: Dict[str, Any],
        created_by: int,
    ):
        cur = Curriculum(
            school_id=school_id,
            title=title,
            description=description,
            grade=grade,
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(cur)
        self.db.commit()
        self.db.refresh(cur)
        return {"curriculum": cur}

    def list_curriculum(self, *, school_id: int):
        items = (
            self.db.query(Curriculum)
            .filter(Curriculum.school_id == school_id)
            .all()
        )
        return {"curriculum": items}

    # TERMS
    def create_term(
        self,
        *,
        school_id: int,
        title: str,
        start_date: datetime,
        end_date: datetime,
        meta: Dict[str, Any],
        created_by: int,
    ):
        term = AcademicTerm(
            school_id=school_id,
            title=title,
            start_date=start_date,
            end_date=end_date,
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(term)
        self.db.commit()
        self.db.refresh(term)
        return {"term": term}

    def list_terms(self, *, school_id: int):
        terms = (
            self.db.query(AcademicTerm)
            .filter(AcademicTerm.school_id == school_id)
            .order_by(AcademicTerm.start_date.asc())
            .all()
        )
        return {"terms": terms}

    # TEACHER ASSIGNMENTS
    def assign_teacher(
        self,
        *,
        school_id: int,
        subject_id: int,
        teacher_id: int,
        class_id: int,
        meta: Dict[str, Any],
        created_by: int,
    ):
        ta = TeacherAssignment(
            school_id=school_id,
            subject_id=subject_id,
            teacher_id=teacher_id,
            class_id=class_id,
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(ta)
        self.db.commit()
        self.db.refresh(ta)
        return {"assignment": ta}

    def list_assignments(self, *, school_id: int, class_id: Optional[int] = None):
        q = self.db.query(TeacherAssignment).filter(TeacherAssignment.school_id == school_id)
        if class_id:
            q = q.filter(TeacherAssignment.class_id == class_id)
        return {"assignments": q.all()}

    # LESSON PLANS
    def create_lesson_plan(
        self,
        *,
        school_id: int,
        teacher_id: int,
        class_id: int,
        subject_id: int,
        date: datetime,
        title: str,
        content: str,
        meta: Dict[str, Any],
        created_by: int,
    ):
        plan = LessonPlan(
            school_id=school_id,
            teacher_id=teacher_id,
            class_id=class_id,
            subject_id=subject_id,
            date=date,
            title=title,
            content=content,
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return {"plan": plan}

    def list_lesson_plans(self, *, school_id: int, class_id: Optional[int] = None):
        q = self.db.query(LessonPlan).filter(LessonPlan.school_id == school_id)
        if class_id:
            q = q.filter(LessonPlan.class_id == class_id)
        return {"plans": q.all()}
