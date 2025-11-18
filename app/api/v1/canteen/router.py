from typing import Dict, Any
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role
from app.services.canteen.canteen_service import CanteenService

router = APIRouter(prefix="/canteen", tags=["Canteen"])

# Menus
@router.post("/menus")
def create_menu(payload: Dict[str, Any], db: Session = Depends(get_db),
                user=Depends(require_roles(Role.SCHOOL_ADMIN, Role.SUPER_ADMIN))):
    svc = CanteenService(db)
    return svc.create_menu(
        school_id=user.school_id,
        date=payload["date"],
        meta=payload.get("meta") or {},
        created_by=user.id,
    )

@router.get("/menus")
def list_menus(db: Session = Depends(get_db),
               user=Depends(require_roles(Role.TEACHER, Role.PARENT, Role.SCHOOL_ADMIN))):
    svc = CanteenService(db)
    return svc.list_menus(school_id=user.school_id)

# Meals
@router.post("/menus/{menu_id}/meals")
def add_meal(menu_id: int, payload: Dict[str, Any], db: Session = Depends(get_db),
             user=Depends(require_roles(Role.SCHOOL_ADMIN))):
    svc = CanteenService(db)
    return svc.add_meal(
        school_id=user.school_id,
        menu_id=menu_id,
        title=payload["title"],
        price=Decimal(str(payload["price"])),
        category=payload.get("category", "food"),
        meta=payload.get("meta") or {},
        created_by=user.id,
    )

@router.get("/menus/{menu_id}/meals")
def list_meals(menu_id: int, db: Session = Depends(get_db),
               user=Depends(require_roles(Role.TEACHER, Role.PARENT, Role.STUDENT))):
    svc = CanteenService(db)
    return svc.list_meals(school_id=user.school_id, menu_id=menu_id)

# Orders
@router.post("/orders")
def place_order(payload: Dict[str, Any], db: Session = Depends(get_db),
                user=Depends(require_roles(Role.STUDENT, Role.PARENT, Role.TEACHER))):
    svc = CanteenService(db)
    return svc.place_order(
        school_id=user.school_id,
        user_id=user.id,
        meal_id=int(payload["meal_id"]),
        qty=int(payload["qty"]),
        created_by=user.id,
    )

@router.get("/orders/history")
def history(db: Session = Depends(get_db),
            user=Depends(require_roles(Role.STUDENT, Role.PARENT, Role.TEACHER))):
    svc = CanteenService(db)
    return svc.user_history(school_id=user.school_id, user_id=user.id)
