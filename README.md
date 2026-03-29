# Intelligent Sales & Revenue Operations Agent

An autonomous multi-agent orchestration layer capable of autonomous prospect research, nuanced conversational intent synthesis, and the deployment of psychologically optimized revenue recovery plays. Built deterministically via **CrewAI Flows** and tightly gated by **Human-in-the-Loop (HITL)** approvals.

## 🚀 Repository Architecture

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

## 🧠 System Mechanics
1. **Pillar 1: B2B Churn Feature Engineering**: Python-driven synthetic CRM environments leveraging Gaussian and Poisson distributions to predict leading drop-off indicators.
2. **Pillar 2: Sentiment NLP**: Hugging Face inference endpoints identifying competitor mentions via zero-shot classification and detecting passive aggression using DistilBERT. PII anonymization handled by local NER extraction.
3. **Pillar 3: Sales Psychology**: LLMs instructed specifically with Chris Voss labeling methodologies to diffuse CRM risk scenarios without generically pitching software features.
4. **Pillar 4: Multi-Agent Orchestration**: CrewAI flows routing actions across specialized agents seamlessly up until the Human-in-the-loop checkpoint. An integrated router model evaluates AE chat feedback iteratively (`approved`, `needs_revision`, `rejected`).

## ⚙️ Setup Instructions & Execution

1. **Initialize Workspace**:
   ```bash
   python -m venv venv
   source venv/Scripts/activate # OR source venv/bin/activate on Mac/Linux
   pip install -r requirements.txt
   ```
2. **Generate Synthetic Data**:
   ```bash
   python -m data.generate_mock
   ```
3. **Run the API & Webhooks**:
   ```bash
   python -m api.main
   ```
4. **Trigger Orchestration Flow**:
   Post a sample payload to `http://localhost:8000/webhooks/telemetry` or manually run the orchestrator module directly.

## 📈 Quantified Impact Model (ROI)

* **Cost Efficiency**: Automating account research and drafting saves ~30 min per stalled deal. For 1,000 at-risk deals/yr at a $75/hr Account Executive rate, operational savings eclipse $35,000 annually.
* **Revenue Recovery**: Recovering merely 15% more churn on a $500,000 MRR risk pool yields $75,000 incrementally.
* **Total Program ROI**: By investing a conservative baseline implementation cost, organizations can expect over **250%+ pure ROI** in the first fiscal year, pivoting their CRM from a static database into an autonomous revenue engine.
