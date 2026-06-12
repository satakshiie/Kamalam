# backend/services/ai_service.py

import os
import json
from groq import Groq
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama3-70b-8192"


def get_ai_recommendations(db: Session) -> list[dict]:
    """
    Analyses customer + order data and returns AI-generated
    segment + campaign recommendations for the dashboard.

    Returns a list of recommendation objects the marketer
    can approve or reject.
    """

    # ── Pull summary stats from DB to give AI context ──
    stats = _get_platform_stats(db)

    prompt = f"""
You are an AI marketing assistant for Kamalam — a curated indie Indian apparel platform 
featuring handcrafted pieces from independent Indian designers.

Here is the current state of the customer base:

PLATFORM STATS:
- Total customers: {stats['total_customers']}
- Total orders: {stats['total_orders']}
- Average order value: ₹{stats['avg_order_value']}
- Most popular craft: {stats['top_craft']}
- Most popular region: {stats['top_region']}

INACTIVE CUSTOMERS (60+ days):
- Count: {stats['inactive_60']}

HIGH VALUE CUSTOMERS (spent ₹15,000+):
- Count: {stats['high_value']}

NEW CUSTOMERS (last 30 days):
- Count: {stats['new_customers']}

CRAFT BREAKDOWN:
{stats['craft_breakdown']}

Based on this data, generate exactly 3 marketing campaign recommendations.

Each recommendation must include:
1. segment_name: a poetic, specific name for the audience (e.g. "Handloom Loyalists", "Lapsed Festive Shoppers")
2. segment_description: one sentence describing who they are
3. segment_reasoning: 2-3 sentences explaining WHY this segment should be targeted now
4. campaign_name: a compelling campaign title
5. message_body: a personalised message (use {{name}} as placeholder). Keep it warm, story-first, and specific to Indian craft culture. Under 50 words.
6. channel: always "email"

Respond ONLY with a valid JSON array of 3 objects. No preamble, no explanation, no markdown.
Example format:
[
  {{
    "segment_name": "...",
    "segment_description": "...",
    "segment_reasoning": "...",
    "campaign_name": "...",
    "message_body": "...",
    "channel": "email"
  }}
]
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000,
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown fences if Groq wraps response in them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        recommendations = json.loads(raw)
        return recommendations

    except Exception as e:
        print(f"❌ AI recommendation error: {e}")
        return _fallback_recommendations()


def _get_platform_stats(db: Session) -> dict:
    """
    Pulls lightweight aggregate stats from DB
    to give the AI enough context to make good recommendations.
    """
    from models import Customer, Order, Product

    total_customers = db.query(Customer).count()
    total_orders    = db.query(Order).count()

    avg_order = db.execute(
        text("SELECT AVG(amount_paid) FROM orders")
    ).scalar() or 0

    inactive_60 = db.execute(text("""
        SELECT COUNT(*) FROM customers
        WHERE last_purchase_date <= date('now', '-60 days')
    """)).scalar() or 0

    high_value = db.execute(text("""
        SELECT COUNT(*) FROM customers
        WHERE total_spent >= 15000
    """)).scalar() or 0

    new_customers = db.execute(text("""
        SELECT COUNT(*) FROM customers
        WHERE first_purchase_date >= date('now', '-30 days')
    """)).scalar() or 0

    top_craft = db.execute(text("""
        SELECT preferred_craft, COUNT(*) as cnt
        FROM customers
        GROUP BY preferred_craft
        ORDER BY cnt DESC
        LIMIT 1
    """)).fetchone()

    top_region = db.execute(text("""
        SELECT preferred_region, COUNT(*) as cnt
        FROM customers
        GROUP BY preferred_region
        ORDER BY cnt DESC
        LIMIT 1
    """)).fetchone()

    craft_breakdown = db.execute(text("""
        SELECT preferred_craft, COUNT(*) as cnt
        FROM customers
        GROUP BY preferred_craft
        ORDER BY cnt DESC
    """)).fetchall()

    craft_str = "\n".join([
        f"  - {row[0]}: {row[1]} customers"
        for row in craft_breakdown if row[0]
    ])

    return {
        "total_customers":  total_customers,
        "total_orders":     total_orders,
        "avg_order_value":  round(avg_order, 0),
        "inactive_60":      inactive_60,
        "high_value":       high_value,
        "new_customers":    new_customers,
        "top_craft":        top_craft[0] if top_craft else "handloom",
        "top_region":       top_region[0] if top_region else "Rajasthan",
        "craft_breakdown":  craft_str,
    }


def _fallback_recommendations() -> list[dict]:
    """
    Returns hardcoded recommendations if Groq API fails.
    Ensures the dashboard never shows empty recommendations.
    """
    return [
        {
            "segment_name":         "Lapsed Handloom Lovers",
            "segment_description":  "Customers who prefer handloom but haven't purchased in 60+ days",
            "segment_reasoning":    "Handloom is your most popular craft preference. These customers have shown strong affinity but gone quiet. A new collection message will re-engage them effectively.",
            "campaign_name":        "New Handloom Drop — Made For You",
            "message_body":         "Hi {name}, your favourite craft just got a new story. Our latest handloom edit is here — slow-made, natural, yours. Shop now →",
            "channel":              "email"
        },
        {
            "segment_name":         "Festive Season Re-engagement",
            "segment_description":  "Customers who bought festive-mood products but are now inactive",
            "segment_reasoning":    "Festive buyers are high-intent but seasonal. Reaching them before the next festive cycle with curated picks significantly improves win-back rates.",
            "campaign_name":        "Festive Favourites Are Back",
            "message_body":         "Hi {name}, festive season is coming and we've curated the best pieces just for you. New kalamkari and bandhani arrivals waiting →",
            "channel":              "email"
        },
        {
            "segment_name":         "Premium Silk Collectors",
            "segment_description":  "High-spend customers with a preference for silk fabric",
            "segment_reasoning":    "Silk buyers have your highest average order value. Exclusive early access campaigns consistently outperform standard campaigns for this group by 3x.",
            "campaign_name":        "Early Access — New Silk Edit",
            "message_body":         "Hi {name}, before we go live — you get first access to our new silk edit. Exclusively curated for our best customers. Shop early →",
            "channel":              "email"
        }
    ]