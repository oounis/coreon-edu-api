from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.security import get_current_user
from app import models
from .schemas import SubjectCreate, SubjectUpdate, SubjectOut

router = APIRouter()

# ======================
# Helpers
# ======================

def _check_access(db: Session, current_user: models.User, school_id: int):
    """
    Allow:
      - platform admin (role='admin')
      - school admins linked via SchoolAdmin
    """
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


def _validate_grade(db: Session, school_id: int, grade_id: int) -> models.Grade:
    """
    Ensure the grade belongs to the given school.
    """
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
    return grade


# ======================
# Routes
# ======================

@router.post(
    "/schools/{school_id}/grades/{grade_id}/subjects",
    response_model=SubjectOut,
    status_code=status.HTTP_201_CREATED,
)
def create_subject(
    school_id: int,
    grade_id: int,
    payload: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _check_access(db, current_user, school_id)
    _validate_grade(db, school_id, grade_id)

    subject = models.Subject(
        name=payload.name,
        code=payload.code,
        description=payload.description,
        is_active=payload.is_active,
        grade_id=grade_id,
    )

    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


@router.get(
    "/schools/{school_id}/grades/{grade_id}/subjects",
    response_model=List[SubjectOut],
)
def list_subjects(
    school_id: int,
    grade_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _check_access(db, current_user, school_id)
    _validate_grade(db, school_id, grade_id)

    return (
        db.query(models.Subject)
        .filter(models.Subject.grade_id == grade_id)
        .order_by(models.Subject.id)
        .all()
    )


@router.get(
    "/schools/{school_id}/grades/{grade_id}/subjects/{subject_id}",
    response_model=SubjectOut,
)
def get_subject(
    school_id: int,
    grade_id: int,
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _check_access(db, current_user, school_id)
    _validate_grade(db, school_id, grade_id)

    subject = (
        db.query(models.Subject)
        .filter(
            models.Subject.id == subject_id,
            models.Subject.grade_id == grade_id,
        )
        .first()
    )
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    return subject


@router.put(
    "/schools/{school_id}/grades/{grade_id}/subjects/{subject_id}",
    response_model=SubjectOut,
)
def update_subject(
    school_id: int,
    grade_id: int,
    subject_id: int,
    payload: SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _check_access(db, current_user, school_id)
    _validate_grade(db, school_id, grade_id)

    subject = (
        db.query(models.Subject)
        .filter(
            models.Subject.id == subject_id,
            models.Subject.grade_id == grade_id,
        )
        .first()
    )
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(subject, field, value)

    db.commit()
    db.refresh(subject)
    return subject


@router.delete(
    "/schools/{school_id}/grades/{grade_id}/subjects/{subject_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_subject(
    school_id: int,
    grade_id: int,
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _check_access(db, current_user, school_id)
    _validate_grade(db, school_id, grade_id)

    subject = (
        db.query(models.Subject)
        .filter(
            models.Subject.id == subject_id,
            models.Subject.grade_id == grade_id,
        )
        .first()
    )
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    db.delete(subject)
    db.commit()
    return
