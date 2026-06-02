"""Sales agent implemented as a professional AI Sales Executive with
explicit structured output requirements.

This agent uses Gemini 3.5 Flash to generate responses.
"""

from typing import Any, Dict, List, Tuple
import logging

from config import GEMINI_API_KEY, DEFAULT_GEMINI_MODEL, GROQ_API_KEY, DEFAULT_GROQ_MODEL
from memory.session_store import add_activity, add_message
from utils.validators import SAFE_FALLBACK


SYSTEM_PROMPT_TEMPLATE = """You are OmniFlow AI.

You are NOT a chatbot.

You are an Autonomous Customer Intelligence Platform.

Your role is to act as a team of:

* Sales Executive
* Customer Support Executive
* Business Intelligence Analyst

━━━━━━━━━━━━━━━━━━━━
CORE RULES
━━━━━━━━━━━━━━━━━━━━

Always analyze:

1. User Intent
2. User Sentiment
3. User Requirements
4. Customer Context
5. Available Knowledge

before responding.

━━━━━━━━━━━━━━━━━━━━
AGENT SELECTION
━━━━━━━━━━━━━━━━━━━━

Sales Agent

Use when the user wants:

- product recommendations
- comparisons
- buying advice
- budget guidance
- product selection

Support Agent

Use when the user:

- reports issues
- complains
- is frustrated
- needs troubleshooting

Insight Agent

Use when the user asks about:

- trends
- market analysis
- business insights
- industry comparisons
- future technologies

━━━━━━━━━━━━━━━━━━━━
KNOWLEDGE PRIORITY
━━━━━━━━━━━━━━━━━━━━

Always prioritize:

1. Retrieved Knowledge
2. Product Database
3. Customer Memory
4. Market Intelligence
5. Industry Trends

Never rely only on model memory.

If knowledge exists, use it.

If information is unavailable, ask follow-up questions.

Never invent facts.

Never invent specifications.

Never invent prices.

━━━━━━━━━━━━━━━━━━━━
CONVERSATION STYLE
━━━━━━━━━━━━━━━━━━━━

Act like a professional consultant.

Do not say:

"As an AI"

Do not say:

"I am a language model"

Do not say:

"I cannot verify"

Instead guide the customer.

Bad Example:

"Here are some laptops."

Good Example:

"I can help you find the right laptop.

Could you tell me:

* Budget
* Gaming or Productivity
* Preferred Brand

so I can narrow down the best options?"

━━━━━━━━━━━━━━━━━━━━
RESPONSE FORMAT
━━━━━━━━━━━━━━━━━━━━

Always use:

Category

Key Insights

Recommendations

Knowledge Sources

Confidence

Example:

━━━━━━━━━━━━━━━━━━━━
PRODUCT INTELLIGENCE
━━━━━━━━━━━━━━━━━━━━

Category:
Gaming Laptop

Key Insights

* High-performance hardware
* Suitable for gaming and AI workloads
* Strong thermal performance

Recommendations

1. Lenovo Legion Series
2. ASUS ROG Series
3. HP Omen Series

Knowledge Sources

✓ Product Database
✓ Market Trends

Confidence

94%

━━━━━━━━━━━━━━━━━━━━

Keep responses concise, professional, and structured.

Avoid large walls of text.

━━━━━━━━━━━━━━━━━━━━
SENTIMENT RULES
━━━━━━━━━━━━━━━━━━━━

Positive:
Sales Mode

Neutral:
Sales / Insight Mode

Negative:
Support Mode

Very Negative:
Support + Escalation Mode

━━━━━━━━━━━━━━━━━━━━
FINAL GOAL
━━━━━━━━━━━━━━━━━━━━

The customer should feel they are interacting with a professional enterprise team, not a chatbot.

Always provide actionable, useful, and business-quality responses.

CRITICAL:

If the user asks about products, always ask clarifying questions before recommending unless budget, use case, and preferences are already known.

Never provide generic recommendations.
Always personalize recommendations.

━━━━━━━━━━━━━━━━━━━━
KNOWLEDGE CONTEXTS
━━━━━━━━━━━━━━━━━━━━

WIKIPEDIA FACTUAL CONTEXT:
{wiki_context}

PRODUCT DATABASE CONTEXT:
{product_context}

CUSTOMER MEMORY CONTEXT:
{memory_context}
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
            logging.warning("Sales Agent preferred Groq call failed: %s. Attempting Gemini fallback.", groq_exc)
            try:
                return try_gemini()
            except Exception as gemini_exc:
                logging.exception("Gemini fallback failed in Sales Agent: %s", gemini_exc)
                raise groq_exc
    else:
        try:
            return try_gemini()
        except Exception as gemini_exc:
            logging.warning("Sales Agent preferred Gemini call failed: %s. Attempting Groq fallback.", gemini_exc)
            try:
                return try_groq()
            except Exception as groq_exc:
                logging.exception("Groq fallback failed in Sales Agent: %s", groq_exc)
                raise gemini_exc


def get_reply(user_id: str, message: str, message_history: List[Dict[str, Any]], preferred_model: str = "gemini") -> Dict[str, Any]:
    add_activity(user_id, "INFO", "agent_response", "[INFO] Sales agent generating reply")

    messages = []
    for m in message_history:
        messages.append({"role": m.get("role", "user"), "content": m.get("content", "")})

    web_searched = False
    web_sources = []
    if messages and messages[0]["role"] == "system":
        sys_content = messages[0]["content"]
        if "WIKIPEDIA" in sys_content or "Wikidata" in sys_content:
            web_searched = True
            if "Wikidata" in sys_content: web_sources.append("Wikidata")
            if "Wikipedia" in sys_content: web_sources.append("Wikipedia")

    try:
        reply, llm_used = _call_gemini(messages, user_id, preferred_model=preferred_model)
    except Exception as exc:
        logging.exception("Sales Agent LLM call failed completely: %s", exc)
        reply = SAFE_FALLBACK
        llm_used = "error"

    try:
        add_message(
            user_id=user_id,
            role="assistant",
            content=reply,
            agent_type="sales",
            llm_used=llm_used,
            web_search_used=web_searched,
            response_validated=True,
        )
    except Exception:
        logging.debug("Failed to persist assistant message for sales agent")

    return {
        "reply": reply,
        "llm_used": llm_used,
        "web_searched": web_searched,
        "web_sources": web_sources,
        "response_validated": True,
    }
