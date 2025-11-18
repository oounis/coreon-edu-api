from pydantic import BaseModel
from typing import Optional

class GradeBase(BaseModel):
    name: str

class GradeCreate(GradeBase):
    pass

class GradeUpdate(BaseModel):
    name: Optional[str] = None

class GradeOut(GradeBase):
    id: int
    school_id: int

    class Config:
        from_attributes = True
