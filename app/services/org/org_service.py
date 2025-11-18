from sqlalchemy.orm import Session
from app.services.base import BaseService

class OrgService(BaseService):
    def __init__(self, db: Session):
        super().__init__(db)

    # Placeholder methods to be implemented later
    # def create_school(...): ...
    # def create_department(...): ...
