from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from app.db.session import Base

class SchoolAdmin(Base):
    __tablename__ = "school_admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "school_id", name="uniq_user_school_admin"),
    )
