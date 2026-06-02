"""Compatibility shim: search/init.py -> search package entry.

Re-export `search_web` for callers that expect this path.
"""

from search.web_search import search_web

__all__ = ["search_web"]
