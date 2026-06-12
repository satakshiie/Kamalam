# backend/models.py

from sqlalchemy import (
    Column, Integer, Text, Float, 
    ForeignKey, DateTime, func
)
from sqlalchemy.orm import relationship
from database import Base

# ─────────────────────────────────────────
# 1. DESIGNERS
# ─────────────────────────────────────────
class Designer(Base):
    __tablename__ = "designers"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    name            = Column(Text, nullable=False)
    brand_name      = Column(Text, nullable=False)
    origin_state    = Column(Text)
    craft_specialty = Column(Text)       # e.g. "Ikat weaving", "Chikankari"
    aesthetic_tags  = Column(Text)       # e.g. "earthy, minimal, handcrafted"
    is_featured     = Column(Integer, default=0)
    joined_at       = Column(DateTime, server_default=func.now())

    # Relationships
    products        = relationship("Product", back_populates="designer")
    orders          = relationship("Order", back_populates="designer")


# ─────────────────────────────────────────
# 2. PRODUCTS
# ─────────────────────────────────────────
class Product(Base):
    __tablename__ = "products"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    designer_id     = Column(Integer, ForeignKey("designers.id"))
    name            = Column(Text, nullable=False)  # e.g. "Indigo Block Print Kurta"

    # Aesthetic Metadata
    craft_type      = Column(Text)    # e.g. "block print", "handloom"
    fabric          = Column(Text)    # e.g. "khadi", "silk", "linen"
    region_origin   = Column(Text)    # e.g. "Jaipur", "Banaras", "Kutch"
    aesthetic_mood  = Column(Text)    # e.g. "festive", "everyday", "bridal"
    color_palette   = Column(Text)    # e.g. "earthy", "pastels", "bold"
    gender_target   = Column(Text)    # e.g. "womenswear", "menswear", "unisex"

    price           = Column(Float)
    stock           = Column(Integer, default=0)
    created_at      = Column(DateTime, server_default=func.now())

    # Relationships
    designer        = relationship("Designer", back_populates="products")
    orders          = relationship("Order", back_populates="product")


# ─────────────────────────────────────────
# 3. CUSTOMERS
# ─────────────────────────────────────────
class Customer(Base):
    __tablename__ = "customers"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    name            = Column(Text, nullable=False)
    email           = Column(Text, unique=True, nullable=False)
    phone           = Column(Text)
    city            = Column(Text)
    state           = Column(Text)

    # Aesthetic Profile
    style_affinity      = Column(Text)  # e.g. "handloom", "contemporary", "fusion"
    preferred_fabric    = Column(Text)  # e.g. "cotton", "silk", "khadi"
    preferred_craft     = Column(Text)  # e.g. "block print", "kalamkari"
    preferred_region    = Column(Text)  # e.g. "Rajasthan", "Bengal"
    size_preference     = Column(Text)
    gender_preference   = Column(Text)

    # Behaviour
    total_orders        = Column(Integer, default=0)
    total_spent         = Column(Float, default=0.0)
    avg_order_value     = Column(Float, default=0.0)
    last_purchase_date  = Column(Text)
    first_purchase_date = Column(Text)

    created_at          = Column(DateTime, server_default=func.now())

    # Relationships
    orders      = relationship("Order", back_populates="customer")
    messages    = relationship("Message", back_populates="customer")


# ─────────────────────────────────────────
# 4. ORDERS
# ─────────────────────────────────────────
class Order(Base):
    __tablename__ = "orders"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    customer_id     = Column(Integer, ForeignKey("customers.id"))
    product_id      = Column(Integer, ForeignKey("products.id"))
    designer_id     = Column(Integer, ForeignKey("designers.id"))

    quantity        = Column(Integer, default=1)
    amount_paid     = Column(Float)
    order_date      = Column(Text)

    # Pattern detection helpers for AI
    is_repeat_craft     = Column(Integer, default=0)  # bought same craft before?
    is_repeat_designer  = Column(Integer, default=0)  # bought same designer before?

    created_at      = Column(DateTime, server_default=func.now())

    # Relationships
    customer    = relationship("Customer", back_populates="orders")
    product     = relationship("Product", back_populates="orders")
    designer    = relationship("Designer", back_populates="orders")


