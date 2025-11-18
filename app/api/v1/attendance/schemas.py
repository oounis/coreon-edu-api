from datetime import date, datetime
from typing import List, Optional, Literal

from pydantic import BaseModel


class AttendanceRecordBase(BaseModel):
    student_id: int
    status: Literal["present", "absent", "late"]
    notes: Optional[str] = None


class AttendanceBulkCreate(BaseModel):
    date: date
    records: List[AttendanceRecordBase]


class AttendanceOut(BaseModel):
    id: int
    date: date
    classroom_id: int
    student_id: int
    status: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
