"""Simple context compression utilities.

This module implements a lightweight extractor that concatenates and trims
retrieved chunks to keep prompts small.
"""
from typing import List, Dict, Any
import json


def compress_context(retrieved: Any, max_chars: int = 1500) -> str:
    """Compress a list of retrieved chunk dicts into a single string."""
    if isinstance(retrieved, str):
         texts = [retrieved]
    elif isinstance(retrieved, list):
         texts = [r.get("text", "") if isinstance(r, dict) else str(r) for r in retrieved]
    else:
         try:
             texts = [json.dumps(retrieved, ensure_ascii=False)]
         except Exception:
             texts = [str(retrieved)]
             
    joined = "\n\n".join(texts).strip()
    if len(joined) <= max_chars:
        return joined

    # keep first 60% and last 40% approx
    head_len = int(max_chars * 0.6)
    tail_len = max_chars - head_len
    head = joined[:head_len].rsplit("\n", 1)[0]
    tail = joined[-tail_len:].split("\n", 1)[-1]
    return head + "\n\n...\n\n" + tail


def build_system_prompt(memory_context: str, wiki_context: str) -> str:
    """Create the small system prompt used by the assistant."""
    system_prompt = f"""
Current Year: 2026

Use retrieved knowledge as the primary source.

MEMORY:
{memory_context}

KNOWLEDGE:
{wiki_context}
"""
    return system_prompt
