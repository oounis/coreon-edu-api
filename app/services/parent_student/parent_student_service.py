from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import (
    Parent,
    Student,
    ParentStudent,
    Attendance,
    FinanceInvoice,
    BehaviorRecord,
    GradeRecord,
)
from app.services.notification_service import NotificationService


class ParentStudentService:

    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationService(db)

    # ------------------------------------------------
    # LINK parent to student
    # ------------------------------------------------
    def link(
        self,
        *,
        school_id: int,
        parent_id: int,
        student_id: int,
        relation: str,
        meta: Optional[Dict[str, Any]],
        created_by: int,
    ):
        parent = (
            self.db.query(Parent)
            .filter(Parent.id == parent_id)
            .filter(Parent.school_id == school_id)
            .first()
        )
        if not parent:
            raise ValueError("Parent not found in this school")

        student = (
            self.db.query(Student)
            .filter(Student.id == student_id)
            .filter(Student.school_id == school_id)
            .first()
        )
        if not student:
            raise ValueError("Student not found in this school")

        link = ParentStudent(
            school_id=school_id,
            parent_id=parent_id,
            student_id=student_id,
            relation=relation,     # father | mother | guardian | sponsor | other
            status="active",
            meta=meta or {},
            created_by=created_by,
        )

        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)

        # Notify parent
        try:
            self.notifications.create(
                user_id=parent_id,
                school_id=school_id,
                key="linked_student",
                type="parent",
                category="relationship",
                data={"student_id": student_id},
                priority="normal",
            )
        except Exception:
            pass

        return {"link": link}

    # ------------------------------------------------
    # Unlink parent ↔ student
    # ------------------------------------------------
    def unlink(
        self,
        *,
        school_id: int,
        parent_id: int,
        student_id: int,
        reason: Optional[str],
        updated_by: int,
    ):
        link = (
            self.db.query(ParentStudent)
            .filter(ParentStudent.school_id == school_id)
            .filter(ParentStudent.parent_id == parent_id)
            .filter(ParentStudent.student_id == student_id)
            .first()
        )
        if not link:
            raise ValueError("Relationship not found")

        link.status = "inactive"
        link.meta = {"reason": reason, "unlinked_at": datetime.utcnow()}
        link.updated_by = updated_by

        self.db.commit()
        self.db.refresh(link)

        return {"unlink": link}

    # ------------------------------------------------
    # List children for parent
    # ------------------------------------------------
    def parent_children(
        self,
        *,
        school_id: int,
        parent_id: int,
    ):
        items = (
            self.db.query(ParentStudent)
            .filter(ParentStudent.school_id == school_id)
            .filter(ParentStudent.parent_id == parent_id)
            .filter(ParentStudent.status == "active")
            .all()
        )
        return {"children": items}

    # ------------------------------------------------
    # List parents of student
    # ------------------------------------------------
    def student_parents(
        self,
        *,
        school_id: int,
        student_id: int,
    ):
        items = (
            self.db.query(ParentStudent)
            .filter(ParentStudent.school_id == school_id)
            .filter(ParentStudent.student_id == student_id)
            .filter(ParentStudent.status == "active")
            .all()
        )
        return {"parents": items}

    # ------------------------------------------------
    # Parent dashboard student summary
    # ------------------------------------------------
    def student_summary(
        self,
        *,
        school_id: int,
        student_id: int,
    ):
        student = (
            self.db.query(Student)
            .filter(Student.id == student_id)
            .filter(Student.school_id == school_id)
            .first()
        )
        if not student:
            raise ValueError("Student not found")

        attendance = (
            self.db.query(Attendance)
            .filter(Attendance.student_id == student_id)
            .order_by(Attendance.date.desc())
            .limit(20)
            .all()
        )

        behavior = (
            self.db.query(BehaviorRecord)
            .filter(BehaviorRecord.student_id == student_id)
            .order_by(BehaviorRecord.created_at.desc())
            .limit(20)
            .all()
        )

        grades = (
            self.db.query(GradeRecord)
            .filter(GradeRecord.student_id == student_id)
            .order_by(GradeRecord.created_at.desc())
            .limit(20)
            .all()
        )

        invoices = (
            self.db.query(FinanceInvoice)
            .filter(FinanceInvoice.student_id == student_id)
            .order_by(FinanceInvoice.created_at.desc())
            .limit(20)
            .all()
        )

        return {
            "student": student,
            "attendance": attendance,
            "behavior": behavior,
            "grades": grades,
            "invoices": invoices,
        }
