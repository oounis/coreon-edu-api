from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app import models
from app.core.security import get_current_user, require_role

router = APIRouter()

# ----------------------
# Schemas
# ----------------------

class ClassroomBase(BaseModel):
    name: str

class ClassroomCreate(ClassroomBase):
    pass

class ClassroomUpdate(BaseModel):
    name: Optional[str] = None

class ClassroomOut(ClassroomBase):
    id: int
    grade_id: int

    class Config:
        orm_mode = True


# ----------------------
# Routes (nested)
#   /api/v1/schools/{school_id}/grades/{grade_id}/classrooms
# ----------------------

@router.post(
    "/{school_id}/grades/{grade_id}/classrooms",
    response_model=ClassroomOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
def create_classroom(
    school_id: int,
    grade_id: int,
    payload: ClassroomCreate,
    db: Session = Depends(get_db),
):
    grade = (
        db.query(models.Grade)
        .filter(
            models.Grade.id == grade_id,
            models.Grade.school_id == school_id,
        )
        .first()
    )
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found for this school")

    exists = (
        db.query(models.Classroom)
        .filter(
            models.Classroom.grade_id == grade_id,
            models.Classroom.name == payload.name,
        )
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Classroom already exists")

    classroom = models.Classroom(name=payload.name, grade_id=grade_id)
    db.add(classroom)
    db.commit()
    db.refresh(classroom)
    return classroom


@router.get(
    "/{school_id}/grades/{grade_id}/classrooms",
    response_model=List[ClassroomOut],
    dependencies=[Depends(require_role("admin"))],
)
def list_classrooms(
    school_id: int,
    grade_id: int,
    db: Session = Depends(get_db),
):
    grade = (
        db.query(models.Grade)
        .filter(
            models.Grade.id == grade_id,
            models.Grade.school_id == school_id,
        )
        .first()
    )
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")

    return (
        db.query(models.Classroom)
        .filter(models.Classroom.grade_id == grade_id)
        .order_by(models.Classroom.id)
        .all()
    )


@router.put(
    "/{school_id}/grades/{grade_id}/classrooms/{classroom_id}",
    response_model=ClassroomOut,
)
def update_classroom(
    school_id: int,
    grade_id: int,
    classroom_id: int,
    payload: ClassroomUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    classroom = (
        db.query(models.Classroom)
        .join(models.Grade, models.Grade.id == models.Classroom.grade_id)
        .filter(
            models.Classroom.id == classroom_id,
            models.Classroom.grade_id == grade_id,
            models.Grade.school_id == school_id,
        )
        .first()
    )
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    if current_user.role != "admin":
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

    data = payload.dict(exclude_unset=True)
    for field, value in data.items():
        if hasattr(classroom, field):
            setattr(classroom, field, value)

    db.commit()
    db.refresh(classroom)
    return classroom


@router.delete(
    "/{school_id}/grades/{grade_id}/classrooms/{classroom_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
def delete_classroom(
    school_id: int,
    grade_id: int,
    classroom_id: int,
    db: Session = Depends(get_db),
):
    classroom = (
        db.query(models.Classroom)
        .join(models.Grade, models.Grade.id == models.Classroom.grade_id)
        .filter(
            models.Classroom.id == classroom_id,
            models.Classroom.grade_id == grade_id,
            models.Grade.school_id == school_id,
        )
        .first()
    )

    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    db.delete(classroom)
    db.commit()
    return
