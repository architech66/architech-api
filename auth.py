# auth.py
import os
from datetime import datetime, timedelta
from typing import Generator

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from database import Session as SessionLocal
from crud import get_user_by_username  # see step 2
from schemas import Token

# load these from env in production!
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_TO_A_RANDOM_32BYTE_HEX")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_pw):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = (datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub: str | None = payload.get("sub")
        if sub is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
        return sub
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    username = decode_token(token)
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user


def get_admin_user(current_user=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not enough permissions")
    return current_user
