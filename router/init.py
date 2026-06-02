"""Compatibility shim: router/init.py -> router package entry.

Some deployment scripts or external references may expect `router/init.py`.
This file re-exports the router API.
"""

from router.message_router import route_message

__all__ = ["route_message"]
