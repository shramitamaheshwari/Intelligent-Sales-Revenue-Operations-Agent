# Intelligent Sales & Revenue Operations Agent

An autonomous multi-agent orchestration layer designed for mid-funnel retention and deal recovery. It is capable of active pipeline monitoring, nuanced conversational intent synthesis, and the deterministic deployment of psychologically optimized revenue recovery plays. Powered by **CrewAI Flows** and tightly gated by **Human-in-the-Loop (HITL)** approvals.

## Hackathon Evaluation Alignment

This project specifically targets mid-funnel retention, deal intelligence, and competitive adaptation over cold outbound prospecting. It demonstrates the following core capabilities:

1. **Deal Intelligence**
   - **Active Webhook Monitoring:** Listens for CRM triggers (`feature_usage_dropped`, `champion_inactive`).
   - **NLP Perception:** Integrates Hugging Face NLI to detect competitor alignment and passive-aggressive sentiment automatically.
   - **Recovery Plays:** Deploys Chris Voss's psychological labeling technique to mitigate risk via the `CopywriterAgent`.

2. **Revenue Retention**
   - **Predictive ML:** Uses a Random Forest classifier in `AnalystAgent` to predict churn probabilty based on mocked usage metrics (CMRR, support ticket velocity).
   - **Intervention Escalation:** The Orchestrator initiates interventions, drafts targeted emails, and heavily relies on a CrewAI flow Human-in-the-Loop (HITL) gate for Account Executive approval.

3. **Competitive Intelligence**
   - **Dynamic Adaptation:** Upon detecting a competitor mention via Zero-Shot NLI, the system flags the orchestrator and applies a strict 75-word cap and strategic pivot rule to the generated copy.

4. **Pipeline Impact & Adaptability**
   - **Self-Healing Loop:** The CrewAI Orchestrator features a self-healing loop using a natural-language router to interpret Account Executive feedback and recursively adapt email drafts.

## Repository Architecture

```text
/intelligent-revops-agent 
├── /agents              # Multi-agent definitions and role/goal setups 
│   ├── analyst_agent.py   # Data ingestion and churn risk scoring prompts 
│   ├── copywriter_agent.py# Sales psychology prompts and email drafting 
│   └── orchestrator.py    # CrewAI Flow logic, routing, and HITL gates 
├── /models              # Local models and inference API connectors 
│   ├── ner_extractor.py   # Minibase.ai CPU-based NER extraction module 
│   └── sentiment_nli.py   # Hugging Face Zero-shot classifier connector 
├── /data                # Synthetic data pipeline and mock CRM environment 
│   ├── generate_mock.py   # Script utilizing Gaussian/Poisson distributions 
│   └── /mock_datasets     # Generated CRM telemetry (CSV/JSON formats) 
├── /api                 # FastAPI web server for frontend/webhook integration 
│   ├── main.py            # Endpoint declarations and server setup 
│   └── webhook_handler.py # Asynchronous webhook catchers for HITL actions 
├── requirements.txt     # Dependency lockfile ensuring reproducibility 
├── architecture.drawio  # Source file for the system architecture diagram 
└── README.md            # Extensive documentation, setup commands, and ROI summary 
```

## Setup Instructions & Execution

### 1. Initialize Workspace
```bash
python -m venv venv
source venv/Scripts/activate # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Generate Synthetic Data
Mock datasets ensure presentation reliability during hackathon evaluations. This script generates `telemetry.csv` using strict realistic distributions.
```bash
python -m data.generate_mock
```

### 3. Run the API & Webhooks
Starts the FastAPI server (accessible at http://localhost:8000/docs for Swagger UI testing).
```bash
python -m api.main
```

### 4. Trigger Orchestration Flow
Post a sample JSON payload to `/webhooks/telemetry` or manually run the orchestrator module directly to witness the CrewAI flow generation and HITL gate check.

## Quantified Impact Model (ROI)

* **Cost Efficiency:** Automating account research and drafting saves ~30 min per stalled deal. For 1,000 at-risk deals/yr at a $75/hr Account Executive rate, operational savings eclipse $35,000 annually.
* **Revenue Recovery:** Recovering merely 15% more churn on a $500,000 MRR risk pool yields $75,000 incrementally.
* **Total Program ROI:** By investing a conservative baseline implementation cost, organizations can expect over 250%+ pure ROI in the first fiscal year, pivoting their CRM from a static database into an autonomous revenue engine.
