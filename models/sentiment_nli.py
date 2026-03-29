"""
Sentiment / Intent Classifier — HuggingFace Zero-Shot NLI
Classifies email text against candidate intent labels without fine-tuning.
Falls back to fast keyword heuristics if transformers library is unavailable.
"""

from __future__ import annotations

# Candidate labels matching the spec's signal taxonomy
CANDIDATE_LABELS = [
    "competitor comparison",
    "cancellation threat",
    "passive-aggressive tone",
    "champion departure",
    "payment issue",
    "general inquiry",
]

# Try loading HuggingFace pipeline
try:
    from transformers import pipeline as hf_pipeline
    _classifier = hf_pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
        device=-1  # CPU only — keep local
    )
    HF_AVAILABLE = True
except Exception:
    _classifier = None
    HF_AVAILABLE = False

# Keyword fallback map (for demo when transformers not installed)
_KEYWORD_MAP = {
    "competitor comparison": ["competitor", "alternative", "switching", "vs ", "better than"],
    "cancellation threat":   ["cancel", "terminate", "not renewing", "walk away", "end contract"],
    "passive-aggressive tone": ["fine", "whatever", "i guess", "sure", "not sure why"],
    "champion departure":    ["left the company", "new role", "leaving", "transitioned", "former"],
    "payment issue":         ["invoice", "overdue", "payment", "billing", "charge"],
}


def classify_intent(text: str, threshold: float = 0.3) -> dict:
    """
    Classify the dominant intent signal in `text`.

    Returns:
        {
          "dominant_signal": str,
          "scores": dict[str, float],
          "backend": "huggingface" | "keyword_heuristic"
        }
    """
    if HF_AVAILABLE and _classifier:
        result = _classifier(text, CANDIDATE_LABELS, multi_label=False)
        scores = dict(zip(result["labels"], result["scores"]))
        dominant = result["labels"][0] if result["scores"][0] >= threshold else "general inquiry"
        return {"dominant_signal": dominant, "scores": scores, "backend": "huggingface"}

    # Keyword heuristic fallback
    text_lower = text.lower()
    hits: dict[str, int] = {}
    for label, keywords in _KEYWORD_MAP.items():
        hits[label] = sum(1 for kw in keywords if kw in text_lower)

    dominant = max(hits, key=hits.get) if any(hits.values()) else "general inquiry"
    scores = {k: round(v / max(sum(hits.values()), 1), 2) for k, v in hits.items()}
    return {"dominant_signal": dominant, "scores": scores, "backend": "keyword_heuristic"}


def map_to_signal(intent: str) -> str:
    """
    Normalise NLI output → internal signal taxonomy used by the Orchestrator.
    """
    mapping = {
        "competitor comparison":   "competitor",
        "cancellation threat":     "usage_drop",
        "passive-aggressive tone": "usage_drop",
        "champion departure":      "champion",
        "payment issue":           "payment",
        "general inquiry":         "usage_drop",
    }
    return mapping.get(intent, "usage_drop")


def get_status() -> dict:
    return {
        "backend": "HuggingFace bart-large-mnli" if HF_AVAILABLE else "keyword heuristic",
        "model_size": "1.6 GB" if HF_AVAILABLE else "N/A",
        "local_only": True,
        "latency_ms": "~800ms" if HF_AVAILABLE else "<5ms"
    }
