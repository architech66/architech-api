# main.py
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader

from database import Base, engine
from crud import list_users, list_sessions
from auth import get_db
from schemas import UserOut, SessionOut

# 1) Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ARCHITECH Auth API")

# 2) Mount our static files & setup Jinja2
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Environment(loader=FileSystemLoader("templates"))

# 3) Hard-coded admin credentials (note the doubled backslash)
ADMIN_USER = "architect66"
ADMIN_PASS = "v+ir2E9WELO%JY\\H"


@app.get("/admin", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """
    Show login form. No auth required here.
    """
    html = templates.get_template("admin.html").render({"error_message": None})
    return HTMLResponse(html)


@app.post("/admin/login", response_class=HTMLResponse)
async def admin_login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """
    Process login. On success, set a cookie and redirect to /admin/panel.
    """
    if username != ADMIN_USER or password != ADMIN_PASS:
        html = templates.get_template("admin.html").render({
            "error_message": "Invalid credentials"
        })
        return HTMLResponse(html, status_code=401)

    response = RedirectResponse(url="/admin/panel", status_code=302)
    response.set_cookie(key="admin_auth", value="true", httponly=True)
    return response


def require_admin(request: Request):
    """
    Dependency to protect private admin routes.
    """
    if request.cookies.get("admin_auth") == "true":
        return True
    raise HTTPException(status_code=403, detail="Not authenticated")


@app.get(
    "/admin/panel",
    response_class=HTMLResponse,
    dependencies=[Depends(require_admin)]
)
async def admin_panel(request: Request):
    """
    Render the actual admin panel (templates/panel.html).
    """
    html = templates.get_template("panel.html").render({})
    return HTMLResponse(html)


@app.get(
    "/admin/users",
    response_model=list[UserOut],
    dependencies=[Depends(require_admin)]
)
async def admin_list_users(db=Depends(get_db)):
    """
    Return JSON list of users.
    """
    return list_users(db)


@app.get(
    "/admin/sessions",
    response_model=list[SessionOut],
    dependencies=[Depends(require_admin)]
)
async def admin_list_sessions(db=Depends(get_db)):
    """
    Return JSON list of sessions.
    """
    return list_sessions(db)
