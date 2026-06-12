# backend/seed.py

import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import (
    Base, Designer, Product, Customer, Order,
    Segment, Campaign, Message, CampaignAnalytics
)
import uuid
import json

# ──────────────────────────────────────────────────────────────────────
# CONSTANTS — Aesthetic vocabulary for Kamalam
# ──────────────────────────────────────────────────────────────────────

CRAFT_TYPES = [
    "block print", "kalamkari", "ikat", "chikankari",
    "bandhani", "ajrakh", "kantha", "phulkari",
    "zardozi", "handloom"
]

FABRICS = [
    "khadi", "silk", "linen", "cotton",
    "chanderi", "mul mul", "tussar", "organza"
]

REGIONS = [
    "Rajasthan", "Bengal", "Gujarat", "Uttar Pradesh",
    "Telangana", "Kerala", "Punjab", "Odisha"
]

AESTHETIC_MOODS = [
    "festive", "everyday", "workwear",
    "bridal", "resort", "indo-western"
]

COLOR_PALETTES = [
    "earthy", "pastels", "bold", "monochrome",
    "jewel tones", "muted neutrals"
]

STYLE_AFFINITIES = [
    "handloom", "contemporary", "fusion",
    "traditional", "streetwear", "minimalist"
]

CITIES_STATES = [
    ("Mumbai", "Maharashtra"),
    ("Chennai", "Tamil Nadu"),
    ("Jaipur", "Rajasthan"),
    ("Kolkata", "West Bengal"),
    ("Bangalore", "Karnataka"),
    ("Hyderabad", "Telangana"),
    ("Ahmedabad", "Gujarat"),
    ("Delhi", "Delhi"),
    ("Kochi", "Kerala"),
    ("Bhubaneswar", "Odisha"),
    ("Lucknow", "Uttar Pradesh"),
    ("Chandigarh", "Punjab"),
]

GENDERS = ["womenswear", "menswear", "unisex"]
SIZES   = ["XS", "S", "M", "L", "XL", "XXL"]


# ──────────────────────────────────────────────────────────────────────
# DESIGNER + PRODUCT DATA
# ──────────────────────────────────────────────────────────────────────

