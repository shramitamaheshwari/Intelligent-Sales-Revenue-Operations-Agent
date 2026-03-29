"""
Webhook Handler — Async Inbound Signal Receiver
Receives events from CRM / product analytics and triggers the RevOps pipeline.
"""

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import asyncio

router = APIRouter()

class WebhookEvent(BaseModel):
    event_type: str           # e.g., "feature_usage_dropped", "champion_inactive"
    account_id: int
    account_name: str
    cmrr: Optional[float] = 0
    days_since_login: Optional[int] = 0
    signal_value: Optional[float] = None
    raw_email_text: Optional[str] = None  # For NER + NLI processing

# In-memory event log for the System Logs UI
event_log: list[dict] = []


async def _process_event(event: WebhookEvent):
    """
    Background task: run NER anonymization + NLI intent classification,
    then trigger the CrewAI pipeline.
    """
    from models.ner_extractor import anonymize, get_status as ner_status
    from models.sentiment_nli import classify_intent, map_to_signal

    entry = {
        "event_type": event.event_type,
        "account": event.account_name,
        "status": "processing"
    }
    event_log.append(entry)

    # Step 1 — PII Anonymization (runs locally, nothing leaves network)
    if event.raw_email_text:
        clean_text, entities = anonymize(event.raw_email_text)
        entry["entities_masked"] = len(entities)
        entry["ner_backend"] = ner_status()["backend"]

        # Step 2 — Zero-shot NLI intent classification
        classification = classify_intent(clean_text)
        signal = map_to_signal(classification["dominant_signal"])
        entry["detected_signal"] = signal
        entry["nli_backend"] = classification["backend"]
    else:
        # Map event_type directly to signal taxonomy
        signal_map = {
            "feature_usage_dropped": "usage_drop",
            "champion_inactive":     "champion",
            "competitor_mention":    "competitor",
            "payment_overdue":       "payment",
        }
        signal = signal_map.get(event.event_type, "usage_drop")

    entry["signal"] = signal
    entry["status"] = "pipeline_triggered"

    # Step 3 — Trigger CrewAI pipeline (fire-and-forget for demo)
    await asyncio.sleep(0.5)  # Simulate async dispatch latency
    entry["status"] = "completed"


@router.post("/webhook/event")
async def receive_event(event: WebhookEvent, background_tasks: BackgroundTasks):
    """
    Generic event receiver. Triggers the full NER → NLI → CrewAI pipeline.
    """
    background_tasks.add_task(_process_event, event)
    return {
        "status": "accepted",
        "message": f"Event '{event.event_type}' for account '{event.account_name}' queued for processing.",
        "pipeline": "NER → NLI → Orchestrator → HITL"
    }


@router.post("/webhook/champion_inactive")
async def champion_inactive(account_id: int, account_name: str, background_tasks: BackgroundTasks):
    """Champion departure signal — triggers Champion Leaves recovery framework."""
    evt = WebhookEvent(event_type="champion_inactive", account_id=account_id, account_name=account_name)
    background_tasks.add_task(_process_event, evt)
    return {"status": "accepted", "signal": "champion", "framework": "Continuity Bridge"}


@router.post("/webhook/usage_dropped")
async def usage_dropped(account_id: int, account_name: str, background_tasks: BackgroundTasks):
    """Usage drop signal — triggers Abandoned Cart (Empathy Labeling) framework."""
    evt = WebhookEvent(event_type="feature_usage_dropped", account_id=account_id, account_name=account_name)
    background_tasks.add_task(_process_event, evt)
    return {"status": "accepted", "signal": "usage_drop", "framework": "Empathy Labeling"}


@router.get("/webhook/events")
async def get_event_log():
    """Returns the live event processing log for System Logs UI."""
    return {"events": event_log[-50:]}  # Last 50 events
