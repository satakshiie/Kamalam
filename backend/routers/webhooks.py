# backend/routers/webhooks.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from database import get_db
from models import Message, Campaign

router = APIRouter()


# ──────────────────────────────────────────────────────────────────────
# WEBHOOK PAYLOAD — shape of what channel service sends back
# ──────────────────────────────────────────────────────────────────────
class DeliveryWebhook(BaseModel):
    external_message_id:    str       # UUID we generated — maps back to our message
    status:                 str       # delivered / opened / clicked / failed
    timestamp:              str
    failure_reason:         Optional[str] = None


# ──────────────────────────────────────────────────────────────────────
# RECEIVE DELIVERY CALLBACK
# Called by channel service after simulating delivery outcome
# Updates the single message row — no campaign-level tallies written
# (avoids SQLite contention on concurrent webhook callbacks)
# ──────────────────────────────────────────────────────────────────────
@router.post("/webhooks/delivery")
def handle_delivery_webhook(payload: DeliveryWebhook, db: Session = Depends(get_db)):
    # Look up message by UUID — not by auto-increment id
    message = db.query(Message).filter(
        Message.external_message_id == payload.external_message_id
    ).first()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Update status + relevant timestamp
    message.status = payload.status

    if payload.status == "delivered":
        message.delivered_at = payload.timestamp
    elif payload.status == "opened":
        message.delivered_at = message.delivered_at or payload.timestamp
        message.opened_at    = payload.timestamp
    elif payload.status == "clicked":
        message.delivered_at = message.delivered_at or payload.timestamp
        message.opened_at    = message.opened_at    or payload.timestamp
        message.clicked_at   = payload.timestamp
    elif payload.status == "failed":
        message.failed_at       = payload.timestamp
        message.failure_reason  = payload.failure_reason

    db.commit()

    # Check if all messages in this campaign are now resolved
    # If so mark campaign as completed
    campaign = db.query(Campaign).filter(Campaign.id == message.campaign_id).first()
    if campaign and campaign.status == "sending":
        pending_count = db.execute(
            text("""
                SELECT COUNT(*) FROM messages
                WHERE campaign_id = :cid
                AND status IN ('pending', 'sent')
            """),
            {"cid": campaign.id}
        ).scalar()

        if pending_count == 0:
            campaign.status = "completed"
            db.commit()

    return {"ok": True, "message_id": payload.external_message_id}