from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user
from app.services.finance.billing_service import BillingService

router = APIRouter(prefix="/finance", tags=["Finance"])

@router.post("/invoice")
def create_invoice(data: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = BillingService(db)
    return svc.create_invoice(
        school_id=user.school_id,
        student_id=data["student_id"],
        amount=data["amount"]
    )
