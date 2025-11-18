from pydantic import BaseModel, EmailStr
from typing import Optional

class TeacherBase(BaseModel):
    name: str
    subject: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_active: bool = True

class TeacherCreate(TeacherBase):
    name: str

class TeacherUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

class TeacherOut(TeacherBase):
    id: int
    classroom_id: Optional[int]

    class Config:
        orm_mode = True
