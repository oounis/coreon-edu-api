from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.security import get_current_user
from app.models.school import School, Grade, Classroom

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Schemas ---
class SchoolCreate(BaseModel):
    name: str

class GradeCreate(BaseModel):
    school_id: int
    name: str

class ClassroomCreate(BaseModel):
    grade_id: int
    name: str

# --- Endpoints ---
@router.post("/schools")
def create_school(body: SchoolCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    if db.query(School).filter(School.name == body.name).first():
        raise HTTPException(status_code=400, detail="School already exists")
    s = School(name=body.name)
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"id": s.id, "name": s.name}

@router.post("/grades")
def create_grade(body: GradeCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    school = db.get(School, body.school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    g = Grade(name=body.name, school_id=body.school_id)
    db.add(g)
    db.commit()
    db.refresh(g)
    return {"id": g.id, "name": g.name, "school_id": g.school_id}

@router.post("/classrooms")
def create_classroom(body: ClassroomCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if user["role"] not in ("admin", "staff"):
        raise HTTPException(status_code=403, detail="Admins/Staff only")
    grade = db.get(Grade, body.grade_id)
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    c = Classroom(name=body.name, grade_id=body.grade_id)
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"id": c.id, "name": c.name, "grade_id": c.grade_id}

@router.get("/schools/{school_id}/classes")
def list_classes(school_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # list classrooms under a school (via grades)
    q = (
        db.query(Classroom, Grade)
        .join(Grade, Classroom.grade_id == Grade.id)
        .filter(Grade.school_id == school_id)
        .all()
    )
    return [{"classroom_id": c.Classroom.id, "classroom": c.Classroom.name, "grade": c.Grade.name} for c in q]
