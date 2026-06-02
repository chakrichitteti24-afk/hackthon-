"""Support agent implemented to provide customer support.

This agent uses Gemini 3.5 Flash to generate responses.
"""

from typing import Any, Dict, List, Tuple
import logging

from config import GEMINI_API_KEY, DEFAULT_GEMINI_MODEL, GROQ_API_KEY, DEFAULT_GROQ_MODEL
from memory.session_store import add_activity, add_message
from utils.validators import SAFE_FALLBACK


SYSTEM_PROMPT_TEMPLATE = """You are OmniFlow AI, a Customer Support Executive.

Current Year: 2026.

STRICT RETRIEVAL-FIRST POLICY & ANTI-HALLUCINATION:
- Provide clear, step-by-step guidance.
- Be professional, empathetic, and direct.
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
Troubleshooting

Key Insights
* Laptop is overheating
* High CPU usage detected

Recommendations
1. Ensure good ventilation
2. Update BIOS

Knowledge Sources
✓ Support Database
✓ Customer Memory

Confidence
95%
"""


def _call_gemini(messages: List[Dict[str, str]], user_id: str, preferred_model: str = "gemini") -> Tuple[str, str]:
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
        
        if gemini_messages:
            response = model.generate_content(
                gemini_messages,
                generation_config={"temperature": 0.2, "max_output_tokens": 800}
            )
        else:
            response = model.generate_content(
                "Hello",
                generation_config={"temperature": 0.2, "max_output_tokens": 800}
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
            
        completion = client.chat.completions.create(
            model=groq_model,
            messages=groq_messages,
            temperature=0.2,
            max_tokens=800,
        )
        reply = completion.choices[0].message.content.strip()
        return reply, "groq"

    # Execution order based on preferred_model
    if preferred_model == "groq":
        try:
            return try_groq()
        except Exception as groq_exc:
            logging.warning("Support Agent preferred Groq call failed: %s. Attempting Gemini fallback.", groq_exc)
            try:
                return try_gemini()
            except Exception as gemini_exc:
                logging.exception("Gemini fallback failed in Support Agent: %s", gemini_exc)
                raise groq_exc
    else:
        try:
            return try_gemini()
        except Exception as gemini_exc:
            logging.warning("Support Agent preferred Gemini call failed: %s. Attempting Groq fallback.", gemini_exc)
            try:
                return try_groq()
            except Exception as groq_exc:
                logging.exception("Groq fallback failed in Support Agent: %s", groq_exc)
                raise gemini_exc


def get_reply(user_id: str, message: str, message_history: List[Dict[str, Any]], preferred_model: str = "gemini") -> Dict[str, Any]:
    add_activity(user_id, "INFO", "agent_response", "[INFO] Support agent generating reply")

    sys_instruction = SYSTEM_PROMPT_TEMPLATE
    messages = []
    for m in message_history:
        role = m.get("role", "user")
        content = m.get("content", "")
        if role == "system":
            sys_instruction += f"\n\nFACTUAL CONTEXT:\n{content}"
        else:
            messages.append({"role": role, "content": content})
    messages.insert(0, {"role": "system", "content": sys_instruction})

    try:
        reply, llm_used = _call_gemini(messages, user_id, preferred_model=preferred_model)
    except Exception as exc:
        logging.exception("Support Agent LLM call failed completely: %s", exc)
        reply = SAFE_FALLBACK
        llm_used = "error"

    try:
        add_message(
            user_id=user_id,
            role="assistant",
            content=reply,
            agent_type="support",
            llm_used=llm_used,
            web_search_used=False,
            response_validated=True,
        )
    except Exception:
        logging.debug("Failed to persist assistant message for support agent")

    return {
        "reply": reply,
        "llm_used": llm_used,
        "web_searched": False,
        "web_sources": [],
        "response_validated": True,
    }
