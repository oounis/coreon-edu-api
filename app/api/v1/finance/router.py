from fastapi import APIRouter
router = APIRouter()

@router.get("/summary")
def finance_summary():
    return {"fees_due": 0, "paid": 0}
