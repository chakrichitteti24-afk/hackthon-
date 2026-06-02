"""Wikipedia-first factual grounding for OmniFlow AI."""

import logging
import requests
import wikipedia
import wikipediaapi

# Part 2: Setup Wikipedia API
wiki = wikipediaapi.Wikipedia(
    language="en",
    user_agent="OmniFlowAI/1.0"
)

# Part 1: Smart lightweight query detection
SIMPLE_MESSAGES = [
    "hi",
    "hello",
    "hey",
    "thanks",
    "thank you",
    "how are you",
    "good morning",
    "good night",
    "ok",
    "okay",
    "yes",
    "no"
]

FACTUAL_KEYWORDS = [
    "phone",
    "mobile",
    "processor",
    "technology",
    "company",
    "ai",
    "compare",
    "recommend",
    "history",
    "cpu",
    "gpu",
    "android",
    "iphone",
    "samsung",
    "apple",
    "features",
    "specifications",
    "business",
    "strategy"
]


def clean_query(query: str) -> str:
    """Perform lightweight query normalization and typo correction."""
    cleaned = query.lower().strip()
    cleaned = cleaned.replace("i phone", "iphone")
    cleaned = cleaned.replace("samsng", "samsung")
    cleaned = cleaned.replace("moble", "mobile")
    return cleaned


def should_use_wikipedia(message: str) -> bool:
    """Determine if a message requires factual grounding via Wikipedia."""
    message_lower = message.lower().strip()

    if message_lower in SIMPLE_MESSAGES:
        return False

    for keyword in FACTUAL_KEYWORDS:
        if keyword in message_lower:
            return True

    return False


def _search_title(query: str) -> str:
    """Resolve query to a real page title using Wikipedia API search endpoint."""
    try:
        response = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": 1,
                "format": "json",
            },
            headers={"User-Agent": "OmniFlowAI/1.0"},
            timeout=4.0,
        )
        response.raise_for_status()
        results = response.json().get("query", {}).get("search", [])
        if results:
            return str(results[0].get("title") or "").strip()
    except Exception as e:
        logging.debug("Wikipedia search title resolution failed: %s", e)
    return query


def search_wikipedia(query: str) -> dict:
    """Search Wikipedia using fuzzy matching and typo corrections, returning structured details."""
    cleaned_query = clean_query(query)
    
    # 1. Try fuzzy matching via wikipedia.search
    try:
        results = wikipedia.search(cleaned_query)
        if results:
            best_match = results[0]
            page = wiki.page(best_match)
            if page.exists():
                return {
                    "title": page.title,
                    "summary": page.summary[:1200],
                    "source": "Wikipedia",
                    "success": True
                }
    except Exception as exc:
        logging.debug("Fuzzy Wikipedia search failed: %s", exc)

    # 2. Fallback to standard API search resolution
    try:
        resolved_title = _search_title(cleaned_query) or cleaned_query
        page = wiki.page(resolved_title)
        if page.exists():
            return {
                "title": page.title,
                "summary": page.summary[:1200],
                "source": "Wikipedia",
                "success": True
            }
    except Exception as exc:
        logging.warning("Wikipedia API fallback failed: %s", exc)

    return {
        "title": "",
        "summary": "",
        "source": "Wikipedia",
        "success": False
    }


__all__ = ["search_wikipedia", "should_use_wikipedia", "wiki", "clean_query"]
