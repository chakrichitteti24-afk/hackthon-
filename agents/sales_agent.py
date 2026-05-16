"""Sales agent – qualifies leads, recommends products, books demos.
Uses Groq LLM with a system prompt that defines its role.
"""

from groq import Groq
from config import GROQ_API_KEY
from typing import List, Dict

# System prompt for the sales agent
SYSTEM_PROMPT = (
    "You are a helpful sales assistant. Your job is to qualify leads, "
    "recommend relevant products, and schedule demo calls. Keep responses concise "
    "and ask follow‑up questions when needed."
)


def get_reply(message_history: List[Dict[str, str]]) -> str:
    """Generate a reply from the sales agent.

    ``message_history`` should be a list of dicts with ``role`` ("user" or "assistant")
    and ``content`` keys, matching the OpenAI chat format.
    """
    client = Groq(api_key=GROQ_API_KEY)
    # prepend system prompt
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + message_history
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.7,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()
