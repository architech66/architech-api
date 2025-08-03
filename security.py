# security.py
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

import crud, schemas

SECRET_KEY = "your-very-secret-key"     # replace with env var in production
ALGORITHM  = "HS256"
ACCESS_EXPIRE_MIN = 30

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return _pwd_ctx.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_ctx.verify(plain, hashed)

def authenticate_user(db: Session, username: str, password: str):
    user = crud.get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_pw):
        return None
    return user

def create_access_token(username: str, expires_minutes: int = ACCESS_EXPIRE_MIN):
    to_encode = {"sub": username}
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
