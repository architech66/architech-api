import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from crud import list_users, list_sessions
from schemas import UserOut, SessionOut, Token
from auth import create_access_token, decode_access_token

# ─── CONFIG ────────────────────────────────────
ADMIN_USER = "architect66"
# we’ll read the real password from an ENV VAR:
ADMIN_PASS = os.getenv("ADMIN_PASS", "")

app = FastAPI(
    title="ARCHITECH Auth API",
    docs_url=None, redoc_url=None, openapi_url=None
)
app.mount("/static", StaticFiles(directory="static"), name="static")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

bearer = HTTPBearer()

def require_admin(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        data = decode_access_token(creds.credentials)
    except:
        raise HTTPException(401, "Invalid token")
    if data.get("sub") != ADMIN_USER:
        raise HTTPException(403, "Forbidden")
    return True

# ─── ROUTES ───────────────────────────────────
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/admin")

@app.get("/admin", response_class=HTMLResponse, include_in_schema=False)
def serve_admin():
    with open("static/admin.html") as f:
        return HTMLResponse(f.read())

@app.post("/token", response_model=Token, include_in_schema=False)
def login_token(form: OAuth2PasswordRequestForm = Depends()):
    if form.username != ADMIN_USER or form.password != ADMIN_PASS:
        raise HTTPException(401, "Bad credentials")
    token = create_access_token({"sub": ADMIN_USER})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/users", response_model=list[UserOut], dependencies=[Depends(require_admin)])
def api_list_users(db: Session = Depends(get_db)):
    return list_users(db)

@app.get("/api/sessions", response_model=list[SessionOut], dependencies=[Depends(require_admin)])
def api_list_sessions(db: Session = Depends(get_db)):
    return list_sessions(db)

@app.exception_handler(404)
def not_found(_, __):
    return JSONResponse({"detail": "Not Found"}, status_code=404)
