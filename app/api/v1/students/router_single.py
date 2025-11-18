from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app import models

router = APIRouter()


# ====================================================
# GET: Student Overview
# ====================================================
@router.get("/students/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = (
        db.query(models.Student)
        .filter(models.Student.id == student_id)
        .first()
    )

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return student


# ====================================================
# GET: Student Attendance
# ====================================================
@router.get("/students/{student_id}/attendance")
def get_student_attendance(student_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(models.Attendance)
        .filter(models.Attendance.student_id == student_id)
        .order_by(models.Attendance.date.desc())
        .all()
    )
    return rows


# ====================================================
# GET: Student Grades (placeholder)
# ====================================================
@router.get("/students/{student_id}/grades")
def get_student_grades(student_id: int):
    # Replace later with proper grade models
    return [
        {"id": 1, "subject": "Math", "score": 88},
        {"id": 2, "subject": "Science", "score": 92},
    ]


# ====================================================
# GET: Parents Linked to Student
# ====================================================
@router.get("/students/{student_id}/parents")
def get_student_parents(student_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(models.ParentStudent)
        .filter(models.ParentStudent.student_id == student_id)
        .all()
    )
    return rows


# ====================================================
# GET: Student Documents (placeholder)
# ====================================================
@router.get("/students/{student_id}/documents")
def get_student_documents(student_id: int):
    return [
        {"id": 1, "name": "Birth Certificate", "type": "PDF"},
        {"id": 2, "name": "Medical Report", "type": "PDF"},
    ]
