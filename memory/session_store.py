"""In-memory session store with timeline-ready message entries and metadata.

Each message stored contains the following fields for analytics and UI:
- role, content, timestamp, llm_used, web_search_used, sentiment, agent_type, confidence, sources
"""

from datetime import datetime, timezone
from threading import RLock
from typing import Any, Dict, List, Optional

# Internal store and lock for thread-safety in the dev server
_sessions: Dict[str, Dict[str, Any]] = {}
_lock = RLock()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_session(user_id: str) -> Dict[str, Any]:
    """Return or create a session dict for *user_id*."""
    with _lock:
        if user_id not in _sessions:
            _sessions[user_id] = {
                "user_id": user_id,
                "agent_type": None,
                "message_history": [],
                "user_profile": {},
                "sentiment_score": None,
                "escalated": False,
                "activity_log": [],
                "analytics": {},
            }
        return _sessions[user_id]


def update_session(user_id: str, **updates) -> None:
    """Update session-level fields for *user_id* (shallow merge)."""
    with _lock:
        session = get_session(user_id)
        session.update(updates)


def add_message(
    user_id: str,
    role: str,
    content: str,
    agent_type: Optional[str] = None,
    llm_used: Optional[str] = None,
    web_search_used: Optional[bool] = False,
    sentiment: Optional[str] = None,
    response_validated: Optional[bool] = None,
    confidence: Optional[int] = None,
    sources: Optional[List[str]] = None,
) -> None:
    """Append a message to the user's timeline with metadata."""
    with _lock:
        session = get_session(user_id)
        item = {
            "role": role,
            "content": content,
            "timestamp": _now_iso(),
            "llm_used": llm_used,
            "web_search_used": web_search_used,
            "sentiment": sentiment,
            "agent_type": agent_type or session.get("agent_type"),
            "response_validated": response_validated,
            "confidence": confidence,
            "sources": sources,
        }
        session["message_history"].append(item)


def add_activity(user_id: str, level: str, category: str, message: str) -> None:
    """Append an activity log entry for the given user session."""
    with _lock:
        session = get_session(user_id)
        entry = {"timestamp": _now_iso(), "level": level, "category": category, "message": message}
        session.setdefault("activity_log", []).append(entry)


def get_activity_log(user_id: str) -> List[Dict[str, Any]]:
    with _lock:
        session = get_session(user_id)
        return list(session.get("activity_log", []))


def get_timeline(user_id: str) -> List[Dict[str, Any]]:
    """Return a copy of the timeline (message_history) for the user."""
    with _lock:
        session = get_session(user_id)
        return list(session.get("message_history", []))


def get_all_sessions() -> List[Dict[str, Any]]:
    with _lock:
        return list(_sessions.values())


def get_analytics() -> Dict[str, Any]:
    """Compute aggregated analytics across all sessions for dashboard consumption."""
    with _lock:
        total_conversations = len(_sessions)
        escalation_count = sum(1 for s in _sessions.values() if s.get("escalated"))

        sentiment_buckets = {"positive": 0, "neutral": 0, "negative": 0, "angry": 0}
        agent_usage = {"sales": 0, "support": 0, "insight": 0}
        active_sessions = 0
        total_response_ms = 0
        response_count = 0

        # Grounding confidence & CSAT calculation variables
        total_confidence = 0
        confidence_count = 0

        # Day-by-day telemetry variables
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        sentiment_by_day = {d: {"positive": 0, "neutral": 0, "negative": 0, "angry": 0} for d in day_names}
        latency_by_day = {d: [] for d in day_names}
        knowledge_by_day = {d: {"direct": 0, "rag": 0} for d in day_names}

        for s in _sessions.values():
            mh = s.get("message_history", [])
            if mh:
                active_sessions += 1

            score = s.get("sentiment_score")
            if score is not None:
                try:
                    sc = float(score)
                    if sc <= 3.5:
                        sentiment_buckets["positive"] += 1
                    elif sc <= 6.5:
                        sentiment_buckets["neutral"] += 1
                    elif sc <= 8.0:
                        sentiment_buckets["negative"] += 1
                    else:
                        sentiment_buckets["angry"] += 1
                except Exception:
                    sentiment_buckets["neutral"] += 1
            
            at = s.get("agent_type") or "sales"
            if at in agent_usage:
                agent_usage[at] += 1

            prev_user_ts = None
            for m in mh:
                try:
                    ts = datetime.fromisoformat(m["timestamp"])
                    day_name = day_names[ts.weekday()]
                except Exception:
                    continue

                if m.get("role") == "user":
                    prev_user_ts = ts
                elif m.get("role") == "assistant":
                    # Determine knowledge RAG vs Direct LLM usage
                    if m.get("web_search_used") or m.get("sources"):
                        knowledge_by_day[day_name]["rag"] += 1
                    else:
                        knowledge_by_day[day_name]["direct"] += 1

                    # Latency check
                    if prev_user_ts is not None:
                        delta = (ts - prev_user_ts).total_seconds() * 1000.0
                        if delta >= 0:
                            total_response_ms += delta
                            response_count += 1
                            latency_by_day[day_name].append(delta)
                        prev_user_ts = None

                    # Accumulate grounding confidence
                    if m.get("confidence") is not None:
                        total_confidence += m.get("confidence")
                        confidence_count += 1

                    # Sentiment by day
                    sent = m.get("sentiment") or "neutral"
                    if sent in sentiment_by_day[day_name]:
                        sentiment_by_day[day_name][sent] += 1

        avg_response_ms = int(total_response_ms / response_count) if response_count else 0
        avg_confidence = int(total_confidence / confidence_count) if confidence_count else 0
        
        # Calculate CSAT out of 5
        total_sentiment_count = sum(sentiment_buckets.values())
        csat = 0.0
        if total_sentiment_count > 0:
            csat = (sentiment_buckets["positive"] * 5.0 +
                    sentiment_buckets["neutral"] * 3.5 +
                    sentiment_buckets["negative"] * 2.0 +
                    sentiment_buckets["angry"] * 1.0) / total_sentiment_count

        # Build serialized trend data for the frontend charts
        sentiment_trend = [{"day": d, **sentiment_by_day[d]} for d in day_names]
        latency_trend = [
            {
                "day": d,
                "latency": int(sum(latency_by_day[d]) / len(latency_by_day[d])) if latency_by_day[d] else 0
            }
            for d in day_names
        ]
        knowledge_trend = [{"name": d, **knowledge_by_day[d]} for d in day_names]

        return {
            "total_conversations": total_conversations,
            "escalation_count": escalation_count,
            "sentiment_distribution": sentiment_buckets,
            "active_sessions": active_sessions,
            "agent_usage": agent_usage,
            "average_response_ms": avg_response_ms,
            "average_confidence": avg_confidence,
            "customer_satisfaction": csat,
            "sentiment_trend": sentiment_trend,
            "latency_trend": latency_trend,
            "knowledge_trend": knowledge_trend,
        }


def clear_session(user_id: str) -> None:
    with _lock:
        _sessions.pop(user_id, None)
