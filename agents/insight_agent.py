"""Insight agent – analyses sentiment of a user message.
It returns a JSON‑compatible dict with ``sentiment`` (one of
``positive``, ``negative``, ``neutral``, ``angry``), a numeric ``score``
(0‑10) and an ``escalate`` flag that is ``True`` when the sentiment is
angry or the score exceeds the escalation threshold.
"""

from groq import Groq
from config import GROQ_API_KEY
from typing import List, Dict, Any

# System prompt that instructs the model to perform sentiment analysis
SYSTEM_PROMPT = (
    "You are an AI sentiment analyst. Analyse the last user message and "
    "return a JSON object with the following keys:"
    "\n- sentiment: one of 'positive', 'negative', 'neutral', 'angry'"
    "\n- score: an integer from 0 to 10 indicating intensity (higher = more negative)"
    "\n- escalate: true if the sentiment is 'angry' or score > 7, otherwise false."
    "\nProvide ONLY the JSON object, no extra text."
)


def get_sentiment(message_history: List[Dict[str, str]]) -> Dict[str, Any]:
    """Call the Groq model and parse the JSON sentiment result.

    ``message_history`` should contain the conversation so far. The model
    only needs the most recent user message, but we pass the full history for
    context.
    """
    client = Groq(api_key=GROQ_API_KEY)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + message_history
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.0,
        max_tokens=256,
    )
    # The model is instructed to output pure JSON – we attempt to parse it.
    import json
    try:
        result = json.loads(response.choices[0].message.content.strip())
    except json.JSONDecodeError:
        # Fallback: return a neutral result if parsing fails
        result = {"sentiment": "neutral", "score": 5, "escalate": False}
    return result
