# crud.py
import json
import secrets
from sqlalchemy.orm import Session
from models import User, Session as Sess, APIKey
from auth import get_password_hash

def create_user(db: Session, u):
    h = get_password_hash(u.password)
    user = User(
        username=u.username,
        hashed_pw=h,
        is_admin=u.is_admin,
        twilio_sid=u.twilio_sid,
        twilio_token=u.twilio_token
    )
    db.add(user); db.commit(); db.refresh(user)
    return user

def list_users(db: Session):
    return db.query(User).all()

def delete_user(db: Session, user_id: int):
    user = db.get(User, user_id)
    if user:
        db.delete(user); db.commit()
    return user

def record_session(db: Session, user_id: int, ip: str,
                   device_model: str=None,
                   os_info: str=None,
                   user_agent: str=None):
    s = Sess(
        user_id=user_id,
        ip_address=ip,
        device_model=device_model,
        os_info=os_info,
        user_agent=user_agent
    )
    db.add(s); db.commit(); db.refresh(s)
    return s

def list_sessions(db: Session):
    return db.query(Sess).order_by(Sess.timestamp.desc()).all()

# --- API Key CRUD ---

def create_api_key(db: Session, user_id: int, scopes: list[str], quota: int|None):
    raw = secrets.token_urlsafe(32)
    ak = APIKey(
        user_id=user_id,
        key=raw,
        scopes=json.dumps(scopes),
        usage_quota=quota
    )
    db.add(ak); db.commit(); db.refresh(ak)
    return ak

def list_api_keys(db: Session):
    return db.query(APIKey).all()

def revoke_api_key(db: Session, key_str: str):
    ak = db.query(APIKey).filter_by(key=key_str).first()
    if ak:
        ak.revoked = True
        db.commit()
    return ak
