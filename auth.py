# add:
from fastapi import Request
from crud import record_session

# inside login_token():
@app.post("/token", response_model=Token)
async def login_token(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request: Request
):
    user = authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(401, "Bad credentials")
    # record IP
    ip = request.client.host
    record_session(db, user.id, ip)
    access = create_access_token({"sub": user.username})
    return {"access_token": access, "token_type": "bearer"}
