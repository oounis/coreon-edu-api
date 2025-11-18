from sqlalchemy.orm import Session
from app.services.base import BaseService
from app.events import event_bus
from app.events.types import WorkflowEvents
from app.events.domain_event import DomainEvent
from app.models import Request

class WorkflowService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)

    def submit_request(self, user_id: int, school_id: int, data: dict):
        req = Request(
            user_id=user_id,
            school_id=school_id,
            payload=data,
            status="pending",
        )
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)

        event_bus.publish(DomainEvent(
            event=WorkflowEvents.APPROVAL_PENDING,
            user_id=user_id,
            school_id=school_id,
            entity="request",
            entity_id=req.id,
            data={"request_id": req.id},
        ))
        return req
