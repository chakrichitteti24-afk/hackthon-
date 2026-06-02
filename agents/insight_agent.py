"""Insight agent implemented to provide market analysis and trends.

This agent uses Gemini 3.5 Flash to generate responses.
"""

from typing import Any, Dict, List, Optional, Tuple
import logging

from config import GEMINI_API_KEY, DEFAULT_GEMINI_MODEL, GROQ_API_KEY, DEFAULT_GROQ_MODEL
from memory.session_store import add_activity, add_message, update_session
from utils.validators import SAFE_FALLBACK


SYSTEM_PROMPT_TEMPLATE = """You are OmniFlow AI, a Business Analyst and Insight Agent.

Current Year: 2026.

STRICT RETRIEVAL-FIRST POLICY & ANTI-HALLUCINATION:
- DO NOT answer queries using internal model memory.
- NEVER invent or guess trends, statistics, or benchmarks.
- If exact information is unavailable, state it clearly.
- NEVER display "Reliable factual information could not be verified."
- NEVER display "[WIKIPEDIA]", "[GROQ]", "[FACTUAL_MODE]"

RESPONSE FORMAT:
You MUST format your response EXACTLY as follows (use markdown, but keep these sections):
Category

Key Insights

Recommendations

Knowledge Sources

Confidence

Example:
Category
Market Analysis

Key Insights
* AI trends show 50% growth
* Edge computing is expanding

Recommendations
1. Invest in AI-ready devices
2. Monitor edge infrastructure

Knowledge Sources
✓ Trend Intelligence
✓ Customer Memory
✓ Wikipedia

Confidence
90%
"""


def _call_gemini(messages: List[Dict[str, str]], user_id: str, preferred_model: str = "gemini", response_mime_type: Optional[str] = None) -> Tuple[str, str]:
    def try_gemini():
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured")
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        
        system_instruction = None
        gemini_messages = []
        for m in messages:
            role = m.get("role")
            content = m.get("content")
            if role == "system":
                system_instruction = content
            elif role == "assistant":
                gemini_messages.append({"role": "model", "parts": [content]})
            else:
                gemini_messages.append({"role": "user", "parts": [content]})
        
        model_name = DEFAULT_GEMINI_MODEL or "gemini-3.5-flash"
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction
        )
        
        gen_config = {"temperature": 0.2, "max_output_tokens": 800}
        if response_mime_type:
            gen_config["response_mime_type"] = response_mime_type

        if gemini_messages:
            response = model.generate_content(
                gemini_messages,
                generation_config=gen_config
            )
        else:
            response = model.generate_content(
                "Hello",
                generation_config=gen_config
            )
        
        reply = response.text
        if not reply or not reply.strip():
            raise ValueError("Empty response from Gemini")
        return reply.strip(), "gemini"

    def try_groq():
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not configured")
        from groq import Groq
        groq_model = DEFAULT_GROQ_MODEL or "llama-3.1-8b-instant"
        client = Groq(api_key=GROQ_API_KEY)
        
        groq_messages = []
        for m in messages:
            groq_messages.append({"role": m.get("role"), "content": m.get("content")})
            
        kwargs = {
            "model": groq_model,
            "messages": groq_messages,
            "temperature": 0.2,
            "max_tokens": 800,
        }
        if response_mime_type == "application/json":
            kwargs["response_format"] = {"type": "json_object"}
            
        completion = client.chat.completions.create(**kwargs)
        reply = completion.choices[0].message.content.strip()
        return reply, "groq"

    # Execution order based on preferred_model
    if preferred_model == "groq":
        try:
            return try_groq()
        except Exception as groq_exc:
            logging.warning("Insight Agent preferred Groq call failed: %s. Attempting Gemini fallback.", groq_exc)
            try:
                return try_gemini()
            except Exception as gemini_exc:
                logging.exception("Gemini fallback failed in Insight Agent: %s", gemini_exc)
                raise groq_exc
    else:
        try:
            return try_gemini()
        except Exception as gemini_exc:
            logging.warning("Insight Agent preferred Gemini call failed: %s. Attempting Groq fallback.", gemini_exc)
            try:
                return try_groq()
            except Exception as groq_exc:
                logging.exception("Groq fallback failed in Insight Agent: %s", groq_exc)
                raise gemini_exc


