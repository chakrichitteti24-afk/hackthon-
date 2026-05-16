"""Entry point for the OmniFlow AI FastAPI backend."""

from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agents import insight_agent, sales_agent, support_agent
from memory.session_store import get_session, update_session
from models.schemas import ChatRequest, ChatResponse, EscalateResponse, SessionResponse


app = FastAPI(title="OmniFlow AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> Dict[str, str]:
    """Simple health-check endpoint."""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Main chat endpoint."""
    if request.agent_type not in {"sales", "support", "insight"}:
        raise HTTPException(status_code=400, detail="Invalid agent_type")

    session = get_session(request.user_id)
    update_session(request.user_id, agent_type=request.agent_type)

    user_msg = {"role": "user", "content": request.message}
    session["message_history"].append(user_msg)

    try:
        if request.agent_type == "sales":
            reply = sales_agent.get_reply(session["message_history"])
            sentiment = "neutral"
        elif request.agent_type == "support":
            reply = support_agent.get_reply(session["message_history"])
            sentiment = "neutral"
        else:
            sentiment_result = insight_agent.get_sentiment(session["message_history"])
            sentiment = str(sentiment_result.get("sentiment", "neutral"))
            score = float(sentiment_result.get("score", 0))
            reply = f"Sentiment analysis result: {sentiment} (score {score:g})"

            update_session(request.user_id, sentiment_score=score)
            if sentiment_result.get("escalate"):
                update_session(request.user_id, escalated=True)
    except Exception as exc:
        reply = (
            "The backend is connected, but the AI provider call failed. "
            "Check GROQ_API_KEY and network access, then try again."
        )
        sentiment = "neutral"
        update_session(request.user_id, provider_error=str(exc))

    session["message_history"].append({"role": "assistant", "content": reply})

    session = get_session(request.user_id)
    escalated = bool(session.get("escalated", False))

    return ChatResponse(
        reply=reply,
        sentiment=sentiment,
        agent_type=request.agent_type,
        escalate=escalated,
        session_id=request.user_id,
    )


@app.get("/session/{user_id}", response_model=SessionResponse)
def get_session_history(user_id: str) -> SessionResponse:
    """Return the full session information for a user."""
    session = get_session(user_id)
    return SessionResponse(
        user_id=session["user_id"],
        messages=session.get("message_history", []),
        sentiment_score=float(session.get("sentiment_score") or 0),
        escalated=bool(session.get("escalated", False)),
    )


@app.post("/escalate/{user_id}", response_model=EscalateResponse)
def escalate(user_id: str) -> EscalateResponse:
    """Manually trigger a human escalation for the given user."""
    update_session(user_id, escalated=True)
    return EscalateResponse(
        user_id=user_id,
        status="escalated",
        message="Manual escalation requested",
    )
