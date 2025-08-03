from sqlalchemy.orm import Session
from models import User, Session as Sess
from security import get_password_hash

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, u):
    h = get_password_hash(u.password)
    usr = User(
        username=u.username,
        hashed_pw=h,
        is_admin=u.is_admin,
        twilio_sid=u.twilio_sid,
        twilio_token=u.twilio_token
    )
    db.add(usr); db.commit(); db.refresh(usr)
    return usr

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
