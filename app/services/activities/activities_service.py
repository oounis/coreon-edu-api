from sqlalchemy.orm import Session
from app.services.base import BaseService
from app.events import event_bus
from app.events.domain_event import DomainEvent
from app.events.types import ActivityEvents
from app.models import ActivityEvent

class ActivitiesService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)

    def create_club_event(self, club_id: int, school_id: int, data: dict):
        evt = ActivityEvent(
            club_id=club_id,
            title=data["title"],
            description=data.get("description"),
            date=data["date"],
        )
        self.db.add(evt)
        self.db.commit()
        self.db.refresh(evt)

        event_bus.publish(DomainEvent(
            event=ActivityEvents.CLUB_EVENT_CREATED,
            school_id=school_id,
            entity="activity_event",
            entity_id=evt.id,
            data={"event_id": evt.id},
        ))
        return evt
