from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class Bus(Base):
    __tablename__ = "buses"

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    plate_number = Column(String(100), nullable=False, unique=True)
    capacity = Column(Integer, nullable=True)
    active = Column(Boolean, nullable=False, server_default="true")

    school = relationship("School")


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(200), nullable=False)
    phone = Column(String(100), nullable=True)
    license_number = Column(String(200), nullable=True)
    active = Column(Boolean, nullable=False, server_default="true")

    school = relationship("School")


class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)

    school_id = Column(
        Integer,
        ForeignKey("schools.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(200), nullable=False)
    active = Column(Boolean, nullable=False, server_default="true")

    school = relationship("School")
    stops = relationship("RouteStop", back_populates="route", cascade="all, delete-orphan")


class RouteStop(Base):
    __tablename__ = "route_stops"
    __table_args__ = (
        UniqueConstraint("route_id", "order", name="uq_route_stop_order"),
    )

    id = Column(Integer, primary_key=True, index=True)

    route_id = Column(
        Integer,
        ForeignKey("routes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    order = Column(Integer, nullable=False)
    name = Column(String(200), nullable=False)
    latitude = Column(String(100), nullable=True)
    longitude = Column(String(100), nullable=True)

    route = relationship("Route", back_populates="stops")


class BusAssignment(Base):
    """
    Which driver + bus is assigned to which route.
    """

    __tablename__ = "bus_assignments"
    __table_args__ = (
        UniqueConstraint("bus_id", "route_id", name="uq_bus_route"),
    )

    id = Column(Integer, primary_key=True, index=True)

    bus_id = Column(
        Integer,
        ForeignKey("buses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    driver_id = Column(
        Integer,
        ForeignKey("drivers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    route_id = Column(
        Integer,
        ForeignKey("routes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class TransportSubscription(Base):
    """
    Student subscribed to transport.
    """

    __tablename__ = "transport_subscriptions"
    __table_args__ = (
        UniqueConstraint("student_id", "route_id", name="uq_student_route"),
    )

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    route_id = Column(
        Integer,
        ForeignKey("routes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    stop_id = Column(
        Integer,
        ForeignKey("route_stops.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    active = Column(Boolean, nullable=False, server_default="true")


class BusAttendance(Base):
    """
    Attendance on bus for pickup/dropoff.
    """

    __tablename__ = "bus_attendance"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    route_id = Column(
        Integer,
        ForeignKey("routes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    stop_id = Column(
        Integer,
        ForeignKey("route_stops.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    direction = Column(String(50), nullable=False)  # pickup/dropoff
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
