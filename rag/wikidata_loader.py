import requests
from typing import List, Dict


def search_wikidata(query: str, limit: int = 5) -> List[Dict]:
    """Search Wikidata for entities matching *query* and return lightweight results."""
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "search": query,
        "limit": limit,
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []

    results: List[Dict] = []
    for item in data.get("search", []):
        results.append(
            {
                "id": item.get("id"),
                "label": item.get("label"),
                "description": item.get("description"),
            }
        )
    return results
"""Simple Wikidata retrieval helpers.

Provides a small wrapper around the Wikidata search API with graceful
failure handling and a compact result format suitable for RAG.
"""
from typing import List, Dict
import requests


def search_wikidata(query: str, max_results: int = 3, timeout: float = 5.0) -> Dict[str, object]:
    """Search Wikidata for *query* and return a compact structure.

    Returns dict: {"success": bool, "results": [ {id,label,description,url} ] }
    """
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "search": query,
        "limit": max_results,
    }

    try:
        resp = requests.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        out: List[Dict[str, str]] = []
        for item in data.get("search", [])[:max_results]:
            qid = item.get("id")
            label = item.get("label") or ""
            desc = item.get("description") or ""
            link = f"https://www.wikidata.org/wiki/{qid}" if qid else ""
            out.append({"id": qid, "label": label, "description": desc, "url": link})
        return {"success": True, "results": out}
    except Exception:
        return {"success": False, "results": []}


__all__ = ["search_wikidata"]
