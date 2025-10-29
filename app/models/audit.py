from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AuditLog(BaseModel):
    event_type: str  # login, logout, failed_login, password_change, etc.
    username: str
    ip_address: str
    timestamp: datetime = datetime.utcnow()
    details: Optional[str] = None
    area: Optional[str] = None
    role: Optional[str] = None
    status: str  # success, failure, warning
    user_agent: Optional[str] = None
    session_id: Optional[str] = None