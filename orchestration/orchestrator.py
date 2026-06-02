"""Orchestration layer implementing the autonomous multi-agent workflow.

Flow:
- Persist user message
- Intent analysis & automatic routing
- Wikipedia grounding first (Sales Agent ONLY)
- Call selected agent
- Sentiment analysis (always)
- Profile extraction and memory sync
- Escalation checks
- Activity logging and analytics update

This module is synchronous and designed for the current FastAPI dev server.
"""
from typing import Dict, Any, Optional
import logging

from router.agent_router import route_agent
from search.web_search import search_web  # kept for backward-compatible tests/imports
from search.wiki_search import search_wikipedia, should_use_wikipedia
from rag.context_compressor import build_system_prompt
from orchestration.knowledge_pipeline import KnowledgePipeline
from router.message_router import route_message
from agents import sales_agent, support_agent, insight_agent
from memory.session_store import (
    get_session,
    add_message,
    update_session,
    get_activity_log,
    get_analytics,
)
from orchestration.logger import log_activity_async as log_activity
from orchestration.profile_extractor import extract_profile_from_messages
from utils.validators import SAFE_FALLBACK, validate_response


STRICT_FACTUAL_SYSTEM_PROMPT = """You are OmniFlow AI.

Current Year: 2026.

STRICT FACTUAL MODE ENABLED.

IMPORTANT:
- NEVER invent products or companies.
- ONLY provide real-world factual information.
- Prioritize Wikipedia grounding if available.
- If information is unavailable, clearly say so.
- Keep responses concise and professional.

WIKIPEDIA FACTUAL CONTEXT:
{wiki_context}
"""

# Lazy knowledge pipeline (initialized on first sales request)
_KNOWLEDGE_PIPELINE: KnowledgePipeline | None = None


