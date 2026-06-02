"""Async activity logger for orchestration events.

Provides a tiny non-blocking wrapper around `memory.session_store.add_activity`
so orchestration can log events without blocking the request path.
"""
from threading import Thread
from typing import Callable
import os

from memory.session_store import add_activity


def _safe_call(fn: Callable, *a, **kw):
    try:
        fn(*a, **kw)
    except Exception:
        # Best-effort; swallow errors to avoid impacting request flow
        pass


_ASYNC = os.getenv("OMNIFLOW_ASYNC_LOGGING", "0") == "1"


def log_activity_async(user_id: str, level: str, category: str, message: str) -> None:
    """Log activity entry.

    By default this function will perform a synchronous write to the in-memory
    session store to preserve deterministic behavior in tests and local
    development. Set `OMNIFLOW_ASYNC_LOGGING=1` in the environment to enable
    non-blocking background writes.
    """
    if _ASYNC:
        t = Thread(target=_safe_call, args=(add_activity, user_id, level, category, message), daemon=True)
        t.start()
    else:
        # Synchronous by default for determinism
        _safe_call(add_activity, user_id, level, category, message)


__all__ = ["log_activity_async"]
