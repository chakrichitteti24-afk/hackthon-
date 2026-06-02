"""Groq-based routing engine for intent, sentiment, and agent selection.

Enforces that Groq only performs:
1. Intent Detection
2. Sentiment Analysis
3. Agent Selection
4. Query Classification
"""
import os
import json
import logging
from typing import Dict, List, Any
from groq import Groq
from config import GROQ_API_KEY

ROUTER_SYSTEM_PROMPT = """You are the OmniFlow AI Routing Engine.
Analyze the user's message and return a JSON object with:
1. "intent": One of "Product Recommendation", "Market Analysis", "Troubleshooting", "General Inquiry".
2. "sentiment": One of "Positive", "Neutral", "Negative", "Very Negative".
3. "agent": One of "Sales Agent", "Insight Agent", "Support Agent".
   Rules for Agent Selection:
   - "Sales Agent" when: product recommendation, buying intent, comparison, budget discussions, shopping guidance.
   - "Insight Agent" when: trends, market analysis, strategic questions, business insights.
   - "Support Agent" when: complaints, issues, frustration, troubleshooting.
   - Sentiment overrides: Negative/Very Negative MUST go to "Support Agent".
4. "confidence": Integer percentage between 50 and 100 (e.g. 95).
5. "reason": Brief explanation of why this routing was chosen.

Output MUST be strictly valid JSON. Do not include markdown code block formatting (like ```json).
"""

# Deterministic Heuristic Fallback
def _heuristic_route(text: str) -> Dict[str, Any]:
    text_lower = (text or "").lower()
    
    # Intent Detection
    if any(k in text_lower for k in ["recommend", "buy", "price", "pricing", "cost", "budget"]):
        intent = "Product Recommendation"
        agent = "Sales Agent"
    elif any(k in text_lower for k in ["trend", "market", "analysis", "compare", "vs"]):
        intent = "Market Analysis"
        agent = "Insight Agent"
    elif any(k in text_lower for k in ["broken", "error", "fail", "issue", "trouble", "overheating", "frustrated"]):
        intent = "Troubleshooting"
        agent = "Support Agent"
    else:
        intent = "General Inquiry"
        agent = "Sales Agent"
        
    # Sentiment Detection
    if any(k in text_lower for k in ["angry", "frustrated", "terrible", "worst", "garbage"]):
        sentiment = "Very Negative"
        agent = "Support Agent"
    elif any(k in text_lower for k in ["bad", "disappointing", "poor"]):
        sentiment = "Negative"
        agent = "Support Agent"
    elif any(k in text_lower for k in ["great", "love", "good", "happy"]):
        sentiment = "Positive"
    else:
        sentiment = "Neutral"

    return {
        "intent": intent,
        "sentiment": sentiment,
        "agent": agent,
        "confidence": 85,
        "reason": "Fallback heuristic matching"
    }

def route_agent(message: str, history: List[Dict] = None) -> Dict[str, Any]:
    """Classify the user query using Groq. Falls back to heuristics if Groq fails."""
    if history is None:
        history = []
        
    text = (message or "").strip()
    if not text:
        return {
            "agent": "sales",
            "intent": "General Inquiry",
            "sentiment_detected": "Neutral",
            "urgency": "normal",
            "stage": "awareness",
            "confidence": 0.75,
            "reasons": ["General inquiry: empty message defaults to Sales Agent"]
        }

    parsed = None
    if GROQ_API_KEY:
        try:
            client = Groq(api_key=GROQ_API_KEY, max_retries=0, timeout=5.0)
            chat_completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
                    {"role": "user", "content": text}
                ],
                temperature=0.0,
                max_tokens=150,
            )
            raw_response = chat_completion.choices[0].message.content.strip()
            # Remove possible code blocks
            if raw_response.startswith("```"):
                lines = raw_response.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_response = "\n".join(lines).strip()
            parsed = json.loads(raw_response)
        except Exception as e:
            logging.warning("Groq router call failed: %s. Using heuristic fallback.", e)
            parsed = None

    if not parsed:
        parsed = _heuristic_route(text)

    # Normalize agent names for the orchestrator
    agent_map = {
        "sales agent": "sales",
        "insight agent": "insight",
        "support agent": "support",
        "sales": "sales",
        "insight": "insight",
        "support": "support"
    }
    raw_agent = str(parsed.get("agent", "sales")).lower().strip()
    agent = agent_map.get(raw_agent, "sales")
    
    # Normalize sentiment names to lowercase
    sentiment = str(parsed.get("sentiment", "neutral")).lower().strip()
    
    # Normalize intent names
    intent_map = {
        "product recommendation": "purchase",
        "market analysis": "analysis",
        "troubleshooting": "troubleshooting",
        "general inquiry": "general",
        "purchase": "purchase",
        "analysis": "analysis",
        "general": "general"
    }
    raw_intent = str(parsed.get("intent", "General Inquiry")).lower().strip()
    intent = intent_map.get(raw_intent, raw_intent)
    
    # Map urgency
    urgency = "high" if sentiment in ["negative", "very negative"] else "normal"
    
    # Map stage
    stage = "consideration" if agent == "sales" else "post-purchase" if agent == "support" else "awareness"

    # Normalize confidence to decimal float
    conf = parsed.get("confidence", 90)
    try:
        confidence = float(conf) / 100.0 if conf > 1 else float(conf)
    except Exception:
        confidence = 0.90

    return {
        "agent": agent,
        "intent": intent,
        "sentiment_detected": sentiment,
        "urgency": urgency,
        "stage": stage,
        "confidence": confidence,
        "reasons": [parsed.get("reason", "Groq classified routing")]
    }

__all__ = ["route_agent"]
