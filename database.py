# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQL_URL = "sqlite:///./app.db"

engine = create_engine(
    SQL_URL,
    connect_args={"check_same_thread": False}
)

# Rename the session factory to SessionLocal so imports line up
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
