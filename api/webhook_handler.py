from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
import sys
import os

# Add parent directory to path to import agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.orchestrator import RevenueRecoveryFlow

router = APIRouter()

class TelemetryPayload(BaseModel):
    account_id: str
    event_type: str
    data: dict

def trigger_crew_flow(payload: dict):
    # This invokes the CrewAI Flow asynchronously
    flow = RevenueRecoveryFlow()
    flow.state['account_id'] = payload.get('account_id')
    flow.state['event_type'] = payload.get('event_type')
    flow.kickoff()

@router.post("/telemetry")
async def receive_telemetry(payload: TelemetryPayload, background_tasks: BackgroundTasks):
    """
    Webhook to receive feature_usage_dropped, champion_inactive etc.
    Triggers Agent 4 Orchestrator Flow.
    """
    if payload.event_type in ["feature_usage_dropped", "champion_inactive"]:
        # Run CrewAI flow in background to not block webhook response
        background_tasks.add_task(trigger_crew_flow, payload.model_dump())
        return {"status": "Flow triggered", "risk_event": payload.event_type}
    
    return {"status": "Event logged", "action": "None"}
