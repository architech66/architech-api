from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from auth import router as auth_router
from security import get_admin_user
from crud import (
    create_user, list_users, delete_user,
    list_sessions
)
from schemas import UserCreate, UserOut, SessionOut

# create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ARCHITECH Auth API")

# mount /token
app.include_router(auth_router)

# admin CRUD
@app.post("/admin/users", response_model=UserOut,
          dependencies=[Depends(get_admin_user)])
def admin_create_user(u: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, u)

@app.get("/admin/users", response_model=list[UserOut],
         dependencies=[Depends(get_admin_user)])
def admin_list_users(db: Session = Depends(get_db)):
    return list_users(db)

@app.delete("/admin/users/{user_id}", response_model=UserOut,
            dependencies=[Depends(get_admin_user)])
def admin_delete_user(user_id: int, db: Session = Depends(get_db)):
    user = delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/admin/sessions", response_model=list[SessionOut],
         dependencies=[Depends(get_admin_user)])
def admin_list_sessions(db: Session = Depends(get_db)):
    return list_sessions(db)

@app.get("/admin", response_class=HTMLResponse,
         dependencies=[Depends(get_admin_user)])
def admin_panel():
    with open("admin.html", "r") as f:
        return HTMLResponse(f.read())
