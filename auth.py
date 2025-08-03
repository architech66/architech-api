from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from security import authenticate_user, create_access_token
from crud import record_session
from schemas import Token

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_token(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request: Request
):
    user = authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Bad credentials")
    # record the IP
    ip = request.client.host
    record_session(db, user.id, ip)
    access = create_access_token({"sub": user.username})
    return {"access_token": access, "token_type": "bearer"}