DESIGNER_DATA = [
    {
        "name": "Priya Nair",
        "brand_name": "Mitti Collective",
        "origin_state": "Kerala",
        "craft_specialty": "Handloom weaving",
        "aesthetic_tags": "earthy, minimal, slow fashion",
        "is_featured": 1,
        "products": [
            {
                "name": "Indigo Handloom Kurta",
                "craft_type": "handloom", "fabric": "cotton",
                "region_origin": "Kerala", "aesthetic_mood": "everyday",
                "color_palette": "earthy", "gender_target": "womenswear",
                "price": 2800, "stock": 40
            },
            {
                "name": "Natural Dye Linen Co-ord",
                "craft_type": "handloom", "fabric": "linen",
                "region_origin": "Kerala", "aesthetic_mood": "resort",
                "color_palette": "muted neutrals", "gender_target": "unisex",
                "price": 4200, "stock": 25
            },
        ]
    },
    {
        "name": "Arjun Mehta",
        "brand_name": "Rang Sutra Studio",
        "origin_state": "Rajasthan",
        "craft_specialty": "Block printing & Ajrakh",
        "aesthetic_tags": "bold, artisanal, heritage",
        "is_featured": 1,
        "products": [
            {
                "name": "Ajrakh Block Print Shirt",
                "craft_type": "ajrakh", "fabric": "mul mul",
                "region_origin": "Rajasthan", "aesthetic_mood": "everyday",
                "color_palette": "earthy", "gender_target": "menswear",
                "price": 3200, "stock": 30
            },
            {
                "name": "Bagru Print Wrap Skirt",
                "craft_type": "block print", "fabric": "cotton",
                "region_origin": "Rajasthan", "aesthetic_mood": "indo-western",
                "color_palette": "bold", "gender_target": "womenswear",
                "price": 2600, "stock": 35
            },
        ]
    },
    {
        "name": "Sneha Banerjee",
        "brand_name": "Taar Studio",
        "origin_state": "West Bengal",
        "craft_specialty": "Kantha embroidery & Tant weaving",
        "aesthetic_tags": "delicate, literary, Bengali heritage",
        "is_featured": 0,
        "products": [
            {
                "name": "Kantha Stitch Saree",
                "craft_type": "kantha", "fabric": "silk",
                "region_origin": "Bengal", "aesthetic_mood": "festive",
                "color_palette": "pastels", "gender_target": "womenswear",
                "price": 7800, "stock": 15
            },
            {
                "name": "Tant Cotton Kurta Set",
                "craft_type": "handloom", "fabric": "cotton",
                "region_origin": "Bengal", "aesthetic_mood": "everyday",
                "color_palette": "muted neutrals", "gender_target": "womenswear",
                "price": 3400, "stock": 20
            },
        ]
    },
    {
        "name": "Vikram Choudhary",
        "brand_name": "Neela Project",
        "origin_state": "Gujarat",
        "craft_specialty": "Bandhani & Ikat",
        "aesthetic_tags": "vibrant, festive, community-made",
        "is_featured": 0,
        "products": [
            {
                "name": "Bandhani Silk Dupatta",
                "craft_type": "bandhani", "fabric": "silk",
                "region_origin": "Gujarat", "aesthetic_mood": "festive",
                "color_palette": "jewel tones", "gender_target": "womenswear",
                "price": 1800, "stock": 50
            },
            {
                "name": "Ikat Merino Shawl",
                "craft_type": "ikat", "fabric": "silk",
                "region_origin": "Gujarat", "aesthetic_mood": "resort",
                "color_palette": "bold", "gender_target": "unisex",
                "price": 5500, "stock": 18
            },
        ]
    },
    {
        "name": "Lakshmi Reddy",
        "brand_name": "Andha Studio",
        "origin_state": "Telangana",
        "craft_specialty": "Kalamkari & Pochampally Ikat",
        "aesthetic_tags": "mythological, expressive, handpainted",
        "is_featured": 1,
        "products": [
            {
                "name": "Kalamkari Kurta",
                "craft_type": "kalamkari", "fabric": "cotton",
                "region_origin": "Telangana", "aesthetic_mood": "festive",
                "color_palette": "earthy", "gender_target": "womenswear",
                "price": 4100, "stock": 22
            },
            {
                "name": "Pochampally Ikat Shirt",
                "craft_type": "ikat", "fabric": "cotton",
                "region_origin": "Telangana", "aesthetic_mood": "workwear",
                "color_palette": "bold", "gender_target": "menswear",
                "price": 3600, "stock": 28
            },
        ]
    },
]

# ──────────────────────────────────────────────────────────────────────
# CUSTOMER NAME POOL
# ──────────────────────────────────────────────────────────────────────

FIRST_NAMES = [
    "Ananya", "Rohan", "Priya", "Arjun", "Meera", "Karthik",
    "Divya", "Siddharth", "Kavya", "Rahul", "Nisha", "Vikram",
    "Pooja", "Aditya", "Shreya", "Nikhil", "Anjali", "Ravi",
    "Deepika", "Suresh", "Lakshmi", "Amit", "Sunita", "Rajesh",
    "Ishaan", "Tanvi", "Varun", "Kritika", "Harish", "Sneha"
]

LAST_NAMES = [
    "Sharma", "Nair", "Reddy", "Patel", "Iyer", "Mehta",
    "Banerjee", "Choudhary", "Verma", "Pillai", "Das", "Joshi",
    "Agarwal", "Krishnan", "Gupta", "Singh", "Rao", "Shah",
    "Chatterjee", "Malhotra"
]


# ──────────────────────────────────────────────────────────────────────
# HELPER — random past date
# ──────────────────────────────────────────────────────────────────────

def random_past_date(max_days_ago: int = 365) -> str:
    delta = random.randint(1, max_days_ago)
    return (datetime.now() - timedelta(days=delta)).strftime("%Y-%m-%d")


# ──────────────────────────────────────────────────────────────────────
# SEEDER
# ──────────────────────────────────────────────────────────────────────

