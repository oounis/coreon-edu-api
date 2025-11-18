from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import (
    Homework,
    HomeworkSubmission,
)
from app.services.notification_service import NotificationService


class HomeworkService:

    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationService(db)

    # -----------------------------
    # Teacher creates homework
    # -----------------------------
    def create_homework(
        self,
        *,
        school_id: int,
        teacher_id: int,
        classroom_id: int,
        subject_id: int,
        title: str,
        description: str,
        due_date: datetime,
        attachments: Optional[List[Dict[str, Any]]],
        meta: Optional[Dict[str, Any]],
    ):
        hw = Homework(
            school_id=school_id,
            teacher_id=teacher_id,
            classroom_id=classroom_id,
            subject_id=subject_id,
            title=title,
            description=description,
            due_date=due_date,
            attachments=attachments or [],
            meta=meta or {},
        )
        self.db.add(hw)
        self.db.commit()
        self.db.refresh(hw)

        # Notify parents/students
        try:
            self.notifications.broadcast(
                school_id=school_id,
                key="homework_new",
                type="academics",
                category="homework",
                data={"title": title},
                audience="classroom:" + str(classroom_id),
            )
        except Exception:
            pass

        return {"homework": hw}

    # -----------------------------
    # List homework for classroom
    # -----------------------------
    def list_homework(
        self,
        *,
        school_id: int,
        classroom_id: int,
    ):
        items = (
            self.db.query(Homework)
            .filter(Homework.school_id == school_id)
            .filter(Homework.classroom_id == classroom_id)
            .order_by(Homework.due_date.desc())
            .all()
        )
        return {"homework": items}

    # -----------------------------
    # Student submission
    # -----------------------------
    def submit(
        self,
        *,
        school_id: int,
        homework_id: int,
        student_id: int,
        content: Optional[str],
        attachments: Optional[List[Dict[str, Any]]],
        submitted_at: Optional[datetime],
        meta: Optional[Dict[str, Any]],
    ):
        submission = (
            self.db.query(HomeworkSubmission)
            .filter(HomeworkSubmission.homework_id == homework_id)
            .filter(HomeworkSubmission.student_id == student_id)
            .first()
        )

        if not submission:
            submission = HomeworkSubmission(
                school_id=school_id,
                homework_id=homework_id,
                student_id=student_id,
                content=content,
                attachments=attachments or [],
                submitted_at=submitted_at or datetime.utcnow(),
                status="submitted",
                meta=meta or {},
            )
            self.db.add(submission)
        else:
            submission.content = content
            submission.attachments = attachments or []
            submission.submitted_at = submitted_at or datetime.utcnow()
            submission.status = "resubmitted"
            submission.meta = meta or {}

        self.db.commit()
        self.db.refresh(submission)
        return {"submission": submission}

    # -----------------------------
    # Teacher review
    # -----------------------------
    def review_submission(
        self,
        *,
        school_id: int,
        homework_id: int,
        submission_id: int,
        feedback: Optional[str],
        score: Optional[float],
        reviewed_by: int,
    ):
        submission = (
            self.db.query(HomeworkSubmission)
            .filter(HomeworkSubmission.school_id == school_id)
            .filter(HomeworkSubmission.id == submission_id)
            .filter(HomeworkSubmission.homework_id == homework_id)
            .first()
        )

        if not submission:
            raise ValueError("Submission not found")

        submission.feedback = feedback
        submission.score = score
        submission.reviewed_by = reviewed_by
        submission.reviewed_at = datetime.utcnow()
        submission.status = "reviewed"

        self.db.commit()
        self.db.refresh(submission)

        # Notify parent/student
        try:
            self.notifications.create(
                user_id=submission.student_id,
                school_id=school_id,
                key="homework_reviewed",
                type="academics",
                category="homework",
                priority="normal",
                data={"homework_id": homework_id},
            )
        except Exception:
            pass

        return {"submission": submission}

    # -----------------------------
    # List submissions for homework
    # -----------------------------
    def list_submissions(
        self,
        *,
        school_id: int,
        homework_id: int,
    ):
        items = (
            self.db.query(HomeworkSubmission)
            .filter(HomeworkSubmission.school_id == school_id)
            .filter(HomeworkSubmission.homework_id == homework_id)
            .all()
        )
        return {"submissions": items}
