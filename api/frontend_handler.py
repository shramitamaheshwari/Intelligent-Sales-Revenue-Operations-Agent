from fastapi import APIRouter
from pydantic import BaseModel
import asyncio
import os
import sys
from pathlib import Path

# Resolve repo root so CSV reads work regardless of CWD
REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "data" / "mock_datasets" / "telemetry.csv"

try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from agents.orchestrator import RevenueRecoveryFlow
    from agents.analyst_agent import ChurnScoringPipeline
    import langchain_groq # ensuring groq is loaded
    CREWAI_AVAILABLE = True
except Exception as e:
    print(f"Error loading agents: {e}")
    CREWAI_AVAILABLE = False

router = APIRouter()

class GenerateRequest(BaseModel):
    account_id: int
    signal: str
    name: str

# Instantiate the live pipeline
ml_pipeline = None
if CREWAI_AVAILABLE:
    try:
        pipeline = ChurnScoringPipeline()
        pipeline.train("data/mock_datasets/telemetry.csv")
        ml_pipeline = pipeline
    except Exception as e:
        print(f"ML Pipeline Initialization Error: {e}")

@router.get("/accounts")
async def get_accounts():
    """
    Dynamically loads and evaluates accounts natively from the mock CRM dataset.
    """
    import pandas as pd
    try:
        df = pd.read_csv(str(CSV_PATH))
    except Exception as e:
        print(f"CSV load failed ({e}), using inline fallback")
        df = pd.DataFrame([
            {"CMRR_mean": 4200, "days_since_last_login": 18, "support_ticket_velocity": 4.2},
            {"CMRR_mean": 2800, "days_since_last_login": 22, "support_ticket_velocity": 1.1},
            {"CMRR_mean": 6100, "days_since_last_login": 5,  "support_ticket_velocity": 0.8},
            {"CMRR_mean": 1200, "days_since_last_login": 9,  "support_ticket_velocity": 2.3},
        ])

    accounts = []
    # Generate varied signals and names deterministically based on index for demo purposes
    names = ["AcmeCorp", "Nexus Analytics", "Stratos Inc.", "PineCrest Labs", "Vortex Systems", "Quantum Bridge", "Aero Dynamic", "Pulse Networks"]
    signals = ["usage_drop", "champion", "competitor", "payment"]
    tones = ["passive-aggressive", "neutral", "positive"]

    for idx, row in df.iterrows():
        # Prevent massive payloads crashing the UI, limit to 25 for demo visibility
        if idx >= 50:   # Show up to 50 accounts for richer ROI numbers
            break
            
        cmrr = float(row.get('CMRR_mean', 3000))
        days = float(row.get('days_since_last_login', 10))
        tickets = float(row.get('support_ticket_velocity', 1.0))
        
        acc = {
            "id": int(idx)+1,
            "name": names[int(idx) % len(names)],
            "tier": "Enterprise" if cmrr > 4000 else "Mid-Market",
            "cmrr": cmrr,
            "risk": 0.5, # Default, overwritten by ML below
            "signal": signals[int(idx) % len(signals)],
            "tone": tones[int(idx) % len(tones)],
            "days": int(days),
            "tickets": round(tickets, 1),
            "adopt": 50 + int((idx * 7) % 40),
            "cmrr_trend": -5 if days > 15 else 5,
            "competitor": (idx % 3 == 0),
            "champion": (idx % 2 == 0)
        }
        
        # DYNAMIC ML INTEGRATION OVERRIDE
        if ml_pipeline:
            live_risk = ml_pipeline.predict_risk([cmrr, tickets, days])
            acc["risk"] = float(live_risk)
            
        accounts.append(acc)

    # Sort descending by risk score to highlight churners at the top
    accounts = sorted(accounts, key=lambda x: x["risk"], reverse=True)
            
    return {"status": "success", "accounts": accounts}

@router.post("/generate")
async def generate_draft(req: GenerateRequest):
    """
    Attempts to execute the actual local CrewAI Orchestrator with Groq LLM.
    If the API limits out or keys are missing, we gracefully return the Resilient Fallback mock.
    """
    signal = req.signal
    
    if CREWAI_AVAILABLE and os.getenv("GROQ_API_KEY"):
        try:
            # We execute a live kickoff bypassing standard flow delays
            from agents.copywriter_agent import CopywriterAgentBuilder
            from crewai import Task, Crew
            
            agent = CopywriterAgentBuilder.build_agent()
            task = Task(
                description=f"Draft a recovery email based on this account context: Account: {req.name}, Risk Signal: {signal}.",
                expected_output="A well-crafted recovery email addressing the risk context using Chris Voss labeling.",
                agent=agent
            )
            crew = Crew(agents=[agent], tasks=[task])
            result = crew.kickoff()
            
            return {
                "status": "success",
                "draft": {
                    "subject": "Agent Generated Draft",
                    "body": str(result),
                    "framework": "Groq LLM Native",
                    "color": "purple"
                }
            }
        except Exception as e:
            print(f"Agent Execution Failed, falling back: {e}")

    # RESILIENT MOCK FALLBACK
    await asyncio.sleep(1.5)
    
    if signal == "competitor":
        subject = "Fair enough — they are a strong choice."
        body = f"Hi {req.name.split(' ')[0]},\n\nHonestly? Stratos has built a remarkably strong product over the last year. I would definitely be evaluating them too.\n\nWhere we typically see enterprise teams switch to us, however, is when standard API throttling becomes a bottleneck at a massive scale. \n\nAre you entirely opposed to a brief 15-minute technical comparison to see the difference before you decide? No pressure either way.\n\n[AE Name]"
        framework = "Competitor"
        color = "red"
    elif signal == "champion":
        subject = "Overwhelmed with the transition?"
        body = f"Hi {req.name.split(' ')[0]},\n\nIt seems like you are inheriting a massive amount of legacy systems right now and are likely overwhelmed with vendor audits and a dozen competing priorities from the board. \n\nI'm reaching out because behind the scenes, we've been managing your auto-renewal compliance reporting for the {req.name} backend. I'd hate for that specific workflow to break entirely during a leadership transition.\n\nCan I offer a completely zero-pressure briefing? No pitch, no deck, just continuity context. Does a quick yes or no work for you?\n\n[AE Name]"
        framework = "Champion Leaves"
        color = "blue"
    else: 
        subject = "Did we break something in the UI?"
        body = f"Hi {req.name.split(' ')[0]},\n\nThis might be a complete waste of your time, but my tracking caught a severe 60% drop in your team's usage of the Core Analytics Module since Tuesday. Did our new navigation layout cause a bottleneck for your workflow? \n\nIf the dashboard is triggering friction rather than helping, I genuinely need to know so our engineers can fix it immediately. \n\nNo agenda or meeting request. Just let me know if we broke something.\n\n[AE Name]"
        framework = "Usage Drop"
        color = "orange"
        
    return {
        "status": "success",
        "draft": {
            "subject": subject,
            "body": body,
            "framework": framework,
            "color": color
        }
    }
