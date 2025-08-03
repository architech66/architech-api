from pydantic import BaseModel
from datetime import datetime

class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool
    active: bool
    class Config:
        from_attributes = True

class SessionOut(BaseModel):
    id: int
    user_id: int
    ip_address: str
    user_agent: str | None
    timestamp: datetime
    class Config:
        from_attributes = True

class ApiKeyOut(BaseModel):
    id: int
    user_id: int
    key: str
    usage_count: int
    revoked: bool
    class Config:
        from_attributes = True
