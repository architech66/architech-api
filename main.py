# main.py
from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import Base, engine, Session  # your existing imports
from auth import authenticate_user, create_access_token, get_current_user, get_admin_user, get_db
from crud import create_user, list_users, delete_user, list_sessions, record_session
from schemas import UserCreate, UserOut, SessionOut, Token

# create your tables as before
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ARCHITECH Auth API")

# 1) Serve static files from ./static
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2) Point Jinja2Templates at ./templates
templates = Jinja2Templates(directory="templates")


# ---- your existing API endpoints (token, CRUD, etc.) go here unchanged ----
# e.g.:
# @app.post("/token", response_model=Token)
# async def login_token(...):
#     ...


# ---- new simple admin‐panel auth + templating ----

# hard-coded admin creds:
ADMIN_USER = "architect66"
ADMIN_PASS = r"v+ir2E9WELO%JY\H"

def is_admin_cookie(request: Request) -> bool:
    return request.cookies.get("admin_auth") == "1"

@app.get("/admin", response_class=HTMLResponse)
async def admin_get(request: Request):
    """
    GET /admin
    - if not logged in: shows login form
    - if logged in: shows main panel (templates/admin.html JS will flip views)
    """
    auth = is_admin_cookie(request)
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "user_is_authenticated": auth}
    )

@app.post("/admin/login", response_class=HTMLResponse)
async def admin_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """
    POST /admin/login
    Checks form creds, sets a secure cookie on success, redirects back to /admin.
    """
    if username != ADMIN_USER or password != ADMIN_PASS:
        # send back to login with an error (you can wire this into your template later)
        return templates.TemplateResponse(
            "admin.html",
            {
                "request": request,
                "user_is_authenticated": False,
                "error_message": "Invalid username or password."
            }
        )

    # on success, set cookie and redirect
    response = RedirectResponse(url="/admin", status_code=302)
    response.set_cookie(
        key="admin_auth",
        value="1",
        httponly=True,
        secure=True,      # HTTPS-only
        max_age=60*60*24  # 1 day
    )
    return response

@app.get("/admin/logout")
async def admin_logout():
    """
    GET /admin/logout
    Clears the auth cookie and redirects to /admin (login screen).
    """
    response = RedirectResponse(url="/admin", status_code=302)
    response.delete_cookie("admin_auth")
    return response
