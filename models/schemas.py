"""Pydantic models for OmniFlow API request and response payloads."""

from typing import Any, Optional, List, Dict

from pydantic import BaseModel


class ChatRequest(BaseModel):
    user_id: str
    agent_type: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    sentiment: str
    agent_type: str
    escalate: bool
    session_id: str


class SessionResponse(BaseModel):
    user_id: str
    messages: List[Dict[str, Any]]
    sentiment_score: float
    escalated: bool


class EscalateResponse(BaseModel):
    user_id: str
    status: str
    message: str
