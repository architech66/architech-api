import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import *
from schemas import UserCreate, UserOut, SessionOut
from crud import create_user, list_users, delete_user, list_sessions
from auth import router as auth_router

# create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ARCHITECH Auth API")
oauth2 = OAuth2PasswordBearer(tokenUrl="/token")

# mount auth token endpoint
app.include_router(auth_router)

# helper to get current and admin user:
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2)):
    from security import JWTError, jwt, SECRET_KEY, ALGORITHM
    from schemas import TokenData
    from crud import list_users as _list_users
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uname = payload.get("sub")
        if uname is None:
            raise
        data = TokenData(username=uname)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter_by(username=data.username).first()
    if not user or not user.active:
        raise HTTPException(401, "Invalid credentials")
    return user

def get_admin_user(user=Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(403, "Admin privileges required")
    return user

# Admin CRUD endpoints
@app.post("/admin/users", response_model=UserOut, dependencies=[Depends(get_admin_user)])
def admin_create_user(u: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, u)

@app.get("/admin/users", response_model=list[UserOut], dependencies=[Depends(get_admin_user)])
def admin_list_users(db: Session = Depends(get_db)):
    return list_users(db)

@app.delete("/admin/users/{user_id}", response_model=UserOut, dependencies=[Depends(get_admin_user)])
def admin_delete_user(user_id: int, db: Session = Depends(get_db)):
    u = delete_user(db, user_id)
    if not u:
        raise HTTPException(404, "User not found")
    return u

@app.get("/admin/sessions", response_model=list[SessionOut], dependencies=[Depends(get_admin_user)])
def admin_list_sessions(db: Session = Depends(get_db)):
    return list_sessions(db)

@app.get("/admin", response_class=HTMLResponse, dependencies=[Depends(get_admin_user)])
def admin_panel():
    html = open("admin.html", encoding="utf-8").read()
    return HTMLResponse(html)
