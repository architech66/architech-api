from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from database import Base, engine, get_db
import auth
import crud
from schemas import UserCreate, UserOut, SessionOut, Token

# create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ARCHITECH Auth API")

# serve static/admin.html at /admin
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/token", response_model=Token)
async def login_token(form: OAuth2PasswordRequestForm = Depends(),
                      db: Depends(get_db),
                      request: Request):
    user = auth.authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(401, "Bad credentials")
    # record IP
    ip = request.client.host
    crud.record_session(db, user.id, ip)
    access = auth.create_access_token(user.username)
    return {"access_token": access, "token_type": "bearer"}

@app.post("/admin/users", response_model=UserOut,
          dependencies=[Depends(auth.get_admin_user)])
def admin_create_user(u: UserCreate, db: Depends(get_db)):
    return crud.create_user(db, u)

@app.get("/admin/users", response_model=list[UserOut],
         dependencies=[Depends(auth.get_admin_user)])
def admin_list_users(db: Depends(get_db)):
    return crud.list_users(db)

@app.delete("/admin/users/{user_id}", response_model=UserOut,
            dependencies=[Depends(auth.get_admin_user)])
def admin_delete_user(user_id: int, db: Depends(get_db)):
    user = crud.delete_user(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

@app.get("/admin/sessions", response_model=list[SessionOut],
         dependencies=[Depends(auth.get_admin_user)])
def admin_list_sessions(db: Depends(get_db)):
    return crud.list_sessions(db)

@app.get("/admin", response_class=HTMLResponse,
         dependencies=[Depends(auth.get_admin_user)])
def admin_panel():
    with open("static/admin.html") as f:
        return HTMLResponse(f.read())
