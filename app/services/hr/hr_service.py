from sqlalchemy.orm import Session
from app.services.base import BaseService
from app.events import event_bus
from app.events.domain_event import DomainEvent
from app.events.types import HREvents
from app.models import LeaveRequest

class HRService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)

    def create_leave_request(self, school_id: int, staff_id: int, data: dict):
        req = LeaveRequest(
            school_id=school_id,
            staff_id=staff_id,
            reason=data.get("reason"),
            days=data.get("days"),
            status="pending",
        )
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)

        event_bus.publish(DomainEvent(
            event=HREvents.LEAVE_REQUEST_CREATED,
            school_id=school_id,
            user_id=staff_id,
            entity="leave_request",
            entity_id=req.id,
        ))
        return req
