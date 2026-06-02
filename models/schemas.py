"""Pydantic models for OmniFlow API request and response payloads.

Includes message timeline items carrying metadata for analytics and UI badges.
"""

from typing import Any, Optional, List, Dict

from pydantic import BaseModel


class ChatRequest(BaseModel):
    user_id: str
    agent_type: Optional[str] = None
    message: str


class MessageItem(BaseModel):
    role: str
    content: str
    timestamp: str
    llm_used: Optional[str] = None
    web_search_used: Optional[bool] = False
    sentiment: Optional[str] = None
    agent_type: Optional[str] = None
    response_validated: Optional[bool] = None


class ChatResponse(BaseModel):
    reply: str
    agent_type: str
    sentiment: str
    escalate: bool
    llm_used: str
    web_searched: bool
    session_id: str
    routing: Optional[Dict[str, Any]] = None
    web_sources: Optional[List[str]] = None
    response_ms: Optional[int] = None
    response_validated: Optional[bool] = None
    confidence: Optional[int] = None
    sources: Optional[List[str]] = None
    memory: Optional[Dict[str, Any]] = None


class SessionResponse(BaseModel):
    user_id: str
    messages: List[MessageItem]
    sentiment_score: float
    escalated: bool
    memory: Optional[Dict[str, Any]] = None


class EscalateResponse(BaseModel):
    user_id: str
    status: str
    message: str
