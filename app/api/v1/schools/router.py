from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app import models
from app.core.security import get_current_user, require_role

router = APIRouter()

# ======================
# Pydantic Schemas
# ======================

class SchoolBase(BaseModel):
    name: str
    code: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    is_active: bool = True

class SchoolCreate(SchoolBase):
    name: str

class SchoolUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    is_active: Optional[bool] = None

class SchoolOut(SchoolBase):
    id: int

    class Config:
        orm_mode = True

class SchoolAdminCreate(BaseModel):
    user_id: int

# ======================
# Helper: per-school RBAC
# ======================

def _ensure_can_manage_school(db: Session, current_user: models.User, school_id: int) -> None:
    """Allow:
    - global admin (role == "admin")
    - OR school_admin for that specific school
    """
    role = getattr(current_user, "role", None)

    if role == "admin":
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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to manage this school",
        )

# ======================
# Routes
# ======================

@router.post(
    "/",
    response_model=SchoolOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
def create_school(payload: SchoolCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(models.School)
        .filter(
            (models.School.name == payload.name)
            | (models.School.code == payload.code)
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="School with this name or code already exists",
        )

    school = models.School(
        name=payload.name,
        code=payload.code,
        city=payload.city,
        country=payload.country,
        is_active=payload.is_active,
    )

    db.add(school)
    db.commit()
    db.refresh(school)
    return school

@router.get(
    "/",
    response_model=List[SchoolOut],
    dependencies=[Depends(require_role("admin"))],
)
def list_schools(db: Session = Depends(get_db)):
    return db.query(models.School).order_by(models.School.id).all()

@router.get(
    "/{school_id}",
    response_model=SchoolOut,
)
def get_school(
    school_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    school = db.query(models.School).filter(models.School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="School not found")

    _ensure_can_manage_school(db, current_user, school_id)
    return school

@router.put(
    "/{school_id}",
    response_model=SchoolOut,
)
def update_school(
    school_id: int,
    payload: SchoolUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    school = db.query(models.School).filter(models.School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="School not found")

    _ensure_can_manage_school(db, current_user, school_id)

    data = payload.dict(exclude_unset=True)

    # SAFE FIELD UPDATE
    for field, value in data.items():
        if hasattr(school, field):
            setattr(school, field, value)

    db.add(school)
    db.commit()
    db.refresh(school)
    return school

@router.delete(
    "/{school_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
def delete_school(
    school_id: int,
    db: Session = Depends(get_db),
):
    school = db.query(models.School).filter(models.School.id == school_id).first()
    if not school:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="School not found")

    db.delete(school)
    db.commit()
    return
