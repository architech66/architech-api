--- a/crud.py
+++ b/crud.py
@@
 def record_session(db: Session, user_id: int, ip: str):
@@
     return s

+def get_user_by_username(db: Session, username: str):
+    return db.query(User).filter(User.username == username).first()
