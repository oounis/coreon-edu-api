from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Numeric
from app.db.session import Base

class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    contact_person = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    meta = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=True)

class RFQ(Base):
    __tablename__ = "rfq"
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, index=True, nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    title = Column(String(255), nullable=False)
    status = Column(String(50), default="draft")
    meta = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=True)

class Quotation(Base):
    __tablename__ = "quotations"
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, index=True, nullable=False)
    rfq_id = Column(Integer, ForeignKey("rfq.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=True)
    file_url = Column(String(255), nullable=True)
    status = Column(String(50), default="pending")
    meta = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=True)
    created_by = Column(Integer, nullable=True)
