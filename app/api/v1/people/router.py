from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.security import get_current_user
from app.models.school import Teacher, Student, Parent, Classroom, parent_student

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Schemas ---
class TeacherCreate(BaseModel):
    full_name: str
    classroom_id: int | None = None

class StudentCreate(BaseModel):
    full_name: str
    classroom_id: int

class ParentCreate(BaseModel):
    full_name: str
    phone: str | None = None

class LinkParentStudent(BaseModel):
    parent_id: int
    student_id: int

# --- Endpoints ---
@router.post("/teachers")
def create_teacher(body: TeacherCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user["role"] not in ("admin", "staff"):
        raise HTTPException(status_code=403, detail="Admins/Staff only")
    if body.classroom_id:
        if not db.get(Classroom, body.classroom_id):
            raise HTTPException(status_code=404, detail="Classroom not found")
    t = Teacher(full_name=body.full_name, classroom_id=body.classroom_id)
    db.add(t)
    db.commit()
    db.refresh(t)
    return {"id": t.id, "full_name": t.full_name, "classroom_id": t.classroom_id}

@router.post("/students")
def create_student(body: StudentCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user["role"] not in ("admin", "staff"):
        raise HTTPException(status_code=403, detail="Admins/Staff only")
    if not db.get(Classroom, body.classroom_id):
        raise HTTPException(status_code=404, detail="Classroom not found")
    s = Student(full_name=body.full_name, classroom_id=body.classroom_id)
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"id": s.id, "full_name": s.full_name, "classroom_id": s.classroom_id}

@router.post("/parents")
def create_parent(body: ParentCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user["role"] not in ("admin", "staff"):
        raise HTTPException(status_code=403, detail="Admins/Staff only")
    p = Parent(full_name=body.full_name, phone=body.phone)
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"id": p.id, "full_name": p.full_name, "phone": p.phone}

@router.post("/link-parent-student")
def link_parent_student(body: LinkParentStudent, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user["role"] not in ("admin", "staff"):
        raise HTTPException(status_code=403, detail="Admins/Staff only")
    parent = db.get(Parent, body.parent_id)
    student = db.get(Student, body.student_id)
    if not parent or not student:
        raise HTTPException(status_code=404, detail="Parent or Student not found")
    parent.students.append(student)
    db.commit()
    return {"ok": True, "parent_id": parent.id, "student_id": student.id}

@router.get("/students/{student_id}/profile")
def student_profile(student_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    s = db.get(Student, student_id)
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    c = s.classroom
    g = c.grade if c else None
    sch = g.school if g else None
    return {
        "student": {"id": s.id, "name": s.full_name},
        "classroom": {"id": c.id, "name": c.name} if c else None,
        "grade": {"id": g.id, "name": g.name} if g else None,
        "school": {"id": sch.id, "name": sch.name} if sch else None,
        "parents": [{"id": p.id, "name": p.full_name, "phone": p.phone} for p in s.parents],
    }
