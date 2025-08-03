# main.py
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import HTMLResponse
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from auth import authenticate_user, create_access_token, get_admin_user
from crud import create_user, list_users, delete_user, list_sessions, record_session
from schemas import UserCreate, UserOut, SessionOut, Token

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ARCHITECH Auth API")

# --- Dependency: yield a DB session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1) Login & issue token (also record IP)
@app.post("/token", response_model=Token)
async def login_token(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Bad credentials")
    record_session(db, user.id, request.client.host)
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# 2) Admin: create user
@app.post(
    "/admin/users",
    response_model=UserOut,
    dependencies=[Depends(get_admin_user)],
)
def admin_create_user(u: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, u)

# 3) Admin: list users
@app.get(
    "/admin/users",
    response_model=list[UserOut],
    dependencies=[Depends(get_admin_user)],
)
def admin_list_users(db: Session = Depends(get_db)):
    return list_users(db)

# 4) Admin: delete user
@app.delete(
    "/admin/users/{user_id}",
    response_model=UserOut,
    dependencies=[Depends(get_admin_user)],
)
def admin_delete_user(user_id: int, db: Session = Depends(get_db)):
    user = delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# 5) Admin: list sessions
@app.get(
    "/admin/sessions",
    response_model=list[SessionOut],
    dependencies=[Depends(get_admin_user)],
)
def admin_list_sessions(db: Session = Depends(get_db)):
    return list_sessions(db)

# 6) Admin UI
@app.get(
    "/admin",
    response_class=HTMLResponse,
    dependencies=[Depends(get_admin_user)],
)
def admin_panel():
    with open("static/admin.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())
