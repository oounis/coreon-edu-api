from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app import models
from .schemas import TeacherCreate, TeacherUpdate, TeacherOut

router = APIRouter()

# ======================
# Helpers
# ======================

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


def _validate_classroom(db: Session, school_id: int, classroom_id: int):
    classroom = (
        db.query(models.Classroom)
        .join(models.Grade)
        .filter(
            models.Classroom.id == classroom_id,
            models.Grade.school_id == school_id,
        )
        .first()
    )
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    return classroom


# ======================
# Routes
# ======================

@router.post(
    "/schools/{school_id}/teachers",
    response_model=TeacherOut,
    status_code=status.HTTP_201_CREATED,
)
def create_teacher(
    school_id: int,
    payload: TeacherCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _check_access(db, current_user, school_id)

    teacher = models.Teacher(
        name=payload.name,
        subject=payload.subject,
        email=payload.email,
        phone=payload.phone,
        classroom_id=None,
        is_active=payload.is_active,
    )

    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


@router.get(
    "/schools/{school_id}/teachers",
    response_model=list[TeacherOut],
)
def list_teachers(
    school_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _check_access(db, current_user, school_id)

    return (
        db.query(models.Teacher)
        .join(models.Classroom, isouter=True)
        .join(models.Grade, isouter=True)
        .filter(
            (models.Grade.school_id == school_id) | 
            (models.Teacher.classroom_id == None)
        )
        .all()
    )


@router.put(
    "/schools/{school_id}/teachers/{teacher_id}",
    response_model=TeacherOut,
)
def update_teacher(
    school_id: int,
    teacher_id: int,
    payload: TeacherUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _check_access(db, current_user, school_id)

    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(teacher, key, value)

    db.commit()
    db.refresh(teacher)
    return teacher


@router.delete(
    "/schools/{school_id}/teachers/{teacher_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_teacher(
    school_id: int,
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _check_access(db, current_user, school_id)

    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    db.delete(teacher)
    db.commit()
    return


@router.post(
    "/schools/{school_id}/teachers/{teacher_id}/assign/{classroom_id}",
    response_model=TeacherOut,
)
def assign_teacher(
    school_id: int,
    teacher_id: int,
    classroom_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _check_access(db, current_user, school_id)

    teacher = db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    _validate_classroom(db, school_id, classroom_id)

    teacher.classroom_id = classroom_id
    db.commit()
    db.refresh(teacher)
    return teacher

