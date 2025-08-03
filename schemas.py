# schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    password: str
    is_admin: bool = False
    twilio_sid: Optional[str] = None
    twilio_token: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool
    active: bool
    twilio_sid: Optional[str]
    twilio_token: Optional[str]

    model_config = { "from_attributes": True }

class SessionOut(BaseModel):
    id: int
    user_id: int
    ip_address: str
    device_model: Optional[str]
    os_info: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime

    model_config = { "from_attributes": True }

class APIKeyCreate(BaseModel):
    user_id: int
    scopes: List[str]
    usage_quota: Optional[int] = None

class APIKeyOut(BaseModel):
    id: int
    user_id: int
    key: str
    scopes: List[str]
    usage_count: int
    usage_quota: Optional[int]
    created_at: datetime
    revoked: bool

    model_config = { "from_attributes": True }

class Token(BaseModel):
    access_token: str
    token_type: str
