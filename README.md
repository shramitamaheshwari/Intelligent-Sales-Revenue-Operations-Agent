# Intelligent Sales & Revenue Operations Agent

> **Hackathon Edition — ET AI Hackathon 2026**
> An autonomous multi-agent churn recovery system powered by CrewAI Flows, Groq LLM, and a Human-in-the-Loop governance layer. Built to monitor at-risk B2B accounts, generate psychologically optimized recovery emails, and ensure no email is ever dispatched without explicit Account Executive approval.

---

## Live Demo

| Interface | URL |
|---|---|
| React Dashboard | `http://localhost:5173` |
| Swagger API Docs | `http://localhost:8000/docs` |
| Health Check | `http://localhost:8000/health` |

> See [`EVALUATOR_TESTS.md`](./EVALUATOR_TESTS.md) for copy-paste JSON payloads for every endpoint.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     DATA INGESTION LAYER                        │
│   CRM / Product Analytics  ──────►  FastAPI Webhook Handler     │
│   (feature_usage_dropped, champion_inactive, competitor_mention) │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ML PERCEPTION LAYER                          │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │  Random Forest  │  │  HuggingFace NLI │  │  spaCy NER   │  │
│  │  Churn Scorer   │  │  Zero-Shot Intent│  │  PII Masking │  │
│  │  (scikit-learn) │  │  Classification  │  │  (Local CPU) │  │
│  └─────────────────┘  └──────────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│               ORCHESTRATION LAYER (CrewAI Flows)                │
│                                                                 │
│  @start ──► analyze_account_health()                            │
│       │                                                         │
│  @listen ──► draft_recovery_play() ──► Strategist Agent         │
│       │                               (Chris Voss Prompts)      │
│       │                                                         │
│  @human_feedback ──► PAUSE ──► AE Review (Slack/Email)          │
│       │                                                         │
│       ├── 'approved'      ──► execute_campaign()                │
│       ├── 'rejected'      ──► abort_campaign() + RLHF log       │
│       └── 'needs_revision'──► review_loop() ──► (recurse)       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REACT DASHBOARD (Vite)                       │
│  Account Monitor │ Agent Pipeline Visualizer │ ROI Model        │
│  HITL Draft Panel │ System Logs │ Light Mode UI                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
intelligent-revops-agent/
│
├── agents/
│   ├── analyst_agent.py       # Intelligence Analyst: RandomForest + NLP churn scoring
│   ├── copywriter_agent.py    # Strategist: Chris Voss psychology prompts + email drafting
│   └── orchestrator.py        # CrewAI Flow: @start, @listen, @human_feedback, or_() loop
│
├── models/
│   ├── ner_extractor.py       # Local spaCy NER — strips PII before any cloud API call
│   └── sentiment_nli.py       # HuggingFace zero-shot NLI — detects competitor/tone intent
│
├── api/
│   ├── main.py                # FastAPI app, CORS, router registration
│   ├── frontend_handler.py    # /api/accounts (CSV+ML) and /api/generate (CrewAI) endpoints
│   └── webhook_handler.py     # Async webhook receivers: NER → NLI → pipeline trigger
│
├── data/
│   ├── generate_mock.py       # Generates 2,000 synthetic CRM records (Gaussian/Poisson)
│   └── mock_datasets/
│       └── telemetry.csv      # Generated CRM telemetry (2,000 rows)
│
├── frontend/                  # Vite + React SPA
│   ├── src/
│   │   ├── App.jsx            # Main app: state machine, API hooks, all views
│   │   └── index.css          # Premium light-mode design system
│   ├── vite.config.js         # Proxy /api → localhost:8000
│   └── package.json
│
├── EVALUATOR_TESTS.md         # Copy-paste JSON payloads for Swagger UI (START HERE)
├── requirements.txt           # Pinned Python dependency lockfile
├── .env.example               # Environment variable template
└── README.md                  # This file
```

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- A [Groq API Key](https://console.groq.com/) (free tier)

---

### Step 1 — Clone & Configure Environment

```bash
git clone https://github.com/shramitamaheshwari/Intelligent-Sales-Revenue-Operations-Agent.git
cd Intelligent-Sales-Revenue-Operations-Agent/intelligent-revops-agent
```

Create your `.env` file:
```bash
cp .env.example .env
# Edit .env and paste your GROQ_API_KEY
```

```env
GROQ_API_KEY=your_groq_api_key_here
```

---

### Step 2 — Python Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### Step 3 — Generate Synthetic Dataset

```bash
# From the /data directory, using the project venv
cd data
..\venv\Scripts\python.exe generate_mock.py
# Output: "Generated 2000 records. Saved to mock_datasets/telemetry.csv"
cd ..
```

---

### Step 4 — Start the Backend API

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

- Swagger UI: **http://localhost:8000/docs**
- Health check: **http://localhost:8000/health**

You should see `Model Trained.` in the terminal — confirming the RandomForest classifier loaded from `telemetry.csv`.

---

### Step 5 — Start the React Frontend

```bash
cd frontend
npm install
npm run dev
```

- React Dashboard: **http://localhost:5173**

---

## Agent Capabilities

### RevOps Intelligence Analyst Agent
- Ingests structured CRM telemetry (CMRR, support ticket velocity, days since last login)
- Trains and runs a `RandomForestClassifier` to output calibrated churn probability scores
- Invokes `spaCy` NER locally to strip PII before passing text to any cloud API
- Calls HuggingFace zero-shot NLI to detect competitor mentions and passive-aggressive tone in email threads

### B2B Sales Strategist Agent (Copywriter)
- Receives structured risk payload from the Analyst Agent
- Selects from three psychological recovery frameworks based on dominant signal:
  - **Usage Drop** — Empathy Labeling (reverse psychology, attribute drop to UI friction)
  - **Champion Leaves** — Continuity Bridge (zero-pressure briefing to preserve workflow)
  - **Competitor Threat** — Tactical Mirror (75-word cap, confidence through brevity)
- Strictly prohibited from feature-pitching; enforces Chris Voss Labeling methodology
- Never dispatches directly — all output is routed to the HITL gate

### CrewAI Flow Orchestrator
- `@start` — triggers `analyze_account_health()` on webhook receipt
- `@listen` — delegates to B2B Strategist Agent for `draft_recovery_play()`
- `@human_feedback` — pauses execution asynchronously, dispatches draft to AE for review
- `or_()` self-healing loop — if AE returns `needs_revision`, re-delegates with feedback appended until resolved
- Terminal states: `execute_campaign()` (approved) or `abort_campaign()` + RLHF logging (rejected)

---

## Security & Data Privacy

| Component | Execution | Data Classification |
|---|---|---|
| spaCy NER Extraction | Local CPU | Processes raw PII — never transmitted |
| RandomForest Churn Model | Local (scikit-learn, in-memory) | Structured features only — no PII |
| HuggingFace Zero-Shot NLI | HF Inference API (cloud) | Receives anonymized text only |
| Groq LLM (Strategist) | Groq API (cloud) | Receives anonymized context payload only |
| CRM API Dispatch | Cloud CRM (mocked) | Receives final approved email only |

> **Architectural guarantee:** The system is structurally incapable of dispatching client-facing communications without passing through the `@human_feedback` gate. This is enforced at the framework level by CrewAI, not by policy.

---

## Quantified Business Impact

| Value Vector | Formula | Projected Value |
|---|---|---|
| Cost Efficiency | 1,000 deals × 0.5 hr saved × $75/hr AE rate − $2,500 API costs | **$35,000 / year** |
| Revenue Recovery | $500K at-risk MRR × 15% absolute lift in recovery rate (30% → 45%) | **$75,000 / year** |
| Implementation Cost | Developer time + licensing + server provisioning | **$30,000** |
| **Total Year-1 ROI** | ($35K + $75K − $30K) ÷ $30K × 100 | **266%** |

---

## Hackathon Evaluation Alignment

| Rubric | Implementation |
|---|---|
| **Deal Intelligence** | Webhook triggers, NLI competitor detection, SHAP-explained churn scores |
| **Revenue Retention** | RandomForest ML pipeline, Chris Voss template selection, HITL gate |
| **Competitive Intelligence** | Zero-shot NLI on email text, 75-word competitor response cap |
| **Pipeline Impact** | Self-healing `or_()` revision loop, RLHF rejection logging |
| **Security / Governance** | Local spaCy NER, PII never leaves network, human approval mandatory |
| **Full-Stack Demo** | React SPA + FastAPI + CrewAI + Groq — all wired end-to-end |

---

## Testing

See **[EVALUATOR_TESTS.md](./EVALUATOR_TESTS.md)** for complete copy-paste JSON payloads for every Swagger UI endpoint, including expected responses and a recommended demo sequence.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent Orchestration | CrewAI Flows |
| LLM Provider | Groq (`llama-3.1-8b-instant`) |
| ML Pipeline | scikit-learn RandomForestClassifier |
| NLP — PII | spaCy `en_core_web_sm` |
| NLP — Intent | HuggingFace `facebook/bart-large-mnli` |
| Backend API | FastAPI + Uvicorn |
| Frontend | React + Vite |
| Data Pipeline | Pandas + NumPy (Gaussian/Poisson distributions) |
| Environment | Python 3.10+, Node.js 18+ |
