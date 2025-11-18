from pydantic import BaseModel, EmailStr
from typing import Optional


class ParentBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    is_active: bool = True


class ParentCreate(ParentBase):
    pass


class ParentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class ParentOut(ParentBase):
    id: int
    school_id: int

    class Config:
        from_attributes = True
