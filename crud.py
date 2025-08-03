from sqlalchemy.orm import Session
from models import User, Session as Sess
from security import get_password_hash

def create_user(db: Session, u):
    pw_hash = get_password_hash(u.password)
    user = User(
        username=u.username,
        hashed_pw=pw_hash,
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

def record_session(db: Session, user_id: int, ip: str):
    s = Sess(user_id=user_id, ip_address=ip)
    db.add(s); db.commit(); db.refresh(s)
    return s

def list_sessions(db: Session):
    return db.query(Sess).order_by(Sess.timestamp.desc()).all()