def seed():
    db: Session = SessionLocal()

    print("🌱 Kamalam CRM — starting seed...")

    # ── WIPE existing data (order matters due to foreign keys) ──
    print("🗑️  Clearing existing data...")
    db.query(CampaignAnalytics).delete()
    db.query(Message).delete()
    db.query(Campaign).delete()
    db.query(Segment).delete()
    db.query(Order).delete()
    db.query(Product).delete()
    db.query(Customer).delete()
    db.query(Designer).delete()
    db.commit()

    # ── 1. SEED DESIGNERS + PRODUCTS ──
    print("👗 Seeding designers and products...")
    all_products = []

    for d_data in DESIGNER_DATA:
        products_data = d_data.pop("products")

        designer = Designer(**d_data)
        db.add(designer)
        db.flush()  # get designer.id without full commit

        for p_data in products_data:
            product = Product(designer_id=designer.id, **p_data)
            db.add(product)
            db.flush()
            all_products.append(product)

    db.commit()
    print(f"   ✅ {len(DESIGNER_DATA)} designers, {len(all_products)} products")

    # ── 2. SEED CUSTOMERS ──
    print("👤 Seeding customers...")
    customers = []

    for i in range(80):
        first   = random.choice(FIRST_NAMES)
        last    = random.choice(LAST_NAMES)
        city, state = random.choice(CITIES_STATES)

        customer = Customer(
            name                = f"{first} {last}",
            email               = f"{first.lower()}.{last.lower()}{i}@example.com",
            phone               = f"+91 9{random.randint(100000000, 999999999)}",
            city                = city,
            state               = state,
            style_affinity      = random.choice(STYLE_AFFINITIES),
            preferred_fabric    = random.choice(FABRICS),
            preferred_craft     = random.choice(CRAFT_TYPES),
            preferred_region    = random.choice(REGIONS),
            size_preference     = random.choice(SIZES),
            gender_preference   = random.choice(GENDERS),
            total_orders        = 0,
            total_spent         = 0.0,
            avg_order_value     = 0.0,
            first_purchase_date = random_past_date(365),
            last_purchase_date  = random_past_date(90),
        )
        db.add(customer)
        customers.append(customer)

    db.commit()
    print(f"   ✅ {len(customers)} customers")

    # ── 3. SEED ORDERS ──
    print("🛒 Seeding orders...")
    order_count = 0

    for customer in customers:
        # Each customer gets 1–5 orders
        num_orders = random.randint(1, 5)
        customer_crafts_bought = []

        for _ in range(num_orders):
            product     = random.choice(all_products)
            order_date  = random_past_date(300)

            is_repeat_craft     = 1 if product.craft_type in customer_crafts_bought else 0
            is_repeat_designer  = 1 if any(
                o.designer_id == product.designer_id
                for o in db.query(Order).filter_by(customer_id=customer.id).all()
            ) else 0

            order = Order(
                customer_id         = customer.id,
                product_id          = product.id,
                designer_id         = product.designer_id,
                quantity            = random.randint(1, 2),
                amount_paid         = product.price * random.randint(1, 2),
                order_date          = order_date,
                is_repeat_craft     = is_repeat_craft,
                is_repeat_designer  = is_repeat_designer,
            )
            db.add(order)
            customer_crafts_bought.append(product.craft_type)

            # Update customer stats
            customer.total_orders   += 1
            customer.total_spent    += order.amount_paid

        customer.avg_order_value = round(
            customer.total_spent / customer.total_orders, 2
        )
        order_count += num_orders

    db.commit()
    print(f"   ✅ {order_count} orders")

    # ── 4. SEED AI-GENERATED SEGMENTS ──
    print("🎯 Seeding AI segments...")

    segments_data = [
        {
            "name": "Handloom Loyalists",
            "description": "Customers who consistently buy handloom products and have made repeat purchases",
            "created_by": "ai",
            "ai_reasoning": "These customers have shown strong affinity for handloom craft across multiple orders. High lifetime value and repeat purchase rate make them ideal for new handloom collection launches.",
            "filters": json.dumps({
                "preferred_craft": "handloom",
                "min_orders": 2
            }),
        },
        {
            "name": "Lapsed Festive Shoppers",
            "description": "Customers who bought festive-mood products but haven't purchased in 60+ days",
            "created_by": "ai",
            "ai_reasoning": "This segment last engaged during a festive season purchase cycle. With an upcoming festive period approaching, a targeted re-engagement campaign with new festive arrivals has high conversion potential.",
            "filters": json.dumps({
                "aesthetic_mood": "festive",
                "days_inactive": 60
            }),
        },
        {
            "name": "Block Print Enthusiasts",
            "description": "Customers whose preferred craft is block print with above average spend",
            "created_by": "ai",
            "ai_reasoning": "Block print customers show strong regional loyalty and tend to explore across designers. A curated multi-designer block print edit would resonate deeply with this group.",
            "filters": json.dumps({
                "preferred_craft": "block print",
                "min_spend": 5000
            }),
        },
        {
            "name": "New Customer Nurture",
            "description": "Customers who placed their first order in the last 30 days",
            "created_by": "ai",
            "ai_reasoning": "First-time buyers need a follow-up touchpoint within 30 days to convert to repeat customers. A warm welcome message highlighting the brand story and new arrivals increases second purchase probability significantly.",
            "filters": json.dumps({
                "days_since_first_order": 30,
                "total_orders": 1
            }),
        },
        {
            "name": "High Value Silk Buyers",
            "description": "Customers with total spend above ₹15,000 who prefer silk fabric",
            "created_by": "ai",
            "ai_reasoning": "This is your premium tier. Silk buyers have the highest average order value on the platform. Exclusive early access campaigns and designer spotlight messages perform best with this segment.",
            "filters": json.dumps({
                "preferred_fabric": "silk",
                "min_total_spent": 15000
            }),
        },
    ]

    segments = []
    for s_data in segments_data:
        # Count customers matching this segment roughly
        customer_count = random.randint(8, 35)
        segment = Segment(**s_data, customer_count=customer_count)
        db.add(segment)
        segments.append(segment)

    db.commit()
    print(f"   ✅ {len(segments)} segments")

    # ── 5. SEED AI-SUGGESTED CAMPAIGNS ──
    print("📢 Seeding campaigns...")

    campaigns_data = [
        {
            "segment": segments[0],  # Handloom Loyalists
            "name": "New Handloom Drop — Mitti Collective",
            "message_body": "Hi {name}, the new Mitti Collective handloom edit just dropped — pieces you'll love. Natural dyes, slow-made, yours first. Shop the drop →",
            "ai_recommendation": "Handloom Loyalists have a 68% repeat purchase rate. Mitti Collective's new drop aligns directly with their craft preference. Recommend sending Tuesday morning for highest open rates.",
            "status": "completed",
            "approved_by_user": 1,
        },
        {
            "segment": segments[1],  # Lapsed Festive Shoppers
            "name": "Festive Re-engagement — Come Back",
            "message_body": "Hi {name}, festive season is around the corner and we've saved the best pieces for you. New kalamkari and bandhani arrivals — exclusively curated for your taste. Explore now →",
            "ai_recommendation": "This segment has been inactive for 60+ days but their last purchase was festive-mood. Timing this campaign 6 weeks before Diwali season maximises win-back probability.",
            "status": "sending",
            "approved_by_user": 1,
        },
        {
            "segment": segments[2],  # Block Print Enthusiasts
            "name": "Block Print Edit — 3 Designers, 1 Story",
            "message_body": "Hi {name}, we curated a block print edit across three of our finest designers — Rajasthan to Bengal, each piece hand-stamped. Made for someone with your eye. View the edit →",
            "ai_recommendation": "Block print buyers explore across designers more than any other segment. A multi-designer curated edit creates discovery while staying within their craft comfort zone.",
            "status": "draft",
            "approved_by_user": 0,
        },
        {
            "segment": segments[3],  # New Customer Nurture
            "name": "Welcome to Kamalam — Your First Story",
            "message_body": "Hi {name}, welcome to Kamalam. Every piece here carries a craft tradition and a maker's name. We'd love to help you find your next favourite. Here's what's new this week →",
            "ai_recommendation": "New customers who receive a brand story message within 30 days are 2.4x more likely to make a second purchase. Keep tone warm and story-first, not promotional.",
            "status": "draft",
            "approved_by_user": 0,
        },
        {
            "segment": segments[4],  # High Value Silk Buyers
            "name": "Early Access — Silk Edit for Our Best Customers",
            "message_body": "Hi {name}, before we go live — you get first access. Our new silk edit from Taar Studio and Neela Project is live exclusively for you for the next 48 hours. Shop early access →",
            "ai_recommendation": "Premium silk buyers respond strongly to exclusivity framing. Early access campaigns for this segment consistently outperform standard campaigns by 3x click rate.",
            "status": "approved",
            "approved_by_user": 1,
        },
    ]

    campaigns = []
    for c_data in campaigns_data:
        seg = c_data.pop("segment")
        campaign = Campaign(
            segment_id      = seg.id,
            channel         = "email",
            ai_suggested    = 1,
            sent_at         = datetime.now().strftime("%Y-%m-%d") if c_data["status"] in ["sending", "completed"] else None,
            **c_data
        )
        db.add(campaign)
        campaigns.append(campaign)

    db.commit()
    print(f"   ✅ {len(campaigns)} campaigns")

    # ── 6. SEED MESSAGES FOR COMPLETED/SENDING CAMPAIGNS ──
    print("📨 Seeding messages...")
    message_count = 0

    STATUS_WEIGHTS_COMPLETED = ["delivered", "delivered", "delivered", "opened", "opened", "clicked", "failed"]
    STATUS_WEIGHTS_SENDING   = ["sent", "delivered", "delivered", "opened", "clicked", "pending", "failed"]

    for campaign in campaigns:
        if campaign.status not in ["completed", "sending"]:
            continue

        weights = STATUS_WEIGHTS_COMPLETED if campaign.status == "completed" else STATUS_WEIGHTS_SENDING
        sample_customers = random.sample(customers, min(campaign.segment.customer_count, len(customers)))

        for customer in sample_customers:
            status = random.choice(weights)
            now    = datetime.now()

            message = Message(
                campaign_id         = campaign.id,
                customer_id         = customer.id,
                external_message_id = str(uuid.uuid4()),
                status              = status,
                sent_at             = now.strftime("%Y-%m-%d %H:%M:%S"),
                delivered_at        = now.strftime("%Y-%m-%d %H:%M:%S") if status in ["delivered", "opened", "clicked"] else None,
                opened_at           = now.strftime("%Y-%m-%d %H:%M:%S") if status in ["opened", "clicked"] else None,
                clicked_at          = now.strftime("%Y-%m-%d %H:%M:%S") if status == "clicked" else None,
                failed_at           = now.strftime("%Y-%m-%d %H:%M:%S") if status == "failed" else None,
                failure_reason      = "Delivery timeout" if status == "failed" else None,
            )
            db.add(message)
            message_count += 1

    db.commit()
    print(f"   ✅ {message_count} messages")

    # ── 7. SEED POST-CAMPAIGN ANALYTICS (completed only) ──
    print("📊 Seeding campaign analytics...")

    for campaign in campaigns:
        if campaign.status != "completed":
            continue

        analytics = CampaignAnalytics(
            campaign_id             = campaign.id,
            top_responding_craft    = random.choice(CRAFT_TYPES),
            top_responding_region   = random.choice(REGIONS),
            top_responding_mood     = random.choice(AESTHETIC_MOODS),
            ai_post_campaign_notes  = (
                f"Campaign performed above average for this segment. "
                f"{random.choice(REGIONS)} customers showed highest engagement. "
                f"Recommend following up with a designer spotlight from the same craft tradition."
            )
        )
        db.add(analytics)

    db.commit()
    print("   ✅ Campaign analytics seeded")

    db.close()

    print("")
    print("✅ Kamalam CRM seed complete!")
    print(f"   👗 {len(DESIGNER_DATA)} designers")
    print(f"   📦 {len(all_products)} products")
    print(f"   👤 80 customers")
    print(f"   🛒 {order_count} orders")
    print(f"   🎯 {len(segments)} AI segments")
    print(f"   📢 {len(campaigns)} campaigns")
    print(f"   📨 {message_count} messages")


# ──────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    seed()