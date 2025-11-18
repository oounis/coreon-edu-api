from pydantic import BaseModel
from typing import Optional


class SubjectBase(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True


class SubjectCreate(SubjectBase):
    name: str


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class SubjectOut(SubjectBase):
    id: int
    grade_id: int

    class Config:
        orm_mode = True
