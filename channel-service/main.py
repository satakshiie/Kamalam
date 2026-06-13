# channel-service/main.py

from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
import httpx
import random
from datetime import datetime

app = FastAPI(title="Kamalam Channel Service")


# ──────────────────────────────────────────────────────────────────────
# PAYLOAD — what the CRM sends us
# ──────────────────────────────────────────────────────────────────────
class SendMessageRequest(BaseModel):
    external_message_id:    str
    recipient:              str
    channel:                str
    body:                   str
    callback_url:           str


# ──────────────────────────────────────────────────────────────────────
# DELIVERY SIMULATION WEIGHTS
# Realistic distribution — not everything succeeds
# ──────────────────────────────────────────────────────────────────────
OUTCOME_WEIGHTS = [
    ("clicked",     15),   # 15% click
    ("opened",      30),   # 30% open but no click
    ("delivered",   40),   # 40% delivered but not opened
    ("failed",      15),   # 15% fail
]

OUTCOMES   = [o[0] for o in OUTCOME_WEIGHTS]
WEIGHTS    = [o[1] for o in OUTCOME_WEIGHTS]


def simulate_outcome() -> str:
    return random.choices(OUTCOMES, weights=WEIGHTS, k=1)[0]


def simulate_delay() -> float:
    # Simulate realistic delivery delay — between 1 and 6 seconds
    return random.uniform(1.0, 6.0)


# ──────────────────────────────────────────────────────────────────────
# SEND ENDPOINT
# CRM calls this for every message in a campaign
# We accept it instantly and simulate delivery in the background
# ──────────────────────────────────────────────────────────────────────
@app.post("/send")
async def send_message(request: SendMessageRequest):
    """
    Accepts a message from the CRM.
    Immediately returns 200 to avoid blocking the CRM.
    Simulates delivery asynchronously in the background.
    """
    asyncio.create_task(
        simulate_delivery(
            external_message_id = request.external_message_id,
            callback_url        = request.callback_url,
        )
    )
    return {
        "accepted":             True,
        "external_message_id":  request.external_message_id
    }


# ──────────────────────────────────────────────────────────────────────
# DELIVERY SIMULATOR
# Runs in the background after /send returns
# Fires callback to CRM with the simulated outcome
# ──────────────────────────────────────────────────────────────────────
async def simulate_delivery(external_message_id: str, callback_url: str):
    """
    Simulates the full delivery lifecycle of a message:

    1. Wait a random delay (mimics real network delivery time)
    2. Pick a random outcome (clicked / opened / delivered / failed)
    3. POST back to the CRM webhook with the outcome + UUID

    The UUID (external_message_id) is how the CRM knows
    which message row to update — never relies on auto-increment IDs.
    """
    await asyncio.sleep(simulate_delay())

    outcome = simulate_outcome()
    now     = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    payload = {
        "external_message_id":  external_message_id,
        "status":               outcome,
        "timestamp":            now,
        "failure_reason":       "Simulated delivery timeout" if outcome == "failed" else None,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                callback_url,
                json    = payload,
                timeout = 5.0
            )
            print(
                f"📬 [{outcome.upper()}] {external_message_id[:8]}... "
                f"→ callback status {response.status_code}"
            )
    except Exception as e:
        print(f"❌ Callback failed for {external_message_id[:8]}...: {e}")


# ──────────────────────────────────────────────────────────────────────
# HEALTH CHECK
# ──────────────────────────────────────────────────────────────────────
@app.get("/")
def read_root():
    return {
        "status":   "online",
        "service":  "Kamalam Channel Service",
        "version":  "1.0.0"
    }