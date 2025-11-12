from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.db.session import SessionLocal
from app.models.academic import Subject, Attendance

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- Subjects ----------
class SubjectCreate(BaseModel):
    name: str = Field(..., min_length=2)
    grade_id: int
    teacher_id: Optional[int] = None

class SubjectOut(BaseModel):
    id: int
    name: str
    grade_id: int
    teacher_id: Optional[int]
    class Config:
        from_attributes = True

@router.post("/subjects", response_model=SubjectOut)
def create_subject(payload: SubjectCreate, db: Session = Depends(get_db)):
    s = Subject(name=payload.name, grade_id=payload.grade_id, teacher_id=payload.teacher_id)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

@router.get("/subjects", response_model=List[SubjectOut])
def list_subjects(grade_id: Optional[int] = None, db: Session = Depends(get_db)):
    stmt = select(Subject)
    if grade_id is not None:
        stmt = stmt.where(Subject.grade_id == grade_id)
    return list(db.execute(stmt).scalars())

# ---------- Attendance ----------
class AttendanceMark(BaseModel):
    date: date
    classroom_id: int
    present_ids: List[int] = []
    absent_ids: List[int] = []
    late_ids: List[int] = []
    notes: Optional[str] = None

@router.post("/attendance/mark")
def mark_attendance(mark: AttendanceMark, db: Session = Depends(get_db)):
    db.query(Attendance).filter(
        and_(Attendance.date == mark.date, Attendance.classroom_id == mark.classroom_id)
    ).delete(synchronize_session=False)

    to_create = []
    for sid in mark.present_ids:
        to_create.append(Attendance(date=mark.date, classroom_id=mark.classroom_id, student_id=sid, status="present", notes=mark.notes))
    for sid in mark.absent_ids:
        to_create.append(Attendance(date=mark.date, classroom_id=mark.classroom_id, student_id=sid, status="absent", notes=mark.notes))
    for sid in mark.late_ids:
        to_create.append(Attendance(date=mark.date, classroom_id=mark.classroom_id, student_id=sid, status="late", notes=mark.notes))

    if to_create:
        db.add_all(to_create)
    db.commit()
    return {"ok": True, "inserted": len(to_create)}

class AttendanceOut(BaseModel):
    id: int
    date: date
    classroom_id: int
    student_id: int
    status: str
    notes: Optional[str]
    class Config:
        from_attributes = True

@router.get("/attendance/day", response_model=List[AttendanceOut])
def get_attendance_day(classroom_id: int, date_: date, db: Session = Depends(get_db)):
    stmt = select(Attendance).where(and_(Attendance.classroom_id == classroom_id, Attendance.date == date_))
    return list(db.execute(stmt).scalars())
