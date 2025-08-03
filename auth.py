from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from crud import record_session
from security import verify_password, create_access_token
from database import get_db
from models import User
from schemas import Token

router = APIRouter()

def authenticate(db: Session, username: str, password: str):
    user = db.query(User).filter_by(username=username).first()
    if not user or not verify_password(password, user.hashed_pw):
        return None
    return user

@router.post("/token", response_model=Token)
async def login_token(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Bad credentials")
    # record their IP
    ip = request.client.host
    record_session(db, user.id, ip)
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
