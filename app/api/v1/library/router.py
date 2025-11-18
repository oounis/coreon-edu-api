from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role

from app.services.library.library_service import LibraryService

router = APIRouter(prefix="/library", tags=["Library"])

# Books
@router.post("/books")
def create_book(payload: Dict[str, Any], db: Session = Depends(get_db),
                user=Depends(require_roles(Role.LIBRARIAN, Role.SCHOOL_ADMIN,
                                           Role.SUPER_ADMIN))):
    svc = LibraryService(db)
    return svc.create_book(
        school_id=user.school_id,
        title=payload["title"],
        author=payload["author"],
        isbn=payload["isbn"],
        category=payload["category"],
        meta=payload.get("meta") or {},
        created_by=user.id,
    )

@router.get("/books")
def list_books(db: Session = Depends(get_db),
               user=Depends(require_roles(Role.LIBRARIAN, Role.TEACHER,
                                         Role.SCHOOL_ADMIN, Role.SUPER_ADMIN))):
    svc = LibraryService(db)
    return svc.list_books(school_id=user.school_id)

# Copies
@router.post("/books/{book_id}/copies")
def add_copy(book_id: int, payload: Dict[str, Any],
             db: Session = Depends(get_db),
             user=Depends(require_roles(Role.LIBRARIAN))):
    svc = LibraryService(db)
    return svc.add_copy(
        school_id=user.school_id,
        book_id=book_id,
        code=payload["code"],
        status=payload.get("status", "available"),
        meta=payload.get("meta") or {},
        created_by=user.id,
    )

@router.get("/books/{book_id}/copies")
def list_copies(book_id: int, db: Session = Depends(get_db),
                user=Depends(require_roles(Role.LIBRARIAN, Role.TEACHER))):
    svc = LibraryService(db)
    return svc.list_copies(school_id=user.school_id, book_id=book_id)

# Loans
@router.post("/loans/borrow")
def borrow(payload: Dict[str, Any], db: Session = Depends(get_db),
           user=Depends(require_roles(Role.LIBRARIAN))):
    svc = LibraryService(db)
    return svc.borrow_copy(
        school_id=user.school_id,
        copy_id=payload["copy_id"],
        user_id=payload["user_id"],
        due_date=datetime.fromisoformat(payload["due_date"]),
        created_by=user.id,
    )

@router.post("/loans/{loan_id}/return")
def return_copy(loan_id: int, db: Session = Depends(get_db),
                user=Depends(require_roles(Role.LIBRARIAN))):
    svc = LibraryService(db)
    return svc.return_copy(school_id=user.school_id, loan_id=loan_id,
                           created_by=user.id)

# Reservations
@router.post("/books/{book_id}/reserve")
def reserve(book_id: int, payload: Dict[str, Any],
            db: Session = Depends(get_db),
            user=Depends(require_roles(Role.STUDENT, Role.PARENT, Role.TEACHER))):
    svc = LibraryService(db)
    return svc.reserve_book(
        school_id=user.school_id,
        book_id=book_id,
        user_id=user.id,
        created_by=user.id,
    )

@router.get("/books/{book_id}/reservations")
def reservations(book_id: int, db: Session = Depends(get_db),
                 user=Depends(require_roles(Role.LIBRARIAN, Role.SCHOOL_ADMIN))):
    svc = LibraryService(db)
    return svc.list_reservations(school_id=user.school_id, book_id=book_id)
