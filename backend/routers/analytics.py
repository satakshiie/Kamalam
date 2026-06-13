# backend/routers/analytics.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from models import Campaign
from services.analytics_service import get_live_stats, get_post_campaign_insights
from schemas.analytics import FullCampaignAnalytics

router = APIRouter()


# ──────────────────────────────────────────────────────────────────────
# EXISTING — single campaign stats (keep this)
# ──────────────────────────────────────────────────────────────────────
@router.get("/campaigns/{campaign_id}/stats", response_model=FullCampaignAnalytics)
def get_campaign_stats(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    live     = get_live_stats(campaign_id=campaign_id, campaign=campaign, db=db)
    insights = None
    if campaign.status == "completed":
        insights = get_post_campaign_insights(campaign_id=campaign_id, db=db)

    return FullCampaignAnalytics(live=live, insights=insights)


# ──────────────────────────────────────────────────────────────────────
# NEW 1 — REVENUE TREND + CAMPAIGN MARKERS
# Powers the main line chart on the dashboard
# ──────────────────────────────────────────────────────────────────────
@router.get("/analytics/revenue-trend")
def get_revenue_trend(db: Session = Depends(get_db)):
    """
    Returns daily revenue for the last 30 days.
    Also returns campaign dispatch dates as markers
    so the frontend can overlay them on the chart.
    """

    # Daily revenue for last 30 days
    revenue_rows = db.execute(text("""
        SELECT
            order_date                  AS date,
            SUM(amount_paid)            AS revenue,
            COUNT(*)                    AS order_count
        FROM orders
        WHERE order_date >= date('now', '-30 days')
        GROUP BY order_date
        ORDER BY order_date ASC
    """)).fetchall()

    # Campaign dispatch dates — for overlay markers
    campaign_markers = db.execute(text("""
        SELECT
            DATE(sent_at)   AS date,
            name            AS campaign_name,
            id              AS campaign_id
        FROM campaigns
        WHERE sent_at IS NOT NULL
        AND DATE(sent_at) >= date('now', '-30 days')
        ORDER BY sent_at ASC
    """)).fetchall()

    return {
        "revenue_trend": [
            {
                "date":         row.date,
                "revenue":      round(row.revenue, 2),
                "order_count":  row.order_count,
            }
            for row in revenue_rows
        ],
        "campaign_markers": [
            {
                "date":          marker.date,
                "campaign_name": marker.campaign_name,
                "campaign_id":   marker.campaign_id,
            }
            for marker in campaign_markers
        ]
    }


# ──────────────────────────────────────────────────────────────────────
# NEW 2 — CRAFT MIX
# Powers the donut chart on the dashboard
# ──────────────────────────────────────────────────────────────────────
@router.get("/analytics/craft-mix")
def get_craft_mix(db: Session = Depends(get_db)):
    """
    Returns order count and revenue broken down by craft type.
    Powers the donut chart showing what's driving sales.
    """

    rows = db.execute(text("""
        SELECT
            p.craft_type,
            COUNT(o.id)         AS order_count,
            SUM(o.amount_paid)  AS total_revenue
        FROM orders o
        JOIN products p ON o.product_id = p.id
        WHERE p.craft_type IS NOT NULL
        GROUP BY p.craft_type
        ORDER BY total_revenue DESC
    """)).fetchall()

    total_revenue = sum(row.total_revenue for row in rows) or 1

    return {
        "craft_mix": [
            {
                "craft":            row.craft_type,
                "order_count":      row.order_count,
                "total_revenue":    round(row.total_revenue, 2),
                "percentage":       round((row.total_revenue / total_revenue) * 100, 1),
            }
            for row in rows
        ]
    }


# ──────────────────────────────────────────────────────────────────────
# NEW 3 — PLATFORM WIDE ENGAGEMENT FUNNEL
# Powers the horizontal funnel chart on the dashboard
# ──────────────────────────────────────────────────────────────────────
@router.get("/analytics/funnel")
def get_engagement_funnel(db: Session = Depends(get_db)):
    """
    Returns platform-wide message engagement counts.
    Aggregates across ALL campaigns — not just one.
    Powers the Sent → Delivered → Opened → Clicked funnel chart.
    """

    result = db.execute(text("""
        SELECT
            COUNT(*)                                            AS total,
            COUNT(CASE WHEN status != 'pending'  THEN 1 END)   AS sent,
            COUNT(CASE WHEN status IN (
                'delivered', 'opened', 'clicked')  THEN 1 END) AS delivered,
            COUNT(CASE WHEN status IN (
                'opened', 'clicked')               THEN 1 END) AS opened,
            COUNT(CASE WHEN status = 'clicked'    THEN 1 END)  AS clicked,
            COUNT(CASE WHEN status = 'failed'     THEN 1 END)  AS failed
        FROM messages
    """)).fetchone()

    total     = result.total     or 1
    sent      = result.sent      or 0
    delivered = result.delivered or 0
    opened    = result.opened    or 0
    clicked   = result.clicked   or 0
    failed    = result.failed    or 0

    def rate(n): return round((n / total) * 100, 1) if total > 0 else 0.0

    return {
        "funnel": {
            "total":            result.total or 0,
            "sent":             sent,
            "delivered":        delivered,
            "opened":           opened,
            "clicked":          clicked,
            "failed":           failed,
        },
        "rates": {
            "delivery_rate":    rate(delivered),
            "open_rate":        rate(opened),
            "click_rate":       rate(clicked),
            "failure_rate":     rate(failed),
        }
    }


# ──────────────────────────────────────────────────────────────────────
# NEW 4 — DASHBOARD SUMMARY CARDS
# Powers the 3 small stat cards at the top of the dashboard
# ──────────────────────────────────────────────────────────────────────
@router.get("/analytics/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Returns high level numbers for the summary cards
    at the top of the dashboard.
    """

    total_customers = db.execute(
        text("SELECT COUNT(*) FROM customers")
    ).scalar() or 0

    total_revenue = db.execute(
        text("SELECT SUM(amount_paid) FROM orders")
    ).scalar() or 0

    active_campaigns = db.execute(
        text("SELECT COUNT(*) FROM campaigns WHERE status = 'sending'")
    ).scalar() or 0

    pending_approvals = db.execute(
        text("SELECT COUNT(*) FROM campaigns WHERE status = 'draft' AND ai_suggested = 1")
    ).scalar() or 0

    total_messages_sent = db.execute(
        text("SELECT COUNT(*) FROM messages WHERE status != 'pending'")
    ).scalar() or 0

    top_craft = db.execute(text("""
        SELECT p.craft_type, COUNT(*) as cnt
        FROM orders o
        JOIN products p ON o.product_id = p.id
        GROUP BY p.craft_type
        ORDER BY cnt DESC
        LIMIT 1
    """)).fetchone()

    return {
        "total_customers":      total_customers,
        "total_revenue":        round(total_revenue, 2),
        "active_campaigns":     active_campaigns,
        "pending_approvals":    pending_approvals,
        "total_messages_sent":  total_messages_sent,
        "top_craft":            top_craft[0] if top_craft else "handloom",
    }