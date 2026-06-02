import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from orchestration.orchestrator import orchestrate_message
from dotenv import load_dotenv

load_dotenv()

# Force UTF-8 stdout encoding on Windows
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding='utf-8')

scenarios = [
    ("sales_user_1", "Recommend a premium phone releasing in 2026"),
    ("sales_user_2", "I am looking for a premium gaming and creator laptop with AMD CPU and an RTX 5080"),
    ("insight_user_1", "What are the key GPU trends in 2026?"),
    ("insight_user_2", "Summarize the market trends for smartphones in 2026")
]

print("Starting End-to-End Orchestration Queries...\n" + "="*80)
for uid, msg in scenarios:
    print(f"\nUSER: {msg} (User: {uid})")
    try:
        res = orchestrate_message(uid, msg)
        print(f"Routed Agent: {res.get('agent_type')}")
        print(f"LLM Used: {res.get('llm_used')}")
        print(f"Sentiment: {res.get('sentiment')} | Escalate: {res.get('escalate')}")
        print(f"Sources: {res.get('sources')}")
        print(f"Confidence: {res.get('confidence')}%")
        print(f"Reply:\n{res.get('reply')}")
    except Exception as exc:
        print(f"ERROR: {exc}")
    print("-" * 80)
