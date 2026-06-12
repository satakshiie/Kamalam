# backend/schemas/analytics.py

from pydantic import BaseModel, computed_field
from typing import Optional


# ──────────────────────────────────────────────────────────────────────
# LIVE STATS — calculated on the fly from messages table (no stored tallies)
# This is what React receives every time it polls /campaigns/:id/stats
# ──────────────────────────────────────────────────────────────────────
class CampaignLiveStats(BaseModel):
    campaign_id:        int
    campaign_name:      str
    status:             str

    # Counts — calculated via SQL COUNT on messages table
    total:              int
    sent:               int
    delivered:          int
    opened:             int
    clicked:            int
    failed:             int
    pending:            int

    # Rates — calculated in the service layer
    delivery_rate:      float   # delivered / total
    open_rate:          float   # opened / total
    click_rate:         float   # clicked / total
    failure_rate:       float   # failed / total

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────────────────────────────
# POST CAMPAIGN AI INSIGHTS — heavier insights written after campaign ends
# Stored in campaign_analytics table
# ──────────────────────────────────────────────────────────────────────
class PostCampaignInsights(BaseModel):
    campaign_id:                int
    top_responding_craft:       Optional[str]
    top_responding_region:      Optional[str]
    top_responding_mood:        Optional[str]
    ai_post_campaign_notes:     Optional[str]

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────────────────────────────
# COMBINED — full analytics response for CampaignDetail.jsx
# Live stats + post-campaign insights in one payload
# ──────────────────────────────────────────────────────────────────────
class FullCampaignAnalytics(BaseModel):
    live:       CampaignLiveStats
    insights:   Optional[PostCampaignInsights] = None
    # insights is None while campaign is still sending
    # populated once campaign status = "completed"