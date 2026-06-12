# backend/routers/customers.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from typing import Optional
from database import get_db
from models import Customer
from schemas.customer import CustomerResponse, CustomerSummary

router = APIRouter()


# ──────────────────────────────────────────────────────────────────────
# GET ALL CUSTOMERS — with optional aesthetic + behaviour filters
# ──────────────────────────────────────────────────────────────────────
@router.get("/customers", response_model=list[CustomerResponse])
def get_customers(
    db:                 Session = Depends(get_db),
    preferred_craft:    Optional[str] = Query(None),
    preferred_region:   Optional[str] = Query(None),
    style_affinity:     Optional[str] = Query(None),
    preferred_fabric:   Optional[str] = Query(None),
    gender_preference:  Optional[str] = Query(None),
    city:               Optional[str] = Query(None),
    min_orders:         Optional[int] = Query(None),
    min_spent:          Optional[float] = Query(None),
    days_inactive:      Optional[int] = Query(None),
):
    query = db.query(Customer)

    # Aesthetic filters
    if preferred_craft:
        query = query.filter(Customer.preferred_craft == preferred_craft)
    if preferred_region:
        query = query.filter(Customer.preferred_region == preferred_region)
    if style_affinity:
        query = query.filter(Customer.style_affinity == style_affinity)
    if preferred_fabric:
        query = query.filter(Customer.preferred_fabric == preferred_fabric)
    if gender_preference:
        query = query.filter(Customer.gender_preference == gender_preference)
    if city:
        query = query.filter(Customer.city == city)

    # Behaviour filters
    if min_orders:
        query = query.filter(Customer.total_orders >= min_orders)
    if min_spent:
        query = query.filter(Customer.total_spent >= min_spent)
    if days_inactive:
        cutoff = (datetime.now() - timedelta(days=days_inactive)).strftime("%Y-%m-%d")
        query = query.filter(Customer.last_purchase_date <= cutoff)

    return query.order_by(Customer.total_spent.desc()).all()


# ──────────────────────────────────────────────────────────────────────
# GET SINGLE CUSTOMER
# ──────────────────────────────────────────────────────────────────────
@router.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


# ──────────────────────────────────────────────────────────────────────
# GET CUSTOMER SUMMARIES — lightweight for dropdowns
# ──────────────────────────────────────────────────────────────────────
@router.get("/customers/summary/all", response_model=list[CustomerSummary])
def get_customer_summaries(db: Session = Depends(get_db)):
    return db.query(Customer).order_by(Customer.name).all()