"""Smart message router that decides whether to use Gemini or Groq.

This router returns a structured decision dict with:
- model: 'gemini' | 'groq'
- reason: short human-readable reason
- confidence: float in 0..1

Rules implemented:
- Use Gemini for recommendations, product intelligence, comparisons, analysis, market insights, research, and detailed responses.
- Use Groq for greetings, confirmations, short responses, and quick interactions.
"""
from typing import Iterable, Dict


FORCE_GEMINI = {
    "recommend",
    "product",
    "intelligence",
    "compare",
    "comparison",
    "analysis",
    "analyze",
    "insight",
    "research",
    "detail",
    "explain",
    "business",
    "future",
    "trends",
    "specs",
}

FORCE_GROQ = {
    "hi",
    "hello",
    "hey",
    "thanks",
    "thank you",
    "yes",
    "no",
    "greetings",
    "confirmation",
}


def _word_count(text: str) -> int:
    return len(text.split()) if text else 0


def _contains(text: str, keywords: Iterable[str]) -> bool:
    if not text:
        return False
    lower = text.lower()
    return any(k in lower for k in keywords)


def route_message(message: str) -> Dict[str, object]:
    """Return a dict: {'model': str, 'reason': str, 'confidence': float}.

    Designed to route between Gemini (primary) and Groq (secondary).
    """
    text = (message or "").strip()
    wc = _word_count(text)

    if not text:
        return {"model": "groq", "reason": "empty query", "confidence": 0.5}

    # Forced Gemini by explicit domain keywords
    if _contains(text, FORCE_GEMINI):
        return {"model": "gemini", "reason": "detailed query", "confidence": 0.95}

    # Forced Groq for short greetings and simple yes/no replies
    if wc <= 5 and (_contains(text, FORCE_GROQ) or text.lower() in FORCE_GROQ):
        return {"model": "groq", "reason": "simple response", "confidence": 0.95}

    # Word-count threshold: short queries -> GROQ, otherwise GEMINI
    if wc <= 5:
        return {"model": "groq", "reason": "short query", "confidence": 0.9}

    return {"model": "gemini", "reason": "detailed query", "confidence": 0.91}


def should_use_wiki(query: str) -> bool:
    """Wikipedia grounding is active for every non-empty query."""
    if not query or not query.strip():
        return False
    return True
