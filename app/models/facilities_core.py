from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    ForeignKey,
    Boolean,
    JSON,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class FacilityRoom(Base):
    """
    Physical room in the school.
    """

    __tablename__ = "facility_rooms"
    __table_args__ = (
        UniqueConstraint("school_id", "name", name="uq_room_name"),
    )

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(200), nullable=False)
    type = Column(String(100), nullable=True)  # lab / classroom / office / hall

    school = relationship("School")


class Asset(Base):
    """
    Asset or equipment belonging to the school.
    """

    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    room_id = Column(
        Integer,
        ForeignKey("facility_rooms.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=True)  # furniture / electronics / etc
    serial_number = Column(String(200), nullable=True)

    room = relationship("FacilityRoom")
    school = relationship("School")


class MaintenanceRequest(Base):
    """
    Maintenance ticket:
    - broken AC
    - electricity issue
    - plumbing
    """

    __tablename__ = "maintenance_requests"

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    room_id = Column(
        Integer,
        ForeignKey("facility_rooms.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    reported_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    description = Column(String(2000), nullable=False)
    category = Column(String(100), nullable=True)  # electrical / cleaning / plumbing
    status = Column(
        String(50),
        nullable=False,
        server_default="pending",
    )  # pending / assigned / in_progress / completed

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    room = relationship("FacilityRoom")
    reporter = relationship("User")


class MaintenanceAssignment(Base):
    """
    Assign maintenance staff to a request.
    """

    __tablename__ = "maintenance_assignments"
    __table_args__ = (
        UniqueConstraint("request_id", "staff_id", name="uq_maintenance_assignment"),
    )

    id = Column(Integer, primary_key=True, index=True)

    request_id = Column(
        Integer,
        ForeignKey("maintenance_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    staff_id = Column(
        Integer,
        ForeignKey("staff_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    request = relationship("MaintenanceRequest")
    staff = relationship("StaffProfile")
