# backend/schemas/customer.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ──────────────────────────────────────────────────────────────────────
# CUSTOMER RESPONSE — what the API sends to React
# ──────────────────────────────────────────────────────────────────────
class CustomerResponse(BaseModel):
    id:                 int
    name:               str
    email:              str
    phone:              Optional[str]
    city:               Optional[str]
    state:              Optional[str]

    # Aesthetic profile
    style_affinity:     Optional[str]
    preferred_fabric:   Optional[str]
    preferred_craft:    Optional[str]
    preferred_region:   Optional[str]
    size_preference:    Optional[str]
    gender_preference:  Optional[str]

    # Behaviour
    total_orders:       int
    total_spent:        float
    avg_order_value:    float
    last_purchase_date: Optional[str]

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────────────────────────────
# CUSTOMER FILTER — query params React sends to filter the list
# ──────────────────────────────────────────────────────────────────────
class CustomerFilter(BaseModel):
    preferred_craft:    Optional[str] = None
    preferred_region:   Optional[str] = None
    style_affinity:     Optional[str] = None
    preferred_fabric:   Optional[str] = None
    gender_preference:  Optional[str] = None
    city:               Optional[str] = None
    min_orders:         Optional[int] = None
    min_spent:          Optional[float] = None
    days_inactive:      Optional[int] = None


# ──────────────────────────────────────────────────────────────────────
# CUSTOMER SUMMARY — lightweight version for dropdowns / segment counts
# ──────────────────────────────────────────────────────────────────────
class CustomerSummary(BaseModel):
    id:     int
    name:   str
    email:  str
    city:   Optional[str]

    class Config:
        from_attributes = True