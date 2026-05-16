"""In-memory session store for OmniFlow AI.

Each user session is stored in a dictionary keyed by ``user_id``.
The stored data matches the specification:

- ``user_id``: identifier of the user
- ``agent_type``: one of ``sales``, ``support`` or ``insight``
- ``message_history``: list of ``{"role": "user"|"assistant", "content": str}``
- ``user_profile``: optional dict with user information (can be extended later)
- ``sentiment_score``: numeric score from the Insight agent (0‑10)

The store is deliberately simple – a plain ``dict`` – because the hackathon
prototype runs in a single process.  For production you would replace this
with a persistent database.
"""

from typing import Dict, List, Any

# Global in‑memory store
_sessions: Dict[str, Dict[str, Any]] = {}


def get_session(user_id: str) -> Dict[str, Any]:
    """Return the session dict for *user_id*.

    If the session does not exist it is created with default values.
    """
    if user_id not in _sessions:
        _sessions[user_id] = {
            "user_id": user_id,
            "agent_type": None,
            "message_history": [],
            "user_profile": {},
            "sentiment_score": None,
            "escalated": False,
        }
    return _sessions[user_id]


def update_session(user_id: str, **updates) -> None:
    """Update fields of the session for *user_id*.

    ``updates`` can contain any of the keys defined in the session dict.
    """
    session = get_session(user_id)
    session.update(updates)


def get_all_sessions() -> List[Dict[str, Any]]:
    """Return a list of all session dictionaries."""
    return list(_sessions.values())


def clear_session(user_id: str) -> None:
    """Remove a session from the store."""
    _sessions.pop(user_id, None)
