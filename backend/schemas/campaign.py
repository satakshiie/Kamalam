# backend/schemas/campaign.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# ──────────────────────────────────────────────────────────────────────
# CAMPAIGN RESPONSE — full campaign card shown to marketer
# ──────────────────────────────────────────────────────────────────────
class CampaignResponse(BaseModel):
    id:                 int
    segment_id:         int
    name:               str
    message_body:       str
    channel:            str

    # AI metadata
    ai_suggested:       int
    ai_recommendation:  Optional[str]  # reasoning shown to marketer
    approved_by_user:   int

    # Status
    status:             str  # draft → approved → sending → completed
    scheduled_at:       Optional[str]
    sent_at:            Optional[str]
    created_at:         datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────────────────────────────
# CAMPAIGN CREATE — when marketer manually creates a campaign
# ──────────────────────────────────────────────────────────────────────
class CampaignCreate(BaseModel):
    segment_id:     int
    name:           str
    message_body:   str
    channel:        str = "email"


# ──────────────────────────────────────────────────────────────────────
# CAMPAIGN APPROVE — marketer hits approve on an AI suggestion
# Just needs the campaign id (in URL) — no body needed
# But we define a response so React knows what comes back
# ──────────────────────────────────────────────────────────────────────
class CampaignApproveResponse(BaseModel):
    id:                 int
    status:             str   # should now be "approved"
    approved_by_user:   int   # should now be 1

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────────────────────────────
# CAMPAIGN SUMMARY — lightweight for lists
# ──────────────────────────────────────────────────────────────────────
class CampaignSummary(BaseModel):
    id:             int
    name:           str
    status:         str
    channel:        str
    approved_by_user: int
    created_at:     datetime

    class Config:
        from_attributes = True