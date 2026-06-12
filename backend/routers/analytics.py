# backend/routers/analytics.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Campaign
from services.analytics_service import get_live_stats, get_post_campaign_insights
from schemas.analytics import FullCampaignAnalytics

router = APIRouter()


# ──────────────────────────────────────────────────────────────────────
# GET FULL CAMPAIGN ANALYTICS
# Called by React every 4 seconds via polling
# Returns live stats + post-campaign AI insights if available
# ──────────────────────────────────────────────────────────────────────
@router.get("/campaigns/{campaign_id}/stats", response_model=FullCampaignAnalytics)
def get_campaign_stats(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Live stats — always calculated fresh from messages table
    live = get_live_stats(campaign_id=campaign_id, campaign=campaign, db=db)

    # Post campaign insights — only available after campaign completes
    insights = None
    if campaign.status == "completed":
        insights = get_post_campaign_insights(campaign_id=campaign_id, db=db)

    return FullCampaignAnalytics(live=live, insights=insights)