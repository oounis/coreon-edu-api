from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    ForeignKey,
    Boolean,
    JSON,
    func,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class HealthProfile(Base):
    """
    Health info for a student:
    - allergies
    - chronic conditions
    - emergency contacts
    """

    __tablename__ = "health_profiles"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    allergies = Column(JSON, nullable=True)
    chronic_conditions = Column(JSON, nullable=True)
    emergency_contacts = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    student = relationship("StudentProfile")


class MedicalVisit(Base):
    """
    Clinic visit log:
    - temperature
    - symptoms
    - treatment given
    """

    __tablename__ = "medical_visits"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    nurse_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    symptoms = Column(String(1000), nullable=True)
    temperature = Column(String(50), nullable=True)
    treatment = Column(String(1000), nullable=True)
    notes = Column(String(2000), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    student = relationship("StudentProfile")
    nurse = relationship("User")


class MedicationRecord(Base):
    """
    Medication administration log.
    """

    __tablename__ = "medication_records"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    nurse_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    medication = Column(String(200), nullable=False)
    dosage = Column(String(200), nullable=True)
    time_given = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    notes = Column(String(1000), nullable=True)

    student = relationship("StudentProfile")
    nurse = relationship("User")


class HealthIncident(Base):
    """
    Serious or reportable incident.
    """

    __tablename__ = "health_incidents"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    nurse_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    description = Column(String(2000), nullable=False)
    severity = Column(String(100), nullable=True)
    action_taken = Column(String(2000), nullable=True)

    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    student = relationship("StudentProfile")
    nurse = relationship("User")
