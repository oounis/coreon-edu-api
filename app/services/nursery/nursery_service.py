from sqlalchemy.orm import Session
from app.services.base import BaseService
from app.events import event_bus
from app.events.domain_event import DomainEvent
from app.events.types import NurseryEvents
from app.models import NurseryDailyReport

class NurseryService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)

    def submit_daily_report(self, school_id: int, staff_id: int, student_id: int, notes: str):
        rpt = NurseryDailyReport(
            school_id=school_id,
            student_id=student_id,
            reporter_id=staff_id,
            notes=notes,
        )
        self.db.add(rpt)
        self.db.commit()
        self.db.refresh(rpt)

        event_bus.publish(DomainEvent(
            event=NurseryEvents.DAILY_REPORT_SUBMITTED,
            school_id=school_id,
            user_id=staff_id,
            entity="nursery_daily_report",
            entity_id=rpt.id,
        ))
        return rpt
