from datetime import datetime

from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from app.db.session import Base


class BehaviorIncident(Base):
    __tablename__ = "behavior_incidents"

    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, index=True, nullable=False)
    student_id = Column(Integer, index=True, nullable=False)
    type = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    severity = Column(String(50), nullable=True)
    meta = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=True)


class BehaviorActionPlan(Base):
    __tablename__ = "behavior_action_plans"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("behavior_incidents.id"), nullable=False)
    steps = Column(JSON, default=list)
    status = Column(String(50), default="open")
    meta = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
