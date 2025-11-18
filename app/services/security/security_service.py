from sqlalchemy.orm import Session
from app.services.base import BaseService
from app.events import event_bus
from app.events.domain_event import DomainEvent
from app.events.types import SecurityEvents
from app.models import SecurityIncident

class SecurityService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)

    def report_incident(self, school_id: int, reporter_id: int, input_data: dict):
        inc = SecurityIncident(
            school_id=school_id,
            reported_by_id=reporter_id,
            title=input_data["title"],
            type=input_data.get("type"),
            description=input_data.get("description"),
        )
        self.db.add(inc)
        self.db.commit()
        self.db.refresh(inc)

        event_bus.publish(DomainEvent(
            event=SecurityEvents.INCIDENT_REPORTED,
            school_id=school_id,
            user_id=reporter_id,
            entity="security_incident",
            entity_id=inc.id,
            data={"incident_id": inc.id},
        ))
        return inc
