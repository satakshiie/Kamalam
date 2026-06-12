# backend/main.py

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import engine, Base, get_db, SessionLocal
from models import Customer
import models
from routers import customers, segments, campaigns, analytics, webhooks


# ──────────────────────────────────────────────────────────────────────
# FASTAPI APPLICATION SETUP
# ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Kamalam CRM API",
    description="AI-Native CRM backend for homegrown Indian apparel brands",
    version="1.0.0"
)


# ──────────────────────────────────────────────────────────────────────
# HELPERS — defined before startup so Python can find them
# ──────────────────────────────────────────────────────────────────────
def auto_seed_if_empty():
    db = SessionLocal()
    try:
        count = db.query(Customer).count()
        if count == 0:
            print("📦 Empty database detected — auto seeding...")
            from seed import seed
            seed()
        else:
            print(f"✅ Database already has {count} customers — skipping seed")
    finally:
        db.close()


# ──────────────────────────────────────────────────────────────────────
# STARTUP — single handler, runs once when FastAPI starts
# ──────────────────────────────────────────────────────────────────────
@app.on_event("startup")
def startup():
    # Step 1 — create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    # Step 2 — seed data if database is empty
    auto_seed_if_empty()


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
        db.execute(text("SELECT 1"))
        return {"database_status": "connected", "details": "Bridge is healthy"}
    except Exception as e:
        return {"database_status": "disconnected", "error": str(e)}
    

app.include_router(customers.router,  prefix="/api")
app.include_router(segments.router,   prefix="/api")
app.include_router(campaigns.router,  prefix="/api")
app.include_router(analytics.router,  prefix="/api")
app.include_router(webhooks.router,   prefix="/api")
