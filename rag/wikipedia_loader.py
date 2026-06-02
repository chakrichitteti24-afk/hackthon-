"""Wikipedia loader utilities using `wikipedia-api`.

Functions to search, fetch and chunk Wikipedia page contents.
"""
from typing import List, Dict
import re


def clean_text(text: str) -> str:
    """Basic cleaning: remove bracketed citations, excessive whitespace."""
    if not text:
        return ""
    # remove bracketed references like [1], [citation needed]
    text = re.sub(r"\[[^\]]+\]", "", text)
    # replace multiple newlines with two
    text = re.sub(r"\n{2,}", "\n\n", text)
    # collapse spaces
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks of approximate `chunk_size` characters.

    Overlap helps preserve context across chunk boundaries.
    """
    if not text:
        return []
    text = text.replace("\r\n", "\n").strip()
    if len(text) <= chunk_size:
        return [text]

    chunks: List[str] = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = text[start:end]
        chunks.append(chunk.strip())
        if end == text_len:
            break
        start = max(0, end - overlap)

    return chunks


def search_and_load(query: str, max_pages: int = 3) -> List[Dict[str, str]]:
    """Search Wikipedia and return up to `max_pages` pages as dicts with title, url and cleaned text.

    Uses `wikipediaapi` which is installed from the `wikipedia-api` package.
    """
    try:
        import wikipediaapi
    except Exception as e:
        raise RuntimeError("Please install wikipedia-api (pip install wikipedia-api)") from e

    wiki = wikipediaapi.Wikipedia("en")
    results: List[Dict[str, str]] = []
    # wikipediaapi supports a simple search helper via the `search` function
    try:
        titles = wiki.search(query)
    except Exception:
        # fallback: try the `wikipedia` package search
        try:
            import wikipedia

            titles = wikipedia.search(query)
        except Exception:
            titles = []

    for t in titles[:max_pages]:
        page = wiki.page(t)
        if not page or not page.exists():
            continue
        text = clean_text(page.text)
        results.append({"title": page.title, "url": page.fullurl, "text": text})

    return results
