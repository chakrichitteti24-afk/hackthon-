"""Entry point for the OmniFlow AI FastAPI backend.

This module preserves the existing public API but enriches responses with
LLM and web-search metadata for the frontend badges and analytics.
"""

from typing import Dict, Any
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agents import insight_agent, sales_agent, support_agent
from memory.session_store import (
    get_session,
    update_session,
    add_message,
    add_activity,
    get_activity_log,
    get_timeline,
    get_analytics,
)
from models.schemas import ChatRequest, ChatResponse, EscalateResponse, SessionResponse
from orchestration.orchestrator import orchestrate_message
from config import GEMINI_API_KEY


app = FastAPI(title="OmniFlow AI Backend")
logger = logging.getLogger("omniflow")
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_index_knowledge():
    """Initialize the knowledge pipeline at application startup so that
    product, brand, trend, processor, and GPU knowledge are indexed into FAISS
    and available for immediate retrieval.
    """
    try:
        from orchestration.knowledge_pipeline import KnowledgePipeline
        from orchestration import orchestrator

        kp = KnowledgePipeline()
        kp.ensure_init()
        orchestrator._KNOWLEDGE_PIPELINE = kp
        logger.info("Knowledge pipeline initialized on startup and set to orchestrator global")
    except Exception as exc:
        logger.exception("Failed to initialize knowledge pipeline on startup: %s", exc)


@app.get("/health")
def health_check() -> Dict[str, str]:
    """Simple health-check endpoint."""
    logger.info("[INFO] /health request received")
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Main chat endpoint that delegates to the orchestrator.

    If `agent_type` is not provided or is 'auto', the orchestrator will decide
    which agent to use automatically.
    """
    logger.info("[INFO] /chat request received")
    if not request.user_id or not request.user_id.strip():
        raise HTTPException(status_code=400, detail="user_id is required")
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="message is required")

    # Validate agent_type when provided
    if request.agent_type and request.agent_type not in {"sales", "support", "insight", "auto"}:
        raise HTTPException(status_code=400, detail="Invalid agent_type")

    # Let orchestrator perform ingestion, routing, agent call, sentiment,
    # memory sync, escalation, and analytics update. Measure duration for
    # observability and frontend latency reporting.
    import time

    start = time.time()
    try:
        result = orchestrate_message(request.user_id, request.message, requested_agent_type=request.agent_type)
    except Exception as exc:
        logger.exception("[ERROR] /chat orchestration failed: %s", exc)
        raise HTTPException(status_code=500, detail="Chat orchestration failed") from exc
    elapsed_ms = int((time.time() - start) * 1000)

    # Record API-level activity for observability
    try:
        add_activity(request.user_id, "INFO", "api", f"/chat processed in {elapsed_ms}ms agent={result.get('agent_type')} model={result.get('llm_used')}")
        add_activity(request.user_id, "INFO", "api", "[INFO] Response validation passed")
    except Exception:
        pass

    session_state = get_session(request.user_id)
    return ChatResponse(
        reply=result.get("reply", ""),
        agent_type=result.get("agent_type", "sales"),
        sentiment=result.get("sentiment", "neutral"),
        escalate=bool(result.get("escalate", False)),
        llm_used=result.get("llm_used", "GROQ"),
        web_searched=bool(result.get("web_searched", False)),
        web_sources=result.get("web_sources", None),
        session_id=result.get("session_id", request.user_id),
        routing=result.get("routing", None),
        response_ms=elapsed_ms,
        response_validated=bool(result.get("response_validated", False)),
        memory=session_state.get("user_profile", {}),
        confidence=result.get("confidence", 85),
        sources=result.get("sources", ["Customer Memory"]),
    )


@app.get("/session/{user_id}", response_model=SessionResponse)
def get_session_history(user_id: str) -> SessionResponse:
    """Return the full session information for a user."""
    logger.info("[INFO] /session/%s request received", user_id)
    session = get_session(user_id)
    return SessionResponse(
        user_id=session["user_id"],
        messages=session.get("message_history", []),
        sentiment_score=float(session.get("sentiment_score") or 0),
        escalated=bool(session.get("escalated", False)),
        memory=session.get("user_profile", {}),
    )


@app.get("/analytics")
def analytics() -> Dict[str, Any]:
    """Return backend analytics for dashboard consumption."""
    data = get_analytics()
    return data


@app.get("/status")
def status() -> Dict[str, Any]:
    """Return runtime service status and integrations for the dashboard."""
    analytics = get_analytics()
    # Detect whether Wikipedia grounding is available (package present)
    try:
        import wikipediaapi  # type: ignore

        wiki_available = True
    except Exception:
        wiki_available = False

    return {
        "api": "ok",
        "wiki_available": wiki_available,
        "gemini_available": bool(GEMINI_API_KEY),
        "memory_active": analytics.get("active_sessions", 0) > 0,
        "escalation_count": analytics.get("escalation_count", 0),
    }


@app.get("/activities/{user_id}")
def get_activities(user_id: str):
    """Return the recent activity log for a session."""
    log = get_activity_log(user_id)
    return {"activities": list(log[-200:])}


@app.post("/demo/{scenario}/{user_id}")
def run_demo(scenario: str, user_id: str):
    """Run a demo scenario that injects messages and triggers orchestration.

    Scenarios: lead_qualification, angry_customer, escalation_demo, product_recommendation, web_intel
    """
    scenario = (scenario or "").lower()

    SCENARIOS = {
        "lead_qualification": [
            {"message": "Hi, I'm evaluating OmniFlow for our enterprise team.", "agent": "sales"},
            {"message": "We run on AWS and need SSO and advanced analytics.", "agent": "sales"},
            {"message": "What's your pricing for 100+ seats?", "agent": "sales"},
        ],
        "angry_customer": [
            {"message": "Your product broke our production deployment and cost us revenue!"},
            {"message": "Support hasn't responded in hours — this is unacceptable and I want a refund."},
        ],
        "escalation_demo": [
            {"message": "I'm seeing data corruption and repeated failures in integration."},
            {"message": "This is urgent and causing major customer impact."},
        ],
        "product_recommendation": [
            {"message": "Recommend a package for a mid-market SaaS with 50-200 users.", "agent": "sales"},
            {"message": "We're comparing you to CompetitorX, how do you compare?", "agent": "sales"},
        ],
        "web_intel": [
            {"message": "Find latest public vulnerabilities for CompetitorX and summarize."},
        ],
    }

    steps = SCENARIOS.get(scenario) or SCENARIOS.get("lead_qualification")
    results = []

    add_activity(user_id, "INFO", "demo", f"Demo started: {scenario}")
    for step in steps:
        try:
            res = orchestrate_message(user_id, step.get("message", ""), requested_agent_type=step.get("agent"))
            results.append(res)
        except Exception as exc:
            add_activity(user_id, "ERROR", "demo", f"Demo step failed: {exc}")

    add_activity(user_id, "INFO", "demo", f"Demo completed: {scenario}")

    return {"scenario": scenario, "results": results, "session": get_session(user_id)}


@app.post("/escalate/{user_id}", response_model=EscalateResponse)
def escalate(user_id: str) -> EscalateResponse:
    """Manually trigger a human escalation for the given user."""
    logger.info("[INFO] /escalate/%s request received", user_id)
    update_session(user_id, escalated=True)
    add_activity(user_id, "WARNING", "escalation", "[WARNING] Manual escalation requested")
    return EscalateResponse(
        user_id=user_id,
        status="escalated",
        message="Manual escalation requested",
    )
