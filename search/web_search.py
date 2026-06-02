
"""Wikipedia-backed web search shim for compatibility with existing code.

This module provides two functions kept for compatibility with the older
web-search implementation: `should_search_web(query)` and
`search_web(query, top_k=2)`. Internally these functions use the
`search_wikipedia` function implemented in `search/wiki_search.py` and
return a compact `context` string plus minimal `results` and `sources` so
agents can continue to inject the value into system prompts.
"""
from typing import Dict, Any
import logging
import time

from .wiki_search import search_wikipedia


_CACHE: Dict[str, Any] = {}
_CACHE_TTL = 60.0


def should_search_web(query: str) -> bool:
    """Heuristic gating: prefer Wikipedia grounding for factual queries.

    This is intentionally conservative to avoid unnecessary queries for
    greetings or short conversational turns.
    """
    if not query:
        return False
    q = query.lower().strip()
    if len(q.split()) <= 5:
        return False
    triggers = ("product", "processor", "cpu", "gpu", "company", "technology", "software", "ai", "model", "history", "vulnerability", "cve", "spec", "specs", "2026", "latest", "trends")
    return any(t in q for t in triggers)


def _truncate(text: str, max_len: int = 200) -> str:
    if not text:
        return ""
    text = text.strip()
    return text if len(text) <= max_len else text[: max_len - 3] + "..."


def search_web(query: str, top_k: int = 2) -> Dict[str, Any]:
    """Return a compatibility dict using Wikipedia as the source.

    Returns an empty dict when no wiki grounding is appropriate or available.
    """
    if not query:
        return {}

    if not should_search_web(query):
        logging.debug("Wikipedia search skipped by heuristic for query: %s", query)
        return {}

    now = time.time()
    cache_key = f"wiki_shim::{query}::top_k={top_k}"
    cached = _CACHE.get(cache_key)
    if cached and now - cached[1] < _CACHE_TTL:
        return cached[0]

    try:
        wiki_data = search_wikipedia(query)
        context = wiki_data.get("summary", "") if wiki_data.get("success") else ""
        title = wiki_data.get("title") or "Wikipedia"
    except Exception as exc:
        logging.debug("search_wikipedia failed: %s", exc)
        context = ""
        title = "Wikipedia"

    if not context:
        logging.debug("Wikipedia returned no context for query: %s", query)
        _CACHE[cache_key] = ({}, now)
        return {}

    # Build a minimal results structure compatible with previous code
    result = {
        "context": context,
        "results": [{"title": title, "snippet": _truncate(context, 200), "url": "https://en.wikipedia.org"}],
        "sources": ["Wikipedia"],
    }
    _CACHE[cache_key] = (result, now)
    logging.debug("Wikipedia search executed for query: %s", query)
    return result
