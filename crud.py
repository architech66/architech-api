# crud.py
from sqlalchemy.orm import Session
import models, schemas, security

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, u: schemas.UserCreate):
    hashed = security.get_password_hash(u.password)
    user = models.User(
        username=u.username,
        hashed_pw=hashed,
        is_admin=u.is_admin,
        twilio_sid=u.twilio_sid,
        twilio_token=u.twilio_token
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def list_users(db: Session):
    return db.query(models.User).all()

def delete_user(db: Session, user_id: int):
    user = db.get(models.User, user_id)
    if user:
        db.delete(user)
        db.commit()
    return user

def record_session(db: Session, user_id: int, ip: str):
    sess = models.Session(user_id=user_id, ip_address=ip)
    db.add(sess)
    db.commit()
    db.refresh(sess)
    return sess

def list_sessions(db: Session):
    return db.query(models.Session).order_by(models.Session.timestamp.desc()).all()
