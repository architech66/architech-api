from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String, unique=True, index=True, nullable=False)
    hashed_pw     = Column(String, nullable=False)
    is_admin      = Column(Boolean, default=False)
    active        = Column(Boolean, default=True)
    twilio_sid    = Column(String, nullable=True)
    twilio_token  = Column(String, nullable=True)
    sessions      = relationship("Session", back_populates="user")

class Session(Base):
    __tablename__ = "sessions"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    ip_address = Column(String, nullable=False)
    timestamp  = Column(DateTime, default=datetime.utcnow)
    user       = relationship("User", back_populates="sessions")
