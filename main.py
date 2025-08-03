# main.py
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import HTMLResponse
from sqlalchemy.orm import Session

from database import Base, engine, Session as SessionLocal
from auth import authenticate_user, create_access_token, get_current_user, get_admin_user
from crud import create_user, list_users, delete_user, list_sessions, record_session
from schemas import UserCreate, UserOut, SessionOut, Token

# --- Initialize DB ---
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ARCHITECH Auth API")

# --- Dependency to get a DB session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 1) Token endpoint (records IP in auth.py) ---
@app.post("/token", response_model=Token)
async def login_token(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Bad credentials")
    # record IP
    record_session(db, user.id, request.client.host)
    access = create_access_token({"sub": user.username})
    return {"access_token": access, "token_type": "bearer"}

# --- 2) Create user ---
@app.post(
    "/admin/users",
    response_model=UserOut,
    dependencies=[Depends(get_admin_user)],
)
def admin_create_user(u: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, u)

# --- 3) List users ---
@app.get(
    "/admin/users",
    response_model=list[UserOut],
    dependencies=[Depends(get_admin_user)],
)
def admin_list_users(db: Session = Depends(get_db)):
    return list_users(db)

# --- 4) Delete user ---
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

# --- 5) List sessions ---
@app.get(
    "/admin/sessions",
    response_model=list[SessionOut],
    dependencies=[Depends(get_admin_user)],
)
def admin_list_sessions(db: Session = Depends(get_db)):
    return list_sessions(db)

# --- 6) Admin HTML panel ---
@app.get(
    "/admin",
    response_class=HTMLResponse,
    dependencies=[Depends(get_admin_user)],
)
def admin_panel():
    # serve your redesigned admin.html from a static folder
    with open("static/admin.html", "r") as f:
        return HTMLResponse(f.read())
