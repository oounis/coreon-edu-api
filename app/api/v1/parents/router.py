from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app import models
from .schemas import ParentCreate, ParentUpdate, ParentOut

router = APIRouter()


# GET /api/v1/schools/{school_id}/parents
@router.get("/", response_model=List[ParentOut])
def list_parents(school_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Parent)
        .filter(models.Parent.school_id == school_id)
        .order_by(models.Parent.last_name, models.Parent.first_name)
        .all()
    )


# POST /api/v1/schools/{school_id}/parents
@router.post("/", response_model=ParentOut, status_code=status.HTTP_201_CREATED)
def create_parent(
    school_id: int,
    data: ParentCreate,
    db: Session = Depends(get_db),
):
    # ensure email is unique
    existing = db.query(models.Parent).filter(models.Parent.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parent with this email already exists",
        )

    obj = models.Parent(
        school_id=school_id,
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone=data.phone,
        is_active=data.is_active,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# PUT /api/v1/schools/{school_id}/parents/{parent_id}
@router.put("/{parent_id}", response_model=ParentOut)
def update_parent(
    school_id: int,
    parent_id: int,
    data: ParentUpdate,
    db: Session = Depends(get_db),
):
    obj = (
        db.query(models.Parent)
        .filter(
            models.Parent.id == parent_id,
            models.Parent.school_id == school_id,
        )
        .first()
    )
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent not found")

    if data.first_name is not None:
        obj.first_name = data.first_name
    if data.last_name is not None:
        obj.last_name = data.last_name
    if data.phone is not None:
        obj.phone = data.phone
    if data.is_active is not None:
        obj.is_active = data.is_active

    db.commit()
    db.refresh(obj)
    return obj


# DELETE /api/v1/schools/{school_id}/parents/{parent_id}
@router.delete("/{parent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_parent(
    school_id: int,
    parent_id: int,
    db: Session = Depends(get_db),
):
    obj = (
        db.query(models.Parent)
        .filter(
            models.Parent.id == parent_id,
            models.Parent.school_id == school_id,
        )
        .first()
    )
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent not found")

    db.delete(obj)
    db.commit()
    return
