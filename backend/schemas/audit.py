from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime
    session_id: Optional[str] = None
    comments: Optional[str] = None

    class Config:
        from_attributes = True