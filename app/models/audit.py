from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from app.db.session import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    ts = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    actor = Column(String, nullable=False)        # username or system
    action = Column(String, nullable=False)       # e.g., "timetable.slot.create"
    obj_type = Column(String, nullable=True)      # e.g., "TimetableSlot"
    obj_id = Column(String, nullable=True)        # e.g., "123"
    meta = Column(JSON, nullable=True)            # extra info
