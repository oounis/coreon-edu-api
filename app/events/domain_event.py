from typing import Any, Dict, Optional
from datetime import datetime

class DomainEvent:
    """
    Standard payload shape for ALL events in system.
    """

    def __init__(
        self,
        *,
        event: str,
        school_id: Optional[int] = None,
        user_id: Optional[int] = None,
        entity: Optional[str] = None,
        entity_id: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None,
        ip: Optional[str] = None,
    ):
        self.timestamp = datetime.utcnow()
        self.event = event
        self.school_id = school_id
        self.user_id = user_id
        self.entity = entity
        self.entity_id = entity_id
        self.data = data or {}
        self.ip = ip

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event": self.event,
            "school_id": self.school_id,
            "user_id": self.user_id,
            "entity": self.entity,
            "entity_id": self.entity_id,
            "data": self.data,
            "ip": self.ip,
            "timestamp": self.timestamp.isoformat(),
        }
