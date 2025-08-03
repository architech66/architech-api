import secrets
from sqlalchemy.orm import Session
from models import User, Session as Sess, ApiKey
from auth import hash_pw, verify_pw

def create_user(db: Session, username, password, is_admin=False, **extra):
    u = User(
      username=username,
      hashed_pw=hash_pw(password),
      is_admin=is_admin,
      **extra
    )
    db.add(u); db.commit(); db.refresh(u)
    return u

def authenticate_user(db: Session, username, password):
    u = db.query(User).filter_by(username=username).first()
    if u and verify_pw(password, u.hashed_pw):
        return u
    return None

def list_users(db: Session):
    return db.query(User).all()

def delete_user(db: Session, user_id: int):
    u = db.get(User, user_id)
    if u:
        db.delete(u); db.commit()
    return u

def record_session(db: Session, user_id: int, ip: str, user_agent: str):
    s = Sess(user_id=user_id, ip_address=ip, user_agent=user_agent)
    db.add(s); db.commit(); db.refresh(s)
    return s

def list_sessions(db: Session):
    return db.query(Sess).order_by(Sess.timestamp.desc()).all()

# API key CRUD
def create_api_key(db: Session, user_id: int):
    key = secrets.token_hex(16)
    k = ApiKey(user_id=user_id, key=key)
    db.add(k); db.commit(); db.refresh(k)
    return k

def list_api_keys(db: Session):
    return db.query(ApiKey).all()

def revoke_api_key(db: Session, key: str):
    k = db.query(ApiKey).filter_by(key=key).first()
    if k:
        k.revoked = True
        db.commit()
    return k
