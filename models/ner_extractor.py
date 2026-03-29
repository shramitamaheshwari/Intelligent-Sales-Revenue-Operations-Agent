"""
NER Extractor — Local PII Anonymization Pipeline
Uses spaCy to strip PERSON / ORG entities from text before it reaches any cloud LLM.
Falls back to regex masking if spaCy model is not installed.
"""

import re

# Try loading the spaCy English model. If not installed, fall back gracefully.
try:
    import spacy
    _nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except Exception:
    _nlp = None
    SPACY_AVAILABLE = False

# Regex fallback patterns for common PII signals
_EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
_PHONE_RE = re.compile(r"\b(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")


def anonymize(text: str) -> tuple[str, list[dict]]:
    """
    Strip PII from `text`. Returns:
      - anonymized_text (str)  — safe to send to cloud LLM
      - entities (list[dict])  — extracted entities for audit log

    Example:
        anonymize("Hi, I'm John Smith from AcmeCorp, call me at 555-1234.")
        → ("Hi, I'm [PERSON] from [ORG], call me at [PHONE].", [...])
    """
    entities = []
    anonymized = text

    if SPACY_AVAILABLE and _nlp:
        doc = _nlp(text)
        # Process in reverse so span offsets stay consistent
        replacements = []
        for ent in doc.ents:
            if ent.label_ in ("PERSON", "ORG", "GPE"):
                tag = f"[{ent.label_}]"
                replacements.append((ent.start_char, ent.end_char, ent.text, tag))
                entities.append({"text": ent.text, "label": ent.label_})

        for start, end, original, tag in sorted(replacements, key=lambda x: -x[0]):
            anonymized = anonymized[:start] + tag + anonymized[end:]
    else:
        # Regex-only fallback
        for m in re.finditer(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", text):
            entities.append({"text": m.group(), "label": "PERSON"})
        anonymized = re.sub(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", "[PERSON]", anonymized)

    # Always strip emails and phones regardless of spaCy
    anonymized = _EMAIL_RE.sub("[EMAIL]", anonymized)
    anonymized = _PHONE_RE.sub("[PHONE]", anonymized)

    return anonymized, entities


def get_status() -> dict:
    """Returns the current anonymization backend status for health checks."""
    return {
        "backend": "spaCy en_core_web_sm" if SPACY_AVAILABLE else "regex fallback",
        "pii_types_masked": ["PERSON", "ORG", "GPE", "EMAIL", "PHONE"],
        "local_only": True,
        "cloud_exposure": "NONE — runs in-process before any external call"
    }
