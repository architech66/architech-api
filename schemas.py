from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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
    class Config:
        orm_mode = True

class SessionOut(BaseModel):
    id: int
    user_id: int
    ip_address: str
    timestamp: datetime
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
