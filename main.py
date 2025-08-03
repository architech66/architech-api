from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import HTMLResponse

from database import Base, engine
from auth import (
    authenticate_user, create_access_token,
    get_current_user, get_admin_user, get_db
)
from crud import (
    create_user, list_users, delete_user,
    list_sessions
)
from schemas import UserCreate, UserOut, SessionOut, Token

Base.metadata.create_all(bind=engine)
app = FastAPI(title="ARCHITECH Auth API")

# 1) Token endpoint (records IP in auth.py)
@app.post("/token", response_model=Token)
async def login_token(form: OAuth2PasswordRequestForm = Depends(),
                      db=Depends(get_db), request: Request):
    # (See auth.py snippet)
    ...

# 2) Create user
@app.post("/admin/users", response_model=UserOut,
          dependencies=[Depends(get_admin_user)])
def admin_create_user(u: UserCreate, db=Depends(get_db)):
    return create_user(db, u)

# 3) List users
@app.get("/admin/users", response_model=list[UserOut],
         dependencies=[Depends(get_admin_user)])
def admin_list_users(db=Depends(get_db)):
    return list_users(db)

# 4) Delete user
@app.delete("/admin/users/{user_id}", response_model=UserOut,
            dependencies=[Depends(get_admin_user)])
def admin_delete_user(user_id: int, db=Depends(get_db)):
    user = delete_user(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

# 5) List sessions
@app.get("/admin/sessions", response_model=list[SessionOut],
         dependencies=[Depends(get_admin_user)])
def admin_list_sessions(db=Depends(get_db)):
    return list_sessions(db)

# 6) Admin HTML panel
@app.get("/admin", response_class=HTMLResponse,
         dependencies=[Depends(get_admin_user)])
def admin_panel():
    with open("admin.html") as f:
        return HTMLResponse(f.read())
