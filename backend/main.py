# backend/main.py

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import engine, Base, get_db
import models  # ensures all table classes are registered before create_all


# ──────────────────────────────────────────────────────────────────────
# FASTAPI APPLICATION SETUP
# ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Kamalam CRM API",
    description="AI-Native CRM backend for homegrown Indian apparel brands",
    version="1.0.0"
)


# ──────────────────────────────────────────────────────────────────────
# DATABASE INITIALIZATION
# ──────────────────────────────────────────────────────────────────────
@app.on_event("startup")
def create_tables():
    """
    Runs once when FastAPI starts — not at import time.
    Reads all models registered under Base and creates
    any tables that don't already exist in indie_crm.db.
    Safe to run on every restart.
    """
    Base.metadata.create_all(bind=engine)


# ──────────────────────────────────────────────────────────────────────
# BASE ENDPOINTS
# ──────────────────────────────────────────────────────────────────────
@app.get("/")
def read_root():
    """
    Root health check endpoint.
    Verifies that the backend server is up and running.
    """
    return {
        "status": "online",
        "platform": "Kamalam CRM API",
        "version": "1.0.0"
    }


@app.get("/api/db-check")
def test_database_connection(db: Session = Depends(get_db)):
    """
    Diagnostic endpoint to confirm the database session factory
    and connection bridge are working properly.
    """
    try:
        db.execute(text("SELECT 1"))  # text() required in SQLAlchemy 2.0+
        return {"database_status": "connected", "details": "Bridge is healthy"}
    except Exception as e:
        return {"database_status": "disconnected", "error": str(e)}