# ─────────────────────────────────────────
# 5. SEGMENTS
# ─────────────────────────────────────────
class Segment(Base):
    __tablename__ = "segments"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    name            = Column(Text, nullable=False)   # e.g. "Handloom Loyalists"
    description     = Column(Text)

    created_by      = Column(Text, default="ai")     # "ai" or "manual"
    ai_reasoning    = Column(Text)                   # why AI picked this segment

    filters         = Column(Text)
    # Stored as JSON string
    # e.g. '{"preferred_craft": "block print", "days_inactive": 30}'

    customer_count  = Column(Integer, default=0)
    created_at      = Column(DateTime, server_default=func.now())

    # Relationships
    campaigns   = relationship("Campaign", back_populates="segment")


# ─────────────────────────────────────────
# 6. CAMPAIGNS
# ─────────────────────────────────────────
class Campaign(Base):
    __tablename__ = "campaigns"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    segment_id      = Column(Integer, ForeignKey("segments.id"))

    name            = Column(Text, nullable=False)
    message_body    = Column(Text, nullable=False)   # AI drafted message
    channel         = Column(Text, default="email")  # "email", "sms", "whatsapp"

    # AI metadata
    ai_suggested        = Column(Integer, default=1)
    ai_recommendation   = Column(Text)   # full AI reasoning shown to marketer
    approved_by_user    = Column(Integer, default=0)

    # Status flow: draft → approved → sending → completed
    status          = Column(Text, default="draft")

    scheduled_at    = Column(Text)
    sent_at         = Column(Text)
    created_at      = Column(DateTime, server_default=func.now())

    # Relationships
    segment     = relationship("Segment", back_populates="campaigns")
    messages    = relationship("Message", back_populates="campaign")
    analytics   = relationship("CampaignAnalytics", back_populates="campaign", uselist=False)


# ─────────────────────────────────────────
# 7. MESSAGES
# ─────────────────────────────────────────
class Message(Base):
    __tablename__ = "messages"

    id                      = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id             = Column(Integer, ForeignKey("campaigns.id"))
    customer_id             = Column(Integer, ForeignKey("customers.id"))

    external_message_id     = Column(Text, unique=True, nullable=False)
    # ↑ UUID generated in Python before sending to channel service
    # Channel service returns this same UUID in its callback
    # Guarantees conflict-free mapping across two services

    status          = Column(Text, default="pending")
    # pending → sent → delivered → opened → clicked → failed

    sent_at         = Column(Text)
    delivered_at    = Column(Text)
    opened_at       = Column(Text)
    clicked_at      = Column(Text)
    failed_at       = Column(Text)
    failure_reason  = Column(Text)

    created_at      = Column(DateTime, server_default=func.now())

    # Relationships
    campaign    = relationship("Campaign", back_populates="messages")
    customer    = relationship("Customer", back_populates="messages")


# ─────────────────────────────────────────
# 8. CAMPAIGN ANALYTICS
# ─────────────────────────────────────────
class CampaignAnalytics(Base):
    __tablename__ = "campaign_analytics"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), unique=True)

    # ── NO tally columns here (total_sent, total_delivered etc.) ──
    # Those are calculated live via COUNT on messages table
    # Avoids SQLite write contention on concurrent webhook callbacks

    # Heavy post-campaign AI insights only
    top_responding_craft    = Column(Text)
    top_responding_region   = Column(Text)
    top_responding_mood     = Column(Text)
    ai_post_campaign_notes  = Column(Text)  # AI summary after campaign ends

    updated_at  = Column(DateTime, server_default=func.now())

    # Relationships
    campaign    = relationship("Campaign", back_populates="analytics")


# ─────────────────────────────────────────
# CREATE ALL TABLES
# ─────────────────────────────────────────
from database import engine
Base.metadata.create_all(bind=engine)
# ↑ Reads all classes above and creates the tables in indie_crm.db
# Safe to run multiple times — only creates tables that don't exist yet