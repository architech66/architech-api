# main.py
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import HTMLResponse
import models, schemas
from database import Base, engine, get_db
import crud, security

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ARCHITECH Auth API")


# 1) Token route
@app.post("/token", response_model=schemas.Token)
async def login_token(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db=Depends(get_db)
):
    user = security.authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # record session
    crud.record_session(db, user.id, request.client.host)

    token = security.create_access_token(user.username)
    return {"access_token": token, "token_type": "bearer"}


# Admin dependency
def require_admin(user: models.User = Depends(security.authenticate_user), db=Depends(get_db)):
    if not user or not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return user


# 2) Create user
@app.post("/admin/users", response_model=schemas.UserOut, dependencies=[Depends(require_admin)])
def admin_create_user(u: schemas.UserCreate, db=Depends(get_db)):
    return crud.create_user(db, u)


# 3) List users
@app.get("/admin/users", response_model=list[schemas.UserOut], dependencies=[Depends(require_admin)])
def admin_list_users(db=Depends(get_db)):
    return crud.list_users(db)


# 4) Delete user
@app.delete("/admin/users/{user_id}", response_model=schemas.UserOut, dependencies=[Depends(require_admin)])
def admin_delete_user(user_id: int, db=Depends(get_db)):
    user = crud.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# 5) List sessions
@app.get("/admin/sessions", response_model=list[schemas.SessionOut], dependencies=[Depends(require_admin)])
def admin_list_sessions(db=Depends(get_db)):
    return crud.list_sessions(db)


# 6) Admin HTML UI
@app.get("/admin", response_class=HTMLResponse, dependencies=[Depends(require_admin)])
def admin_panel():
    with open("admin.html", "r") as f:
        return HTMLResponse(f.read())
