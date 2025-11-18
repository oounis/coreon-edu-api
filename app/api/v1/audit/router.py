from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.db.session import SessionLocal
from app.core.security import require_roles
from app.models.audit import AuditLog

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class AuditOut:
    # pydantic-free lightweight dict projector to avoid importing BaseModel
    def __init__(self, row: AuditLog):
        self.id = row.id
        self.ts = row.ts
        self.actor = row.actor
        self.action = row.action
        self.obj_type = row.obj_type
        self.obj_id = row.obj_id
        self.meta = row.meta

@router.get("/logs", dependencies=[Depends(require_roles("admin"))])
def list_logs(
    db: Session = Depends(get_db),
    actor: Optional[str] = None,
    action_like: Optional[str] = Query(default=None, description="substring match"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
) -> List[dict]:
    stmt = select(AuditLog).order_by(desc(AuditLog.id)).offset(offset).limit(limit)
    if actor:
        stmt = select(AuditLog).where(AuditLog.actor == actor).order_by(desc(AuditLog.id)).offset(offset).limit(limit)
    if action_like:
        # simple LIKE, safe enough for ops viewing
        stmt = select(AuditLog).where(AuditLog.action.ilike(f"%{action_like}%")).order_by(desc(AuditLog.id)).offset(offset).limit(limit)

    rows = list(db.execute(stmt).scalars())
    return [AuditOut(r).__dict__ for r in rows]
