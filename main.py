# main.py
from pathlib import Path

from fastapi import (
    FastAPI, Depends, HTTPException, Request, Form
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from auth import (
    authenticate_user,
    create_access_token,
    get_admin_user
)
from crud import (
    create_user,
    list_users,
    delete_user,
    record_session,
    list_sessions
)
from database import Base, engine, SessionLocal
from schemas import UserCreate, UserOut, SessionOut, Token

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ARCHITECH Auth API")

# Serve your HTML/CSS/JS from ./static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Redirect root → docs
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

# Token endpoint (records IP)
@app.post("/token", response_model=Token)
async def login_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db = Depends(SessionLocal)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(401, "Bad credentials")
    record_session(db, user.id, request.client.host)
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# Admin login page
@app.get("/admin", response_class=HTMLResponse, include_in_schema=False)
async def get_admin_login(request: Request):
    error = request.query_params.get("error", "")
    html = Path("static/admin_login.html").read_text()
    return HTMLResponse(html.replace("{{ error }}", error))

# Handle login form
@app.post("/admin/login", include_in_schema=False)
async def post_admin_login(
    username: str = Form(...),
    password: str = Form(...)
):
    # one hard-coded admin
    if username != "architech66" or password != r"v+ir2E9WELO%JY\H":
        return RedirectResponse("/admin?error=Invalid+credentials", status_code=302)

    resp = RedirectResponse("/admin/panel", status_code=302)
    resp.set_cookie("admin", "true", httponly=True)
    return resp

# Protected admin panel
@app.get("/admin/panel", response_class=HTMLResponse)
async def admin_panel(request: Request):
    if request.cookies.get("admin") != "true":
        raise HTTPException(401, "Not authenticated")
    return HTMLResponse(Path("static/admin.html").read_text())

# JSON API: Users
@app.get("/admin/users", response_model=list[UserOut])
async def api_list_users(
    current=Depends(get_admin_user),
    db=Depends(SessionLocal)
):
    return list_users(db)

@app.post("/admin/users", response_model=UserOut)
async def api_create_user(
    u: UserCreate,
    current=Depends(get_admin_user),
    db=Depends(SessionLocal)
):
    return create_user(db, u)

@app.delete("/admin/users/{user_id}", response_model=UserOut)
async def api_delete_user(
    user_id: int,
    current=Depends(get_admin_user),
    db=Depends(SessionLocal)
):
    user = delete_user(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

# JSON API: Sessions
@app.get("/admin/sessions", response_model=list[SessionOut])
async def api_list_sessions(
    current=Depends(get_admin_user),
    db=Depends(SessionLocal)
):
    return list_sessions(db)
