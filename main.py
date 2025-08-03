--- a/main.py
+++ b/main.py
@@
-@app.post("/token", response_model=Token)
-async def login_token(
-    form: OAuth2PasswordRequestForm = Depends(),
-    db: Session = Depends(get_db),
-    request: Request
-):
+@app.post("/token", response_model=Token)
+async def login_token(
+    request: Request,
+    form: OAuth2PasswordRequestForm = Depends(),
+    db: Session = Depends(get_db),
+):
     user = authenticate_user(db, form.username, form.password)
     if not user:
         raise HTTPException(401, "Bad credentials")
     # record IP
     ip = request.client.host
