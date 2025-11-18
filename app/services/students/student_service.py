from sqlalchemy.orm import Session
from app.services.base import BaseService

class StudentService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)

    # Placeholder methods to be implemented later
    # def enroll_student(...): ...
    # def promote_student(...): ...
