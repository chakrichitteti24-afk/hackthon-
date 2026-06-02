from typing import List


def compress_context(text: str, max_chars: int = 3000) -> str:
    """Naive context compressor: keeps head and tail when text is oversized.

    This is intentionally simple and fast for demo purposes. Replace with an
    LLM-based summarizer or more advanced compression when available.
    """
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_chars:
        return text
    head = text[: max_chars // 2]
    tail = text[-(max_chars // 2) :]
    return head + "\n\n...[truncated]...\n\n" + tail
