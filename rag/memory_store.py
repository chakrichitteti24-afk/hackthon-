import os
import sys
from typing import Dict, Any

# Make sure the backend root is on sys.path so we can import the existing session store
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    from memory import session_store
except Exception:
    # best-effort import fallback
    import importlib

    session_store = importlib.import_module("memory.session_store")


def get_customer_memory(user_id: str) -> Dict[str, Any]:
    """Return a compact dict with customer's remembered preferences.

    The function reads session-level `user_profile` and falls back to
    lightweight heuristics over message history.
    """
    s = session_store.get_session(user_id)
    profile = s.get("user_profile", {}) or {}

    memory = {
        "budget": profile.get("budget"),
        "interest": profile.get("interest"),
        "brand": profile.get("brand"),
        "sentiment": profile.get("sentiment") or s.get("sentiment_score"),
    }

    # If any field missing, attempt simple heuristics over the last few messages
    if not memory.get("interest"):
        mh = s.get("message_history", [])
        for m in reversed(mh[-6:]):
            if m.get("role") == "user":
                txt = (m.get("content") or "").lower()
                if "gaming" in txt or "laptop" in txt:
                    memory["interest"] = memory.get("interest") or "gaming laptops"
                    break

    return memory


def upsert_customer_memory(user_id: str, mem: Dict[str, Any]) -> None:
    s = session_store.get_session(user_id)
    profile = s.get("user_profile", {}) or {}
    profile.update(mem)
    session_store.update_session(user_id, user_profile=profile)
"""Customer memory helpers to extract a compact, human-readable memory summary.

This module wraps the existing `memory.session_store` for a concise
memory context suitable for prompt injection.
"""
from typing import List
from memory.session_store import get_session


def get_compact_memory(user_id: str, max_messages: int = 6) -> str:
    """Return a short text summarizing the customer's memory/profile and
    recent messages.

    The returned string is intentionally terse to keep prompts small.
    """
    sess = get_session(user_id)
    profile = sess.get("user_profile", {}) or {}
    parts: List[str] = []

    # Key profile fields
    for k in ("budget", "interest", "brand", "sentiment"):
        if k in profile and profile.get(k) not in (None, ""):
            parts.append(f"{k.capitalize()}: {profile.get(k)}")

    # Recent user messages for short-term memory
    timeline = sess.get("message_history", []) or []
    user_messages = [m.get("content", "") for m in timeline if m.get("role") == "user"]
    if user_messages:
        recent = user_messages[-max_messages:]
        parts.append("Recent user messages:")
        for u in recent:
            # keep each message on one line
            line = u.replace("\n", " ")
            parts.append(f"- {line}")

    if not parts:
        return ""
    return "\n".join(parts)


__all__ = ["get_compact_memory"]
