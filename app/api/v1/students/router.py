from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db.session import get_db
from app import models
from app.core.security import get_current_user

router = APIRouter()

# =================================
# Pydantic Schemas
# =================================

class StudentBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    birthdate: Optional[str] = None
    gender: Optional[str] = None
    national_id: Optional[str] = None
    admission_number: Optional[str] = None
    profile_photo_url: Optional[str] = None
    is_active: Optional[bool] = True

class StudentCreate(StudentBase):
    name: str

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    birthdate: Optional[str] = None
    gender: Optional[str] = None
    national_id: Optional[str] = None
    admission_number: Optional[str] = None
    profile_photo_url: Optional[str] = None
    is_active: Optional[bool] = None

class StudentOut(StudentBase):
    id: int
    classroom_id: int

    class Config:
        orm_mode = True

# =================================
# Helpers
# =================================

def _check_access(db: Session, current_user: models.User, school_id: int):
    if current_user.role == "admin":
        return
    link = (
        db.query(models.SchoolAdmin)
        .filter(
            models.SchoolAdmin.user_id == current_user.id,
            models.SchoolAdmin.school_id == school_id,
        )
        .first()
    )
    if not link:
        raise HTTPException(status_code=403, detail="Not allowed")

def _validate_structure(db: Session, school_id: int, grade_id: int, classroom_id: int):
    grade = (
        db.query(models.Grade)
        .filter(models.Grade.id == grade_id, models.Grade.school_id == school_id)
        .first()
    )
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")

    classroom = (
        db.query(models.Classroom)
        .filter(models.Classroom.id == classroom_id, models.Classroom.grade_id == grade_id)
        .first()
    )
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    return classroom

# =================================
# Routes
# =================================

@router.post(
    "/{school_id}/grades/{grade_id}/classrooms/{classroom_id}/students",
    response_model=StudentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_student(school_id: int, grade_id: int, classroom_id: int,
                   payload: StudentCreate,
                   db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):

    _check_access(db, current_user, school_id)
    _validate_structure(db, school_id, grade_id, classroom_id)

    student = models.Student(
        name=payload.name,
        email=payload.email,
        birthdate=payload.birthdate,
        gender=payload.gender,
        national_id=payload.national_id,
        admission_number=payload.admission_number,
        profile_photo_url=payload.profile_photo_url,
        is_active=payload.is_active,
        classroom_id=classroom_id,
    )

    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.get(
    "/{school_id}/grades/{grade_id}/classrooms/{classroom_id}/students",
    response_model=List[StudentOut],
)
def list_students(school_id: int, grade_id: int, classroom_id: int,
                  db: Session = Depends(get_db),
                  current_user: models.User = Depends(get_current_user)):

    _check_access(db, current_user, school_id)
    _validate_structure(db, school_id, grade_id, classroom_id)

    return (
        db.query(models.Student)
        .filter(models.Student.classroom_id == classroom_id)
        .order_by(models.Student.id)
        .all()
    )


@router.get(
    "/{school_id}/grades/{grade_id}/classrooms/{classroom_id}/students/{student_id}",
    response_model=StudentOut,
)
def get_student(school_id: int, grade_id: int, classroom_id: int,
                student_id: int,
                db: Session = Depends(get_db),
                current_user: models.User = Depends(get_current_user)):

    _check_access(db, current_user, school_id)
    _validate_structure(db, school_id, grade_id, classroom_id)

    student = (
        db.query(models.Student)
        .filter(
            models.Student.id == student_id,
            models.Student.classroom_id == classroom_id,
        )
        .first()
    )

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return student


@router.put(
    "/{school_id}/grades/{grade_id}/classrooms/{classroom_id}/students/{student_id}",
    response_model=StudentOut,
)
def update_student(school_id: int, grade_id: int, classroom_id: int,
                   student_id: int, payload: StudentUpdate,
                   db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):

    _check_access(db, current_user, school_id)
    _validate_structure(db, school_id, grade_id, classroom_id)

    student = (
        db.query(models.Student)
        .filter(models.Student.id == student_id, models.Student.classroom_id == classroom_id)
        .first()
    )

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    data = payload.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return student


@router.delete(
    "/{school_id}/grades/{grade_id}/classrooms/{classroom_id}/students/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_student(school_id: int, grade_id: int, classroom_id: int,
                   student_id: int,
                   db: Session = Depends(get_db),
                   current_user: models.User = Depends(get_current_user)):

    _check_access(db, current_user, school_id)
    _validate_structure(db, school_id, grade_id, classroom_id)

    student = (
        db.query(models.Student)
        .filter(models.Student.id == student_id, models.Student.classroom_id == classroom_id)
        .first()
    )

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.is_active = False
    db.commit()
    return
