# backend/services/campaign_service.py

import uuid
import httpx
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
from dotenv import load_dotenv
from models import Campaign, Message, Segment, Customer

load_dotenv()

CHANNEL_SERVICE_URL = os.getenv("CHANNEL_SERVICE_URL", "http://localhost:8001")


def dispatch_campaign(campaign_id: int, db: Session):
    """
    Dispatches a campaign to the channel service.
    
    Flow:
    1. Load campaign + its segment
    2. Find all customers in the segment
    3. Create a Message row per customer with a UUID
    4. Send each message to the channel service
    5. Mark campaign as sending
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        print(f"❌ Campaign {campaign_id} not found")
        return

    segment = db.query(Segment).filter(Segment.id == campaign.segment_id).first()
    if not segment:
        print(f"❌ Segment {campaign.segment_id} not found")
        return

    # ── Get customers for this segment ──
    customers = get_customers_for_segment(segment=segment, db=db)

    if not customers:
        print(f"⚠️ No customers found for segment {segment.name}")
        return

    print(f"📢 Dispatching campaign '{campaign.name}' to {len(customers)} customers...")

    # ── Create message rows + dispatch to channel service ──
    for customer in customers:
        external_id = str(uuid.uuid4())

        # Personalise message body
        personalised_body = campaign.message_body.replace(
            "{name}", customer.name.split()[0]
        )

        # Create message row in DB
        message = Message(
            campaign_id             = campaign.id,
            customer_id             = customer.id,
            external_message_id     = external_id,
            status                  = "pending",
        )
        db.add(message)
        db.flush()  # get message written without full commit

        # Send to channel service asynchronously
        try:
            httpx.post(
                f"{CHANNEL_SERVICE_URL}/send",
                json={
                    "external_message_id": external_id,
                    "recipient":           customer.email,
                    "channel":             campaign.channel,
                    "body":                personalised_body,
                    "callback_url":        "http://localhost:8000/api/webhooks/delivery"
                },
                timeout=5.0
            )
        except Exception as e:
            print(f"⚠️  Failed to dispatch message {external_id}: {e}")

    # ── Mark campaign as sending ──
    campaign.status  = "sending"
    campaign.sent_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.commit()

    print(f"✅ Campaign '{campaign.name}' dispatched — {len(customers)} messages queued")


def get_customers_for_segment(segment: Segment, db: Session) -> list:
    """
    Returns customers matching a segment's filters.
    Filters are stored as a JSON string in the segment row.
    """
    import json
    from datetime import datetime, timedelta

    filters = {}
    if segment.filters:
        try:
            filters = json.loads(segment.filters)
        except Exception:
            filters = {}

    query = db.query(Customer)

    # Apply filters dynamically based on what's in the segment
    if "preferred_craft" in filters:
        query = query.filter(
            Customer.preferred_craft == filters["preferred_craft"]
        )
    if "preferred_fabric" in filters:
        query = query.filter(
            Customer.preferred_fabric == filters["preferred_fabric"]
        )
    if "style_affinity" in filters:
        query = query.filter(
            Customer.style_affinity == filters["style_affinity"]
        )
    if "min_orders" in filters:
        query = query.filter(
            Customer.total_orders >= filters["min_orders"]
        )
    if "min_spend" in filters:
        query = query.filter(
            Customer.total_spent >= filters["min_spend"]
        )
    if "min_total_spent" in filters:
        query = query.filter(
            Customer.total_spent >= filters["min_total_spent"]
        )
    if "days_inactive" in filters:
        cutoff = (
            datetime.now() - timedelta(days=filters["days_inactive"])
        ).strftime("%Y-%m-%d")
        query = query.filter(Customer.last_purchase_date <= cutoff)
    if "total_orders" in filters:
        query = query.filter(
            Customer.total_orders == filters["total_orders"]
        )

    return query.all()