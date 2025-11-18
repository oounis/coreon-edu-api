from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime

from sqlalchemy.orm import Session
from app.models import (
    LibraryBook,
    LibraryCopy,
    LibraryLoan,
    LibraryReservation,
)
from app.services.notification_service import NotificationService


class LibraryService:
    """
    Library Management:
    - Books & copies
    - Loans (borrow/return)
    - Reservations (queue)
    - Fines (late fees)
    """

    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationService(db)

    # ------------------
    # Books
    # ------------------
    def create_book(self, *, school_id: int, title: str, author: str,
                    isbn: str, category: str, meta: Dict[str, Any],
                    created_by: int):
        book = LibraryBook(
            school_id=school_id,
            title=title,
            author=author,
            isbn=isbn,
            category=category,
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return {"book": book}

    def list_books(self, *, school_id: int):
        items = self.db.query(LibraryBook).filter(
            LibraryBook.school_id == school_id
        ).all()
        return {"books": items}

    # ------------------
    # Copies
    # ------------------
    def add_copy(self, *, school_id: int, book_id: int, code: str,
                 status: str = "available", meta: Dict[str, Any] = None,
                 created_by: int = None):
        copy = LibraryCopy(
            school_id=school_id,
            book_id=book_id,
            code=code,
            status=status,
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(copy)
        self.db.commit()
        self.db.refresh(copy)
        return {"copy": copy}

    def list_copies(self, *, school_id: int, book_id: int):
        items = self.db.query(LibraryCopy).filter(
            LibraryCopy.school_id == school_id,
            LibraryCopy.book_id == book_id,
        ).all()
        return {"copies": items}

    # ------------------
    # Loans
    # ------------------
    def borrow_copy(self, *, school_id: int, copy_id: int, user_id: int,
                    due_date: datetime, created_by: int):
        copy = self.db.query(LibraryCopy).filter(
            LibraryCopy.id == copy_id,
            LibraryCopy.school_id == school_id,
        ).first()
        if not copy:
            raise ValueError("Copy not found")

        if copy.status != "available":
            raise ValueError("Copy is not available")

        loan = LibraryLoan(
            school_id=school_id,
            copy_id=copy_id,
            user_id=user_id,
            borrowed_at=datetime.utcnow(),
            due_date=due_date,
            status="ongoing",
            created_by=created_by,
        )
        copy.status = "borrowed"

        self.db.add(loan)
        self.db.commit()
        self.db.refresh(loan)

        return {"loan": loan}

    def return_copy(self, *, school_id: int, loan_id: int, created_by: int):
        loan = self.db.query(LibraryLoan).filter(
            LibraryLoan.id == loan_id,
            LibraryLoan.school_id == school_id,
        ).first()
        if not loan:
            raise ValueError("Loan not found")

        copy = self.db.query(LibraryCopy).filter(
            LibraryCopy.id == loan.copy_id
        ).first()

        loan.status = "returned"
        loan.returned_at = datetime.utcnow()
        copy.status = "available"

        # late fee
        fee = 0
        if loan.due_date < loan.returned_at:
            fee = (loan.returned_at - loan.due_date).days * 1  # 1 USD per day

        self.db.commit()
        return {"loan": loan, "late_fee": fee}

    # ------------------
    # Reservations
    # ------------------
    def reserve_book(self, *, school_id: int, book_id: int,
                      user_id: int, created_by: int):
        r = LibraryReservation(
            school_id=school_id,
            book_id=book_id,
            user_id=user_id,
            status="queued",
            created_by=created_by,
            requested_at=datetime.utcnow(),
        )
        self.db.add(r)
        self.db.commit()
        self.db.refresh(r)
        return {"reservation": r}

    def list_reservations(self, *, school_id: int, book_id: int):
        items = self.db.query(LibraryReservation).filter(
            LibraryReservation.school_id == school_id,
            LibraryReservation.book_id == book_id,
        ).all()
        return {"reservations": items}
