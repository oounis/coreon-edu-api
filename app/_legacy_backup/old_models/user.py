from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)

    # MUST MATCH security.py JWT logic
    password_hash = Column(String, nullable=False)

    role = Column(String, nullable=False, default="staff")  # admin, teacher, staff, parent
    is_active = Column(Boolean, default=True)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"
