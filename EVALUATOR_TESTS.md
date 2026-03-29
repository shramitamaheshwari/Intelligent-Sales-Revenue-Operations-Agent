# Evaluator API Test Guide — Intelligent RevOps Agent

> **For Hackathon Evaluators:** This document contains copy-paste ready JSON payloads for every endpoint in the system.
> Start the backend (`uvicorn api.main:app --reload`) and navigate to **http://localhost:8000/docs** to use the interactive Swagger UI.

---

## Quick Start for Evaluators

```bash
# 1. Activate the venv
.\venv\Scripts\activate

# 2. Start the backend API
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Open Swagger UI
start http://localhost:8000/docs

# 4. (Optional) Run the React frontend
cd frontend && npm run dev
# Then open http://localhost:5173
```

---

## Endpoint Test Payloads

---

### WEBHOOKS — Inbound Signal Receivers

---

#### `POST /webhooks/webhook/event`
**Purpose:** Generic event receiver — triggers full NER anonymization → NLI classification → CrewAI pipeline as an async background task.

**Paste into Request Body:**
```json
{
  "event_type": "feature_usage_dropped",
  "account_id": 1,
  "account_name": "AcmeCorp",
  "cmrr": 4200,
  "days_since_login": 18,
  "signal_value": 0.87,
  "raw_email_text": "Honestly we've been evaluating Salesforce and a few other alternatives. I'm not sure we're getting the value we expected from the Core Analytics module. John Smith from our team flagged this last week."
}
```

**Expected Response:**
```json
{
  "status": "accepted",
  "message": "Event 'feature_usage_dropped' for account 'AcmeCorp' queued for processing.",
  "pipeline": "NER → NLI → Orchestrator → HITL"
}
```

**What to verify:** The `raw_email_text` field runs through the local NER pipeline (PII masking) and the NLI zero-shot classifier. After firing this, call `GET /webhooks/webhook/events` to see the processing log — you should see `entities_masked` > 0 for "John Smith".

---

#### `POST /webhooks/webhook/champion_inactive`
**Purpose:** Champion departure shortcut — triggers Continuity Bridge recovery framework.

> **Note:** Uses query parameters, not a request body. Fill in the fields under "Parameters" in Swagger UI.

```
account_id: 2
account_name: Nexus Analytics
```

**Expected Response:**
```json
{
  "status": "accepted",
  "signal": "champion",
  "framework": "Continuity Bridge"
}
```

---

#### `POST /webhooks/webhook/usage_dropped`
**Purpose:** Usage drop shortcut — triggers Empathy Labeling recovery framework.

```
account_id: 1
account_name: AcmeCorp
```

**Expected Response:**
```json
{
  "status": "accepted",
  "signal": "usage_drop",
  "framework": "Empathy Labeling"
}
```

---

#### `GET /webhooks/webhook/events`
**Purpose:** Returns the live event processing log. No body needed — click Execute.

**Expected Response:**
```json
{
  "events": [
    {
      "event_type": "feature_usage_dropped",
      "account": "AcmeCorp",
      "status": "completed",
      "signal": "usage_drop",
      "entities_masked": 2,
      "ner_backend": "regex fallback",
      "detected_signal": "usage_drop",
      "nli_backend": "keyword_heuristic"
    }
  ]
}
```

---

### FRONTEND — React Dashboard API

---

#### `GET /api/accounts`
**Purpose:** Loads all at-risk accounts from `telemetry.csv`, runs RandomForest churn scoring on every row, returns sorted by risk descending.

No body needed — click Execute.

**Expected Response (truncated):**
```json
{
  "status": "success",
  "accounts": [
    {
      "id": 1,
      "name": "Quantum Bridge",
      "tier": "Mid-Market",
      "cmrr": 2259.58,
      "risk": 1.0,
      "signal": "champion",
      "tone": "passive-aggressive",
      "days": 12,
      "tickets": 3.4,
      "adopt": 57,
      "cmrr_trend": -5,
      "competitor": true,
      "champion": true
    }
  ]
}
```

**What to verify:** Response contains 50 accounts. Each `risk` value is dynamically computed by the live `RandomForestClassifier` trained on `telemetry.csv` — not hardcoded.

---

#### `POST /api/generate` — Scenario 1: Usage Drop

```json
{
  "account_id": 1,
  "signal": "usage_drop",
  "name": "AcmeCorp"
}
```

**Expected Response:**
```json
{
  "status": "success",
  "draft": {
    "subject": "Did we break something in the UI?",
    "body": "Hi AcmeCorp,\n\nThis might be a complete waste of your time, but my tracking caught a severe 60% drop in your team's usage...",
    "framework": "Usage Drop",
    "color": "orange"
  }
}
```

---

#### `POST /api/generate` — Scenario 2: Champion Leaves

```json
{
  "account_id": 2,
  "signal": "champion",
  "name": "Nexus Analytics"
}
```

**Expected Response:**
```json
{
  "status": "success",
  "draft": {
    "subject": "Overwhelmed with the transition?",
    "body": "Hi Nexus,\n\nIt seems like you are inheriting a massive amount of legacy systems right now...",
    "framework": "Champion Leaves",
    "color": "blue"
  }
}
```

---

#### `POST /api/generate` — Scenario 3: Competitor Threat

```json
{
  "account_id": 3,
  "signal": "competitor",
  "name": "Stratos Inc."
}
```

**Expected Response:**
```json
{
  "status": "success",
  "draft": {
    "subject": "Fair enough — they are a strong choice.",
    "body": "Hi Stratos,\n\nHonestly? They've built a remarkably strong product over the last year...",
    "framework": "Competitor",
    "color": "red"
  }
}
```

---

#### `POST /api/generate` — Scenario 4: DSO / Payment

```json
{
  "account_id": 4,
  "signal": "payment",
  "name": "PineCrest Labs"
}
```

> **Live LLM indicator:** If the `GROQ_API_KEY` is active, the `framework` field will return `"Groq LLM Native"` — confirming a real CrewAI agent kickoff occurred, not the fallback template.

---

### DEFAULT

---

#### `GET /`
Redirects to Swagger UI (`/docs`). Expected: `301 Redirect`.

#### `GET /health`
No body needed.

**Expected Response:**
```json
{
  "status": "operational",
  "agent_version": "1.0.0"
}
```

---

## Recommended Evaluator Demo Sequence

Run these in order for the most impactful live demo:

1. `GET /health` — confirm system is operational
2. `GET /api/accounts` — show 50 live ML-scored accounts
3. `POST /api/generate` (competitor signal) — trigger CrewAI agent
4. `POST /webhooks/webhook/event` (with raw_email_text) — demonstrate NER pipeline
5. `GET /webhooks/webhook/events` — show the processing log with PII masking applied
