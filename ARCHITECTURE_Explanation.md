# Architecture Walkthrough Script
## Intelligent Sales & Revenue Operations Agent
### Estimated Duration: ~4–5 minutes (spoken at comfortable pace)

---

> **Delivery Notes:**
> - Speak at a measured pace — this is dense material, evaluators need time to absorb it.
> - Pause at each `[PAUSE]` marker for 1–2 seconds.
> - Phrases in **[SHOW: ...]** indicate what to have on screen or point to at that moment.
> - Tone should be confident and precise — like a senior engineer presenting a design review, not a sales pitch.

---

## Opening — The Problem Statement

**[SHOW: Account Monitor dashboard — list of at-risk accounts with risk bars]**

> "Every B2B SaaS company is sitting on a ticking clock.
>
> Right now, your Account Executives are manually combing through CRM dashboards, catching a usage drop three weeks after it happened, drafting a generic outreach email, and hitting send — hoping for the best.
>
> That process is slow, inconsistent, and at scale, it simply doesn't work.
>
> What we built is a system that detects churn before the AE even opens their laptop. It analyzes the signal, selects the right psychological recovery strategy, drafts the email — and then it stops.
>
> Because the one thing an autonomous system should never do is put words in a human's mouth and send them to a client without review. [PAUSE]
>
> That architectural constraint — the Human-in-the-Loop gate — is not a limitation. It is the product."

---

## Layer 1 — Data Ingestion

**[SHOW: System Logs panel or the webhook endpoint in Swagger UI]**

> "The system starts at the data layer.
>
> Rather than polling the CRM every few minutes — which is expensive and slow — we use an event-driven architecture. FastAPI registers asynchronous webhook receivers that subscribe to specific product analytics events.
>
> When Segment or Mixpanel fires a `feature_usage_dropped` event, when your CRM detects that the champion contact has gone inactive, when an email thread contains a competitor mention — those signals hit our `/webhooks/event` endpoint instantly. [PAUSE]
>
> The payload arrives. The NLP pipeline activates. And the clock starts."

---

## Layer 2 — The ML Perception Layer

**[SHOW: Agent Pipeline view — Analyst Agent node highlighted]**

> "The first agent to wake up is the RevOps Intelligence Analyst.
>
> It receives the account telemetry — CMRR trend, support ticket velocity, days since last login — and passes it through a Random Forest classifier trained on two thousand synthetic CRM records.
>
> The model returns a calibrated churn probability score, along with Shapley Additive Explanations — SHAP values — that tell us *which specific signals* are driving the risk for that exact account. Not a generic score. A ranked, explainable breakdown. [PAUSE]
>
> In parallel, if there's an email thread in the payload, two NLP pipelines fire simultaneously.
>
> First — and critically — the spaCy NER model runs locally on CPU. It extracts named entities: person names, company names, locations. And it strips them. Zero PII leaves the local network. The payload that goes upstream is fully anonymized. [PAUSE]
>
> Second, a HuggingFace zero-shot NLI classifier evaluates the email text against candidate intent labels — 'competitor comparison', 'cancellation threat', 'passive-aggressive tone' — without requiring any fine-tuning. It outputs the dominant intent signal, which the orchestrator uses to select the recovery strategy.
>
> So by the time the Analyst Agent is done, what comes out is a clean, structured JSON context payload. Risk score. Dominant signal. Intent labels. Anonymized entities. Ready for the next stage."

---

## Layer 3 — The Orchestration Layer

**[SHOW: Agent Pipeline — full flow visible, HITL node highlighted amber/yellow]**

> "This is where the CrewAI Flows architecture takes over. And this is the part of the system I want to spend the most time on.
>
> The Orchestrator is a deterministic state machine. Not a chain of prompts. A state machine with explicit `@start`, `@listen`, and `@human_feedback` decorators that enforce a strict execution graph. [PAUSE]
>
> It starts with `analyze_account_health()`, which triggers the Analyst Agent we just described.
>
> The result flows into `draft_recovery_play()`, which delegates the task to the B2B Sales Strategist Agent.
>
> Now, the Strategist Agent is given one job: draft a recovery email. But it's tightly constrained.
>
> It cannot feature-pitch. It cannot use generic language. Based on the dominant signal from the Analyst, it selects one of three psychological frameworks — and these are not made up. These are Chris Voss negotiation techniques from 'Never Split the Difference':
>
> — For a usage drop, it applies **Empathy Labeling** — attributing the drop to a potential UI problem we caused, not the customer's disengagement. Reverse psychology that lowers the defensive posture.
>
> — For a departing champion, it uses the **Continuity Bridge** — zero-pressure, no pitch, just: 'I'd hate for the workflow you rely on to break during a leadership transition.'
>
> — For a competitor threat, it applies **Tactical Mirroring** with a hard 75-word cap. Confidence encoded through brevity.
>
> The draft goes into the flow's internal state. And then — [PAUSE] — execution stops."

---

