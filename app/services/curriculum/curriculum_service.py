from __future__ import annotations
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models import (
    CoursePlan,
    CourseOutcome,
    CourseSyllabus,
)


class CurriculumService:
    """
    Academic curriculum domain:
    - Course plans
    - Course outcomes
    - Syllabus sections
    """

    def __init__(self, db: Session):
        self.db = db

    def create_plan(self, *, school_id: int, subject_id: int, term: str, meta: Dict[str, Any], created_by: int):
        p = CoursePlan(
            school_id=school_id,
            subject_id=subject_id,
            term=term,
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(p)
        self.db.commit()
        self.db.refresh(p)
        return {"plan": p}

    def add_outcome(self, *, school_id: int, plan_id: int, title: str, description: str, created_by: int):
        o = CourseOutcome(
            school_id=school_id,
            plan_id=plan_id,
            title=title,
            description=description,
            created_by=created_by,
        )
        self.db.add(o)
        self.db.commit()
        self.db.refresh(o)
        return {"outcome": o}

    def add_syllabus(self, *, school_id: int, plan_id: int, title: str, content: str, created_by: int):
        s = CourseSyllabus(
            school_id=school_id,
            plan_id=plan_id,
            title=title,
            content=content,
            created_by=created_by,
        )
        self.db.add(s)
        self.db.commit()
        self.db.refresh(s)
        return {"syllabus": s}
