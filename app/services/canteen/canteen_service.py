from __future__ import annotations
from typing import Dict, Any, Optional, List
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import (
    CanteenMenu,
    CanteenMeal,
    CanteenOrder,
    CanteenTransaction,
)
from app.services.notification_service import NotificationService


class CanteenService:
    """
    Canteen management:
    - Daily menus
    - Meals
    - Student/Staff meal orders
    - Wallet / transactions
    """

    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationService(db)

    # ------------------
    # Menu
    # ------------------
    def create_menu(self, *, school_id: int, date: str, meta: Dict[str, Any], created_by: int):
        menu = CanteenMenu(
            school_id=school_id,
            date=date,
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(menu)
        self.db.commit()
        self.db.refresh(menu)
        return {"menu": menu}

    def list_menus(self, *, school_id: int):
        items = self.db.query(CanteenMenu).filter(
            CanteenMenu.school_id == school_id
        ).order_by(CanteenMenu.date.desc()).all()
        return {"menus": items}

    # ------------------
    # Meals
    # ------------------
    def add_meal(self, *, school_id: int, menu_id: int, title: str,
                 price: Decimal, category: str, meta: Dict[str, Any], created_by: int):
        meal = CanteenMeal(
            school_id=school_id,
            menu_id=menu_id,
            title=title,
            price=price,
            category=category,
            meta=meta or {},
            created_by=created_by,
        )
        self.db.add(meal)
        self.db.commit()
        self.db.refresh(meal)
        return {"meal": meal}

    def list_meals(self, *, school_id: int, menu_id: int):
        items = self.db.query(CanteenMeal).filter(
            CanteenMeal.school_id == school_id,
            CanteenMeal.menu_id == menu_id,
        ).all()
        return {"meals": items}

    # ------------------
    # Orders
    # ------------------
    def place_order(self, *, school_id: int, user_id: int, meal_id: int,
                    qty: int, created_by: int):
        meal = self.db.query(CanteenMeal).filter(
            CanteenMeal.id == meal_id,
            CanteenMeal.school_id == school_id,
        ).first()
        if not meal:
            raise ValueError("Meal not found")

        total = meal.price * qty

        order = CanteenOrder(
            school_id=school_id,
            meal_id=meal_id,
            user_id=user_id,
            qty=qty,
            total=total,
            created_at=datetime.utcnow(),
            created_by=created_by,
        )
        self.db.add(order)

        txn = CanteenTransaction(
            school_id=school_id,
            user_id=user_id,
            amount=total,
            direction="debit",
            reference=f"canteen-order-{order.id}",
            meta={"meal_id": meal_id, "qty": qty},
            created_by=created_by,
        )
        self.db.add(txn)

        self.db.commit()
        self.db.refresh(order)
        self.db.refresh(txn)

        return {"order": order, "transaction": txn}

    def user_history(self, *, school_id: int, user_id: int):
        orders = self.db.query(CanteenOrder).filter(
            CanteenOrder.school_id == school_id,
            CanteenOrder.user_id == user_id,
        ).all()
        return {"orders": orders}
