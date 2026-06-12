# backend/database.py

from sqlalchemy import create_engine , event
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite file will be created automatically in the backend folder
DATABASE_URL = "sqlite:///./indie_crm.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
    # ↑ Required for SQLite with FastAPI
    # FastAPI handles requests on multiple threads
    # SQLite by default only allows one thread — this disables that restriction
)
from sqlalchemy import  event

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
    
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
# ↑ All your models.py tables will inherit from this


# Dependency — used in every router
# Gives a DB session, closes it after the request is done
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()