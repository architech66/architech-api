# main.py
from typing import List
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse

from database import engine, Base
from auth import authenticate_user, create_access_token, get_admin_user, get_db
from crud import create_user, list_users, delete_user, list_sessions
from schemas import UserCreate, UserOut, SessionOut, Token
from sqlalchemy.orm import Session

# create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ARCHITECH Auth API")

# serve your admin.html and related assets from /static
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request: Request = None
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    # record the session with IP
    ip = request.client.host if request else "unknown"
    record_session(db, user.id, ip)
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post(
    "/admin/users",
    response_model=UserOut,
    dependencies=[Depends(get_admin_user)]
)
def admin_create_user(u: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, u)


@app.get(
    "/admin/users",
    response_model=List[UserOut],
    dependencies=[Depends(get_admin_user)]
)
def admin_list_users(db: Session = Depends(get_db)):
    return list_users(db)


@app.delete(
    "/admin/users/{user_id}",
    response_model=UserOut,
    dependencies=[Depends(get_admin_user)]
)
def admin_delete_user(user_id: int, db: Session = Depends(get_db)):
    user = delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get(
    "/admin/sessions",
    response_model=List[SessionOut],
    dependencies=[Depends(get_admin_user)]
)
def admin_list_sessions(db: Session = Depends(get_db)):
    return list_sessions(db)


@app.get(
    "/admin",
    response_class=HTMLResponse,
    dependencies=[Depends(get_admin_user)]
)
def admin_panel():
    # now looking in static/admin.html
    with open("static/admin.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())
