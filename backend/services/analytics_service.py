# backend/services/analytics_service.py

from sqlalchemy.orm import Session
from sqlalchemy import text
from models import Campaign, CampaignAnalytics
from schemas.analytics import CampaignLiveStats, PostCampaignInsights


def get_live_stats(campaign_id: int, campaign: Campaign, db: Session) -> CampaignLiveStats:
    """
    Calculates live campaign stats on the fly via COUNT queries.
    Never reads from stored tallies — avoids SQLite write contention
    on concurrent webhook callbacks from channel service.
    """
    result = db.execute(text("""
        SELECT
            COUNT(*)                                        AS total,
            COUNT(CASE WHEN status = 'sent'      THEN 1 END) AS sent,
            COUNT(CASE WHEN status = 'delivered' THEN 1 END) AS delivered,
            COUNT(CASE WHEN status = 'opened'    THEN 1 END) AS opened,
            COUNT(CASE WHEN status = 'clicked'   THEN 1 END) AS clicked,
            COUNT(CASE WHEN status = 'failed'    THEN 1 END) AS failed,
            COUNT(CASE WHEN status = 'pending'   THEN 1 END) AS pending
        FROM messages
        WHERE campaign_id = :campaign_id
    """), {"campaign_id": campaign_id}).fetchone()

    total       = result.total     or 0
    delivered   = result.delivered or 0
    opened      = result.opened    or 0
    clicked     = result.clicked   or 0
    failed      = result.failed    or 0

    # Safe division — avoid divide by zero if no messages yet
    def rate(numerator: int) -> float:
        return round((numerator / total) * 100, 1) if total > 0 else 0.0

    return CampaignLiveStats(
        campaign_id     = campaign_id,
        campaign_name   = campaign.name,
        status          = campaign.status,
        total           = total,
        sent            = result.sent       or 0,
        delivered       = delivered,
        opened          = opened,
        clicked         = clicked,
        failed          = failed,
        pending         = result.pending    or 0,
        delivery_rate   = rate(delivered),
        open_rate       = rate(opened),
        click_rate      = rate(clicked),
        failure_rate    = rate(failed),
    )


def get_post_campaign_insights(campaign_id: int, db: Session):
    """
    Returns stored AI insights for completed campaigns.
    Only populated after campaign status = completed.
    """
    analytics = db.query(CampaignAnalytics).filter(
        CampaignAnalytics.campaign_id == campaign_id
    ).first()

    if not analytics:
        return None

    return PostCampaignInsights(
        campaign_id             = campaign_id,
        top_responding_craft    = analytics.top_responding_craft,
        top_responding_region   = analytics.top_responding_region,
        top_responding_mood     = analytics.top_responding_mood,
        ai_post_campaign_notes  = analytics.ai_post_campaign_notes,
    )