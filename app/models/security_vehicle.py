from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Boolean,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class VehicleAccess(Base):
    """
    Registered vehicle allowed to access school.
    """

    __tablename__ = "vehicle_accesses"

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    plate_number = Column(String(100), nullable=False, index=True)
    owner_name = Column(String(200), nullable=True)
    owner_type = Column(String(50), nullable=True)    # parent / staff / visitor / vendor / other
    vehicle_type = Column(String(100), nullable=True) # car / bus / van / motorcycle

    active = Column(Boolean, nullable=False, server_default="true")

    school = relationship("School")
    logs = relationship(
        "VehicleAccessLog",
        back_populates="vehicle",
        cascade="all, delete-orphan",
    )


class VehicleAccessLog(Base):
    """
    Log of vehicle entering / exiting.
    """

    __tablename__ = "vehicle_access_logs"

    id = Column(Integer, primary_key=True, index=True)

    vehicle_id = Column(
        Integer,
        ForeignKey("vehicle_accesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    security_post_id = Column(
        Integer,
        ForeignKey("security_posts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    direction = Column(String(10), nullable=False)  # in / out
    driver_name = Column(String(200), nullable=True)

    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    vehicle = relationship("VehicleAccess", back_populates="logs")
    school = relationship("School")
    post = relationship("SecurityPost")