## Layer 4 — The Human-in-the-Loop Gate

**[SHOW: HITL Draft Panel — email draft visible with Approve / Reject buttons]**

> "This is the architectural centerpiece.
>
> The `@human_feedback` decorator pauses the entire flow asynchronously. It dispatches the draft — along with the account context, the risk score, and an approval interface — to the Account Executive.
>
> The AE reviews it. They can approve. They can reject. Or they can respond in natural language — 'Make this shorter' or 'Reference the Q3 data they mentioned.'
>
> And this is a clever piece of engineering: a lightweight router model parses that free-form feedback and collapses it into one of three discrete categorical outcomes: `approved`, `rejected`, or `needs_revision`. [PAUSE]
>
> Why does that matter? Because ambiguous human input cannot be allowed to cause unpredictable agent behavior downstream. The router forces determinism at the boundary between human and machine.
>
> If `needs_revision` is returned, the `or_()` operator routes the feedback back to the Strategist Agent, which re-drafts with the revision notes appended. This loop continues until the AE emits an unambiguous signal.
>
> If `approved` — the system calls `execute_campaign()`, which stages the email in the CRM and schedules the send.
>
> If `rejected` — the draft is discarded, and the interaction is logged to the RLHF pipeline to improve future performance.
>
> And I want to be very clear about one thing: every single path through this state graph that leads to `execute_campaign()` passes through an explicit human authorization checkpoint. This is not a policy rule that can be bypassed by prompt injection or unexpected agent chaining. It is enforced at the framework level."

---

## Layer 5 — The React Dashboard

**[SHOW: Account Monitor → click Draft → HITL panel → click Approve → switch to Pipeline view]**

> "On top of all of this sits a React frontend built with Vite — a production-grade SPA that replaces the vanilla HTML prototype.
>
> The Account Monitor pulls live data from the FastAPI backend. The Random Forest is scoring every account in real time from the telemetry CSV. The risk bars you see are not hardcoded. They're ML outputs. [PAUSE]
>
> When you click Draft on an account, the React frontend fires a `POST /api/generate` request to the backend, which instantiates the CrewAI crew, kicks off the agent, and streams the result back.
>
> If the Groq API is unavailable — rate limit, network issue, anything — the system falls back to a signal-accurate local template. The demo never crashes.
>
> And when you flip to the Agent Pipeline tab, what you see is live. That flow visualizer is wired to the same state that drives the HITL panel. When you hit Approve, the HITL node turns green. The Execute node activates. The pipeline resolves."

---

## Closing — The Architectural Guarantee

**[SHOW: README or ROI Model page]**

> "Let me close with the business case, because I think it crystallizes why the architecture is designed the way it is.
>
> For a company monitoring one thousand at-risk accounts per month — which is a typical mid-market AE portfolio at scale — the system reclaims twenty-four thousand AE hours per year. It lifts churn recovery rates by fifteen percentage points, from thirty percent to forty-five percent, recovering an incremental seventy-five thousand dollars of MRR every single month.
>
> Against a thirty-thousand-dollar implementation cost, that's a two hundred sixty-six percent ROI — and a payback period of under two weeks.
>
> But the number that matters most to me isn't the ROI percentage. [PAUSE]
>
> It's this: the system is architecturally incapable of sending an unsanctioned email to a client.
>
> In a world where autonomous AI is rapidly moving from research to production, that design constraint is the difference between a demo and a product you can actually deploy.
>
> Thank you."

---

## Appendix — Rapid-Fire Q&A Prep

Use these if judges follow up with hard questions:

**Q: "What happens if the Groq API hits its rate limit mid-demo?"**
> "The backend has a try/except wrapper around every CrewAI kickoff. If Groq is unavailable, the system immediately falls back to a signal-accurate local template — so the UI never shows an error. The fallback also maps correctly to the signal type, so Nexus Analytics gets the Champion Leaves template, not a generic Usage Drop."

**Q: "Is the RandomForest actually trained or is it mocked?"**
> "It's actually trained. On startup, the FastAPI server calls `ChurnScoringPipeline().train()` against a 2,000-row CSV generated by our Gaussian/Poisson distribution script. You can see 'Model Trained.' in the terminal when the server boots. Every risk score returned by the API is a live `predict_proba()` call against that fitted model."

**Q: "Why spaCy instead of a cloud NER API?"**
> "Because the moment customer names leave your network — even to an NER API — you have a PII exposure event. spaCy's `en_core_web_sm` runs in-process, on CPU, with no network call whatsoever. The anonymized text is what gets sent to Groq. The raw text never does."

**Q: "How would this work in production — not a hackathon?"**
> "The architecture is already production-structured. Replace the CSV with a Salesforce or HubSpot webhook subscription. Replace the Slack notification stub with a real Slack App OAuth token. The CrewAI flow, FastAPI endpoints, and HITL gate are all production-viable as-is. The only gap is CRM API credentials and a hosted cloud deployment — both of which are configuration, not engineering."
