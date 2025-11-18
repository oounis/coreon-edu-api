from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app import models
from .schemas import GradeCreate, GradeUpdate, GradeOut

router = APIRouter()

# GET /api/v1/schools/{school_id}/grades
@router.get("/", response_model=List[GradeOut])
def list_grades(school_id: int, db: Session = Depends(get_db)):
    return db.query(models.Grade).filter(models.Grade.school_id == school_id).all()

# POST /api/v1/schools/{school_id}/grades
@router.post("/", response_model=GradeOut, status_code=201)
def create_grade(school_id: int, grade: GradeCreate, db: Session = Depends(get_db)):
    obj = models.Grade(name=grade.name, school_id=school_id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

# PUT /api/v1/schools/{school_id}/grades/{grade_id}
@router.put("/{grade_id}", response_model=GradeOut)
def update_grade(school_id: int, grade_id: int, data: GradeUpdate, db: Session = Depends(get_db)):
    obj = db.query(models.Grade).filter_by(id=grade_id, school_id=school_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Grade not found")

    if data.name:
        obj.name = data.name

    db.commit()
    db.refresh(obj)
    return obj

# DELETE /api/v1/schools/{school_id}/grades/{grade_id}
@router.delete("/{grade_id}", status_code=204)
def delete_grade(school_id: int, grade_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.Grade).filter_by(id=grade_id, school_id=school_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Grade not found")

    db.delete(obj)
    db.commit()
    return