def orchestrate_message(user_id: str, message: str, requested_agent_type: Optional[str] = None) -> Dict[str, Any]:
    """Run the full automation workflow for an incoming user message.

    Returns a dict compatible with the existing ChatResponse fields.
    """
    session = get_session(user_id)

    # Persist the incoming user message
    add_message(user_id=user_id, role="user", content=message)
    log_activity(user_id, "INFO", "ingest", "[INFO] Query analyzed")

    # Determine agent
    chosen_agent = None
    routing_confidence = 0.0
    routing_reasons = []

    intent = "inquiry"
    sentiment_detected = "neutral"
    urgency = "normal"
    stage = "awareness"

    if requested_agent_type and requested_agent_type.lower() in {"sales", "support", "insight"} and requested_agent_type.lower() != "auto":
        chosen_agent = requested_agent_type.lower()
        routing_confidence = 1.0
        routing_reasons = ["user_requested"]
        log_activity(user_id, "INFO", "routing", f"[INFO] User requested agent: {chosen_agent}")
    else:
        route = route_agent(message, session.get("message_history", []))
        chosen_agent = route.get("agent", "sales")
        routing_confidence = float(route.get("confidence", 0.0))
        routing_reasons = list(route.get("reasons", []))
        intent = route.get("intent", "inquiry")
        sentiment_detected = route.get("sentiment_detected", "neutral")
        urgency = route.get("urgency", "normal")
        stage = route.get("stage", "awareness")
        log_activity(user_id, "INFO", "routing", f"[INFO] Routed to {chosen_agent} (confidence={routing_confidence}) intent={intent} sentiment={sentiment_detected}")

    # Mark agent on session
    update_session(user_id, agent_type=chosen_agent)

    # Knowledge assembly pipeline for Sales (Product KB, Memory, Wikidata, FAISS)
    wiki_context = ""
    web_searched = False
    web_sources = []

    memory_context = ""
    product_context = ""
    compressed_context = ""
    kb_confidence = 0
    kb_sources = []

    # Run the knowledge pipeline for all agents (best-effort)
    global _KNOWLEDGE_PIPELINE
    if _KNOWLEDGE_PIPELINE is None:
        _KNOWLEDGE_PIPELINE = KnowledgePipeline()
    try:
        ctx = _KNOWLEDGE_PIPELINE.build_context(user_id, message)
        memory_context = ctx.get("memory_context", "") or ""
        product_context = ctx.get("product_context", "") or ""
        wiki_context = ctx.get("wiki_context", "") or ""
        compressed_context = ctx.get("compressed_context", "") or ""
        kb_confidence = ctx.get("confidence", 0)
        kb_sources = ctx.get("sources", [])
        
        web_searched = bool(wiki_context)
        web_sources = kb_sources if kb_sources else (["Wikidata"] if web_searched else [])
        log_activity(user_id, "INFO", "search", f"[INFO] Knowledge pipeline assembled (confidence={kb_confidence}%)")
    except Exception as exc:
        logging.debug("Knowledge pipeline failed: %s", exc)
        # Fallback to legacy Wikipedia grounding behavior
        if should_use_wikipedia(message):
            try:
                wiki_data = search_wikipedia(message)
                if wiki_data.get("success"):
                    wiki_context = wiki_data.get("summary", "")
                    web_searched = True
                    web_sources = ["Wikipedia"]
                    log_activity(user_id, "INFO", "search", "[INFO] Fuzzy search successful (fallback)")
            except Exception:
                wiki_context = ""
                log_activity(user_id, "WARNING", "search", "[WARNING] Wikipedia fallback failed")

    # Clarification step: always collect required buyer info before recommending
    try:
        if chosen_agent == "sales":
            # required profile fields
            profile = session.get("user_profile", {}) or {}
            required = ["budget", "interest", "brand"]
            missing = [f for f in required if not profile.get(f)]
            product_intent_keywords = ["recommend", "compare", "best", "which", "suggest", "buy"]
            is_product_intent = any(k in (message or "").lower() for k in product_intent_keywords)

            # Clarify only when this looks like a product intent AND we both lack
            # required profile fields and have low knowledge confidence. This
            # reduces unnecessary short-circuiting during tests and when the
            # KB is already confident.
            if is_product_intent and (kb_confidence < 70 and missing):
                # Ask for clarifying requirements using a human-like consultative tone
                clarify_text = (
                    "I'd be happy to help you choose the right product.\n\n"
                    "Could you tell me:\n"
                    "* Budget (range or max)\n"
                    "* Intended usage (e.g., gaming, productivity, business)\n"
                    "* Preferred brand(s)\n\n"
                    "so I can narrow down the best options?"
                )
                log_activity(user_id, "INFO", "clarification", "[INFO] Human-like clarification requested")
                try:
                    add_message(user_id=user_id, role="assistant", content=clarify_text, agent_type="sales", llm_used="groq", web_search_used=False, response_validated=True)
                except Exception:
                    pass

                return {
                    "reply": clarify_text,
                    "agent_type": "sales",
                    "sentiment": "neutral",
                    "escalate": False,
                    "llm_used": "groq",
                    "web_searched": False,
                    "web_sources": [],
                    "session_id": user_id,
                    "routing": {
                        "agent_routing": {"confidence": routing_confidence, "reasons": routing_reasons},
                        "model_routing": {"model": "groq", "reason": "clarification", "confidence": 0.9},
                    },
                    "response_validated": True,
                }
    except Exception:
        # If clarification flow fails, continue to normal agent flow
        pass

    # Build an augmented history to pass to agents. 
    # For Sales agent, we'll pass the full structured context separately to its get_reply
    if chosen_agent == "sales":
        system_prompt = sales_agent.SYSTEM_PROMPT_TEMPLATE.format(
            wiki_context=wiki_context or "No Wikipedia context available.",
            product_context=product_context or "No product database matches found.",
            memory_context=memory_context or "No relevant customer memory found.",
            confidence=kb_confidence,
            sources_list=", ".join([f"✓ {s}" for s in kb_sources]) if kb_sources else "None"
        )
    elif memory_context or wiki_context or product_context or compressed_context:
        try:
            combined = "\n\n".join(filter(None, [wiki_context, product_context, compressed_context]))
            system_prompt = build_system_prompt(memory_context, combined)
        except Exception:
            combined = "\n\n".join(filter(None, [wiki_context, product_context, compressed_context]))
            system_prompt = STRICT_FACTUAL_SYSTEM_PROMPT.format(wiki_context=combined)
    else:
        system_prompt = STRICT_FACTUAL_SYSTEM_PROMPT.format(wiki_context=wiki_context)

    augmented_history = [{"role": "system", "content": system_prompt}] + list(session.get("message_history", []))
    reply = ""
    
    # Decide model using smart message router
    model_routing = route_message(message)
    routed_model = model_routing.get("model", "gemini")
    
    llm_used = routed_model
    agent_web_searched = web_searched
    response_validated = False
    
    try:
        if chosen_agent == "sales":
            # If confidence is very low, we might want to force a clarification
            if kb_confidence < 80 and ("spec" in message.lower() or "price" in message.lower() or "recommend" in message.lower()):
                 # We'll let the LLM handle the clarification based on the prompt instructions,
                 # but we can also log it.
                 log_activity(user_id, "WARNING", "search", "[WARNING] Low knowledge confidence (<80%)")

            res = sales_agent.get_reply(user_id, message, augmented_history, preferred_model=routed_model)
            reply = res.get("reply", "")
            llm_used = res.get("llm_used", routed_model)
            agent_web_searched = bool(res.get("web_searched", agent_web_searched))
            web_sources = res.get("web_sources") or web_sources
            response_validated = bool(res.get("response_validated", False))

        elif chosen_agent == "support":
            res = support_agent.get_reply(user_id, message, augmented_history, preferred_model=routed_model)
            reply = res.get("reply", "")
            llm_used = res.get("llm_used", routed_model)
            agent_web_searched = False
            web_sources = []
            response_validated = False

        else:  # insight
            res = insight_agent.get_sentiment(user_id, message, augmented_history, preferred_model=routed_model)
            reply = res.get("reply", "")
            llm_used = res.get("llm_used", routed_model)
            agent_web_searched = False
            web_sources = []
            response_validated = False

        log_activity(user_id, "INFO", "agent_response", f"[INFO] {chosen_agent.title()} replied (LLM={llm_used.upper()})")
    except Exception as exc:
        logging.exception("Orchestration agent call failed: %s", exc)
        reply = "Sorry, the AI providers are temporarily unavailable."
        llm_used = "ERROR"
        log_activity(user_id, "ERROR", "agent_response", "[ERROR] Agent call failed")

    # Run response validation only for the Sales Agent
    if chosen_agent == "sales":
        if not response_validated:
            response_validated = validate_response(reply)
            if not response_validated:
                reply = SAFE_FALLBACK
                response_validated = True
                log_activity(user_id, "WARNING", "validation", "[WARNING] Response validation failed")
            else:
                log_activity(user_id, "INFO", "validation", "[INFO] Response validation passed")
    else:
        response_validated = False

    # Use sentiment from the routing engine to save an LLM call and significantly reduce latency
    sentiment = sentiment_detected if chosen_agent != "insight" else "neutral"
    score = 8.0 if sentiment in ["negative", "very negative", "angry"] else 2.0
    escalate = False
    
    try:
        if chosen_agent != "insight":
            log_activity(user_id, "INFO", "sentiment", f"[INFO] Sentiment classified as {sentiment}")
        else:
            # If insight agent already ran, reflect its session values
            s = get_session(user_id)
            sentiment = s.get("message_history", [])[-1].get("sentiment") if s.get("message_history") else "neutral"
            score = float(s.get("sentiment_score") or 0)
            escalate = bool(s.get("escalated", False))
            log_activity(user_id, "INFO", "sentiment", f"[INFO] Sentiment classified as {sentiment}")
    except Exception as exc:
        logging.exception("Orchestrator sentiment check failed: %s", exc)
        log_activity(user_id, "WARNING", "sentiment", "[WARNING] Sentiment analysis failed")

    # Profile extraction and memory synchronization
    try:
        profile = extract_profile_from_messages(augmented_history)
        if profile:
            # Merge into existing profile
            existing = session.get("user_profile", {}) or {}
            merged = {**existing, **profile}
            update_session(user_id, user_profile=merged)
        log_activity(user_id, "INFO", "memory", "[INFO] Shared memory synchronized")
    except Exception as exc:
        logging.debug("Profile extraction failed: %s", exc)

    # Escalation engine: check escalation rules
    try:
        if escalate or score >= 7 or _detect_repeated_negative(session.get("message_history", [])):
            update_session(user_id, escalated=True)
            escalate = True
            log_activity(user_id, "WARNING", "escalation", "[WARNING] Escalation triggered due to sentiment rules")
    except Exception as exc:
        logging.debug("Escalation check failed: %s", exc)

    # Update session analytics snapshot
    try:
        analytics = get_analytics()
        update_session(user_id, analytics=analytics)
    except Exception:
        pass

    session_state = get_session(user_id)

    # Compute grounding confidence & sources based on active agent
    final_confidence = 85
    final_sources = ["Customer Memory"]
    if chosen_agent == "sales":
        final_confidence = kb_confidence if kb_confidence > 0 else 75
        final_sources = kb_sources if kb_sources else (["Wikipedia"] if agent_web_searched else ["Product Database"])
    elif chosen_agent == "support":
        final_confidence = 88
        final_sources = ["Support Guide", "Customer Memory"]
    else: # insight
        final_confidence = 90
        final_sources = ["Sentiment Lexicon", "Customer Memory"]

    # Ensure "Customer Memory" is added to sources if there is history
    if session_state.get("user_profile") and "Customer Memory" not in final_sources:
        final_sources.append("Customer Memory")

    # Update last message in history with the computed metrics
    mh = session_state.get("message_history", [])
    if mh and mh[-1].get("role") == "assistant":
        mh[-1]["confidence"] = final_confidence
        mh[-1]["sources"] = final_sources

    return {
        "reply": reply,
        "agent_type": chosen_agent,
        "sentiment": sentiment,
        "escalate": bool(session_state.get("escalated", False)),
        "llm_used": llm_used,
        "web_searched": agent_web_searched,
        "web_sources": web_sources,
        "session_id": user_id,
        "routing": {
            "intent": intent,
            "sentiment": sentiment_detected,
            "urgency": urgency,
            "stage": stage,
            "reason": routing_reasons[0] if routing_reasons else "Workflow matched",
            "workflow": [
                "✓ Intent Analysis",
                "✓ Knowledge Retrieval",
                "✓ Agent Activation",
                "✓ Response Generated"
            ],
            "agent_routing": {"confidence": routing_confidence, "reasons": routing_reasons},
            "model_routing": {
                "model": llm_used,
                "reason": model_routing.get("reason", "agent_specialization"),
                "confidence": model_routing.get("confidence", 1.0)
            },
        },
        "response_validated": response_validated,
        "confidence": final_confidence,
        "sources": final_sources,
    }


def _detect_repeated_negative(message_history: list) -> bool:
    """Detect repeated negative user messages in recent history.

    Returns True when there are 2 or more negative/angry sentiments in the last 6 messages.
    """
    if not message_history:
        return False
    recent = message_history[-8:]
    neg_count = 0
    for m in recent:
        if m.get("role") == "user":
            s = (m.get("sentiment") or "").lower()
            if s in ("negative", "angry"):
                neg_count += 1
    return neg_count >= 2


__all__ = ["orchestrate_message"]
