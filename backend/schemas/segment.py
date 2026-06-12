# backend/schemas/segment.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ──────────────────────────────────────────────────────────────────────
# SEGMENT RESPONSE — full segment card shown on dashboard
# ──────────────────────────────────────────────────────────────────────
class SegmentResponse(BaseModel):
    id:             int
    name:           str
    description:    Optional[str]
    created_by:     str           # "ai" or "manual"
    ai_reasoning:   Optional[str] # why AI picked this — shown to marketer
    filters:        Optional[str] # raw JSON string of filter criteria
    customer_count: int
    created_at:     datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────────────────────────────
# SEGMENT CREATE — when a marketer manually creates a segment
# ──────────────────────────────────────────────────────────────────────
class SegmentCreate(BaseModel):
    name:           str
    description:    Optional[str] = None
    filters:        Optional[str] = None  # JSON string


# ──────────────────────────────────────────────────────────────────────
# SEGMENT SUMMARY — lightweight for campaign creation dropdowns
# ──────────────────────────────────────────────────────────────────────
class SegmentSummary(BaseModel):
    id:             int
    name:           str
    customer_count: int

    class Config:
        from_attributes = True