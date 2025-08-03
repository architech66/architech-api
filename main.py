# main.py
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import Base, engine, get_db
import auth, crud
from schemas import (
    UserCreate, UserOut,
    SessionOut,
    APIKeyCreate, APIKeyOut,
    Token
)

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ARCHITECH Auth API")

# Serve admin UI
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Middleware for API-key quota enforcement ---
@app.middleware("http")
async def api_key_quota_middleware(request: Request, call_next):
    key_str = request.headers.get("X-API-Key")
    if key_str:
        db = next(get_db())
        from models import APIKey
        ak = db.query(APIKey).filter_by(key=key_str, revoked=False).first()
        if not ak:
            return JSONResponse(status_code=403, content={"detail":"Invalid API Key"})
        if ak.usage_quota is not None and ak.usage_count >= ak.usage_quota:
            return JSONResponse(status_code=429, content={"detail":"Quota exceeded"})
        ak.usage_count += 1
        db.commit()
    return await call_next(request)

# --- Token endpoint with hardware capture ---
@app.post("/token", response_model=Token)
async def login_token(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = auth.authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(401, "Bad credentials")

    # capture hardware info
    dev = request.headers.get("X-Device-Model")
    os_ = request.headers.get("X-OS-Info")
    ua  = request.headers.get("User-Agent")

    crud.record_session(db, user.id, request.client.host,
                        device_model=dev, os_info=os_, user_agent=ua)

    token = auth.create_access_token(user.username)
    return {"access_token": token, "token_type": "bearer"}

# --- User management ---
@app.post("/admin/users", response_model=UserOut,
          dependencies=[Depends(auth.get_admin_user)])
def admin_create_user(u: UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, u)

@app.get("/admin/users", response_model=list[UserOut],
         dependencies=[Depends(auth.get_admin_user)])
def admin_list_users(db: Session = Depends(get_db)):
    return crud.list_users(db)

@app.delete("/admin/users/{user_id}", response_model=UserOut,
            dependencies=[Depends(auth.get_admin_user)])
def admin_delete_user(user_id: int, db: Session = Depends(get_db)):
    u = crud.delete_user(db, user_id)
    if not u:
        raise HTTPException(404, "User not found")
    return u

# --- Sessions (with hardware) ---
@app.get("/admin/sessions", response_model=list[SessionOut],
         dependencies=[Depends(auth.get_admin_user)])
def admin_list_sessions(db: Session = Depends(get_db)):
    return crud.list_sessions(db)

# --- API Key Management ---
@app.post("/admin/keys", response_model=APIKeyOut,
          dependencies=[Depends(auth.get_admin_user)])
def admin_create_key(data: APIKeyCreate, db: Session = Depends(get_db)):
    return crud.create_api_key(db, data.user_id, data.scopes, data.usage_quota)

@app.get("/admin/keys", response_model=list[APIKeyOut],
         dependencies=[Depends(auth.get_admin_user)])
def admin_list_keys(db: Session = Depends(get_db)):
    return crud.list_api_keys(db)

@app.delete("/admin/keys/{key}", dependencies=[Depends(auth.get_admin_user)])
def admin_revoke_key(key: str, db: Session = Depends(get_db)):
    ak = crud.revoke_api_key(db, key)
    if not ak:
        raise HTTPException(404, "API Key not found")
    return {"status":"revoked"}

# --- Static admin panel ---
@app.get("/admin", response_class=HTMLResponse,
         dependencies=[Depends(auth.get_admin_user)])
def admin_panel():
    with open("static/admin.html", "r") as f:
        return HTMLResponse(f.read())
