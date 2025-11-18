from typing import Dict, Any, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.rbac.permission_checker import require_roles
from app.core.rbac.role_enums import Role
from app.services.communication.communication_service import CommunicationService

router = APIRouter(prefix="/communication", tags=["Communication"])


# -------------------------------
# Internal Messaging
# -------------------------------
@router.post("/messages/send")
def send_message(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(
        require_roles(
            Role.TEACHER,
            Role.SCHOOL_ADMIN,
            Role.SUPER_ADMIN,
            Role.HR,
        )
    ),
):
    svc = CommunicationService(db)
    return svc.send_message(
        school_id=user.school_id,
        sender_id=user.id,
        recipients=payload["recipients"],
        subject=payload["subject"],
        content=payload["content"],
        meta=payload.get("meta") or {},
    )


# -------------------------------
# Announcements
# -------------------------------
@router.post("/announcements")
def create_announcement(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    user=Depends(
        require_roles(
            Role.SCHOOL_ADMIN,
            Role.SUPER_ADMIN,
            Role.PRINCIPAL,
        )
    ),
):
    svc = CommunicationService(db)
    return svc.create_announcement(
        school_id=user.school_id,
        title=payload["title"],
        body=payload["body"],
        audience=payload["audience"],
        attachments=payload.get("attachments") or [],
        meta=payload.get("meta") or {},
        created_by=user.id,
    )


@router.get("/announcements")
def list_announcements(
    db: Session = Depends(get_db),
    user=Depends(
        require_roles(
            Role.TEACHER,
            Role.SCHOOL_ADMIN,
            Role.SUPER_ADMIN,
            Role.PARENT,
            Role.STUDENT,
            Role.PRINCIPAL,
        )
    ),
):
    svc = CommunicationService(db)
    return svc.list_announcements(school_id=user.school_id)