def _rule_based_sentiment(message: str) -> Dict[str, Any]:
    """Fallback rule-based sentiment classification when LLM is unavailable or for testing."""
    text_lower = (message or "").lower()
    if any(k in text_lower for k in ["broken", "terrible", "worst", "angry", "frustrated", "fail", "error"]):
        return {
            "sentiment": "angry",
            "score": 8.0,
            "escalate": True
        }
    return {
        "sentiment": "neutral",
        "score": 2.0,
        "escalate": False
    }


def get_sentiment(user_id: str, message: str, message_history: List[Dict[str, Any]], preferred_model: str = "gemini") -> Dict[str, Any]:
    """Provides market insights and also analyzes sentiment."""
    add_activity(user_id, "INFO", "agent_response", "[INFO] Insight agent generating reply")

    sys_instruction = (
        SYSTEM_PROMPT_TEMPLATE +
        "\n\nCRITICAL: You must output a valid JSON object ONLY. Do not wrap it in markdown formatting other than optionally ```json.\n"
        "The JSON object must contain these exact keys:\n"
        "- 'reply': A string containing your analyst response formatted with the Category, Key Insights, Recommendations, Knowledge Sources, and Confidence sections.\n"
        "- 'sentiment': A string ('positive', 'neutral', 'negative', 'angry') representing the user's sentiment.\n"
        "- 'score': A number from 0.0 to 10.0 representing the intensity of negative sentiment (higher is more negative/angry).\n"
        "- 'escalate': A boolean (true/false) indicating if the query requires urgent human intervention.\n"
    )
    messages = []
    for m in message_history:
        role = m.get("role", "user")
        content = m.get("content", "")
        if role == "system":
            sys_instruction += f"\n\nFACTUAL CONTEXT:\n{content}"
        else:
            messages.append({"role": role, "content": content})
    messages.insert(0, {"role": "system", "content": sys_instruction})
    
    # Ensure current query is included if history is empty
    if not any(m.get("role") == "user" for m in messages):
        messages.append({"role": "user", "content": message})

    try:
        reply_raw, llm_used = _call_gemini(messages, user_id, preferred_model=preferred_model, response_mime_type="application/json")
        import json
        try:
            parsed = json.loads(reply_raw)
        except Exception as parse_err:
            print(f"\n--- DEBUG: RAW GEMINI REPLY ---\n{reply_raw}\n-------------------------------\n")
            import re
            # use greedy search to find outermost braces
            match = re.search(r"\{.*\}", reply_raw, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
            else:
                raise parse_err
        
        reply = parsed.get("reply") or reply_raw
        sentiment = parsed.get("sentiment", "neutral")
        score = float(parsed.get("score", 0.0))
        escalate = bool(parsed.get("escalate", False))
    except Exception as exc:
        logging.exception("Insight agent LLM call failed completely: %s", exc)
        fallback = _rule_based_sentiment(message)
        sentiment = fallback["sentiment"]
        score = fallback["score"]
        escalate = fallback["escalate"]
        reply = SAFE_FALLBACK
        llm_used = "error"

    try:
        add_message(
            user_id=user_id,
            role="assistant",
            content=reply,
            agent_type="insight",
            llm_used=llm_used,
            web_search_used=False,
            sentiment=sentiment,
            response_validated=True,
        )
    except Exception:
        logging.debug("Failed to persist assistant message for insight agent")

    return {
        "reply": reply,
        "sentiment": sentiment,
        "score": score,
        "escalate": escalate,
        "llm_used": llm_used,
        "web_searched": False,
        "web_sources": [],
        "response_validated": True,
    }
