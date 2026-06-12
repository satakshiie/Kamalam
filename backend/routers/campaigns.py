# backend/routers/campaigns.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import Campaign, Segment
from schemas.campaign import (
    CampaignResponse,
    CampaignCreate,
    CampaignApproveResponse,
    CampaignSummary
)
from services.ai_service import get_ai_recommendations
router = APIRouter()


# ──────────────────────────────────────────────────────────────────────
# GET ALL CAMPAIGNS
# ──────────────────────────────────────────────────────────────────────
@router.get("/campaigns", response_model=list[CampaignResponse])
def get_campaigns(db: Session = Depends(get_db)):
    return db.query(Campaign).order_by(Campaign.created_at.desc()).all()


# ──────────────────────────────────────────────────────────────────────
# GET SINGLE CAMPAIGN
# ──────────────────────────────────────────────────────────────────────
@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


# ──────────────────────────────────────────────────────────────────────
# CREATE CAMPAIGN — manual creation by marketer
# ──────────────────────────────────────────────────────────────────────
@router.post("/campaigns", response_model=CampaignResponse)
def create_campaign(payload: CampaignCreate, db: Session = Depends(get_db)):
    # Verify segment exists
    segment = db.query(Segment).filter(Segment.id == payload.segment_id).first()
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")

    campaign = Campaign(
        segment_id      = payload.segment_id,
        name            = payload.name,
        message_body    = payload.message_body,
        channel         = payload.channel,
        ai_suggested    = 0,   # manually created
        approved_by_user= 0,
        status          = "draft",
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


# ──────────────────────────────────────────────────────────────────────
# APPROVE CAMPAIGN — marketer approves an AI suggestion
# Triggers campaign dispatch via campaign_service
# ──────────────────────────────────────────────────────────────────────
@router.post("/campaigns/{campaign_id}/approve", response_model=CampaignApproveResponse)
def approve_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.approved_by_user == 1:
        raise HTTPException(status_code=400, detail="Campaign already approved")

    # Update campaign status
    campaign.approved_by_user   = 1
    campaign.status             = "approved"
    db.commit()
    db.refresh(campaign)

    # Dispatch campaign to channel service
    from services.campaign_service import dispatch_campaign
    dispatch_campaign(campaign_id=campaign.id, db=db)

    return campaign


# ──────────────────────────────────────────────────────────────────────
# REJECT CAMPAIGN — marketer rejects an AI suggestion
# ──────────────────────────────────────────────────────────────────────
@router.post("/campaigns/{campaign_id}/reject", response_model=CampaignSummary)
def reject_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft campaigns can be rejected")

    campaign.status = "rejected"
    db.commit()
    db.refresh(campaign)
    return campaign


# ──────────────────────────────────────────────────────────────────────
# GET CAMPAIGNS BY STATUS — useful for dashboard filtering
# ──────────────────────────────────────────────────────────────────────
@router.get("/campaigns/status/{status}", response_model=list[CampaignSummary])
def get_campaigns_by_status(status: str, db: Session = Depends(get_db)):
    valid_statuses = ["draft", "approved", "sending", "completed", "rejected"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    return db.query(Campaign).filter(
        Campaign.status == status
    ).order_by(Campaign.created_at.desc()).all()

@router.get("/recommendations")
def get_recommendations(db: Session = Depends(get_db)):
    """
    Calls Groq API with platform stats and returns
    3 fresh AI campaign recommendations for the dashboard.
    """
    recommendations = get_ai_recommendations(db=db)
    return {"recommendations": recommendations}