import os
from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from database import Base, engine, get_db
from crud import (
    authenticate_user, list_users, delete_user,
    list_sessions, record_session,
    create_api_key, list_api_keys, revoke_api_key
)
from security import ADMIN_USER, ADMIN_PASS, SESSION_SECRET
from schemas import UserOut, SessionOut, ApiKeyOut

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
# mount static/
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# dependency: only admin may call
def require_admin(req: Request):
    if req.session.get("user") != ADMIN_USER:
        raise HTTPException(401, "Not authenticated")

# ——— LOGIN FLow ————————————————————————————————

@app.get("/admin")
def get_admin(request: Request):
    if request.session.get("user") != ADMIN_USER:
        return templates.TemplateResponse("login.html", {"request": request, "error": ""})
    return templates.TemplateResponse("admin.html", {"request": request})

@app.post("/admin/login")
def do_login(request: Request,
             username: str = Form(...),
             password: str = Form(...)):
    if username == ADMIN_USER and password == ADMIN_PASS:
        request.session["user"] = ADMIN_USER
        return RedirectResponse("/admin", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

@app.get("/admin/logout")
def do_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin", status_code=302)

# ——— ADMIN AJAX ENDPOINTS ————————————————————————

@app.get("/admin/users", dependencies=[Depends(require_admin)], response_model=list[UserOut])
def ajax_list_users(db=Depends(get_db)):
    return list_users(db)

@app.delete("/admin/users/{user_id}", dependencies=[Depends(require_admin)], response_model=UserOut)
def ajax_delete_user(user_id: int, db=Depends(get_db)):
    u = delete_user(db, user_id)
    if not u:
        raise HTTPException(404, "User not found")
    return u

@app.get("/admin/sessions", dependencies=[Depends(require_admin)], response_model=list[SessionOut])
def ajax_list_sessions(request: Request, db=Depends(get_db)):
    # record page‐hit as session?
    record_session(db,
                   user_id = None,
                   ip       = request.client.host,
                   user_agent = request.headers.get("user-agent",""))
    return list_sessions(db)

@app.get("/admin/keys", dependencies=[Depends(require_admin)], response_model=list[ApiKeyOut])
def ajax_list_keys(db=Depends(get_db)):
    return list_api_keys(db)

@app.post("/admin/keys/{user_id}", dependencies=[Depends(require_admin)], response_model=ApiKeyOut)
def ajax_create_key(user_id: int, db=Depends(get_db)):
    return create_api_key(db, user_id)

@app.delete("/admin/keys/{key}", dependencies=[Depends(require_admin)], response_model=ApiKeyOut)
def ajax_revoke_key(key: str, db=Depends(get_db)):
    k = revoke_api_key(db, key)
    if not k:
        raise HTTPException(404, "Key not found")
    return k
