from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user
from app.services.workflow.workflow_service import WorkflowService

router = APIRouter(prefix="/workflow", tags=["Workflow"])

@router.post("/submit")
def submit_request(payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    svc = WorkflowService(db)
    return svc.submit_request(
        user_id=user.id,
        school_id=user.school_id,
        data=payload
    )
