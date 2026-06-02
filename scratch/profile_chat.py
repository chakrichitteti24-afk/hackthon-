import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from memory.session_store import get_session
from router.agent_router import route_agent
from orchestration.knowledge_pipeline import KnowledgePipeline
from agents import sales_agent, support_agent, insight_agent
from utils.validators import validate_response, SAFE_FALLBACK

kp_global = KnowledgePipeline()

def profile_run(run_id, message):
    user_id = f"profile_user_{run_id}"
    
    print(f"\n--- START PROFILING RUN {run_id} (msg: '{message}') ---")
    
    t0 = time.time()
    session = get_session(user_id)
    print(f"1. get_session took {(time.time() - t0)*1000:.2f}ms")
    
    t0 = time.time()
    route = route_agent(message, session.get("message_history", []))
    chosen_agent = route.get("agent", "sales")
    print(f"2. route_agent ({chosen_agent}) took {(time.time() - t0)*1000:.2f}ms")
    
    t0 = time.time()
    ctx = kp_global.build_context(user_id, message)
    print(f"3. build_context took {(time.time() - t0)*1000:.2f}ms")
    
    augmented_history = [{"role": "system", "content": "System prompt info"}] + list(session.get("message_history", []))
    
    # Decide model using smart message router
    from router.message_router import route_message
    model_routing = route_message(message)
    routed_model = model_routing.get("model", "gemini")
    print(f"   Routed to model: {routed_model} (reason: {model_routing.get('reason')})")
    
    t0 = time.time()
    if chosen_agent == "sales":
        res = sales_agent.get_reply(user_id, message, augmented_history, preferred_model=routed_model)
    elif chosen_agent == "support":
        res = support_agent.get_reply(user_id, message, augmented_history, preferred_model=routed_model)
    else:
        res = insight_agent.get_sentiment(user_id, message, augmented_history, preferred_model=routed_model)
    print(f"4. Agent ({chosen_agent}) call took {(time.time() - t0)*1000:.2f}ms")
    print(f"   LLM used: {res.get('llm_used')}")
    
    print(f"--- DONE PROFILING RUN {run_id} ---")

if __name__ == "__main__":
    profile_run(1, "I need help with billing and price increases and my subscription")
    profile_run(2, "I need help with billing and price increases and my subscription")
    profile_run(3, "hello")
