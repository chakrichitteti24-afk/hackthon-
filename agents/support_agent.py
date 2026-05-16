"""Support agent – resolves issues, remembers user history, creates tickets.
Uses Groq LLM with a system prompt that defines its role.
"""

from groq import Groq
from config import GROQ_API_KEY
from typing import List, Dict

SYSTEM_PROMPT = (
    "You are a helpful support assistant. Resolve the user's issue, "
    "refer to previous conversation history when relevant, and if the problem cannot be solved, "
    "create a support ticket. Keep responses concise and friendly."
)


def get_reply(message_history: List[Dict[str, str]]) -> str:
    """Generate a reply from the support agent.

    ``message_history`` follows the OpenAI chat format.
    """
    client = Groq(api_key=GROQ_API_KEY)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + message_history
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.7,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()
