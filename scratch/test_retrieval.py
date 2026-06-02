import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from orchestration.knowledge_pipeline import KnowledgePipeline

print("Initializing KnowledgePipeline...")
kp = KnowledgePipeline()
kp.ensure_init()

queries = [
    "iPhone 17 Pro",
    "Samsung Galaxy S26 Ultra",
    "MacBook Pro 16 M4 Max price and specs",
    "ROG Zephyrus G16 (2026) GPU AMD Ryzen",
    "What are the AI trends in 2026?",
    "Tell me about the GPU trends in 2026",
    "What is the market trend for smartphones in 2026?"
]

print("\nRunning RAG Retrieval Tests:\n" + "="*50)
for q in queries:
    print(f"\nQUERY: '{q}'")
    context = kp.build_context(user_id="test_user_123", query=q, top_k=3)
    print(f"Sources: {context.get('sources')}")
    print(f"Confidence: {context.get('confidence')}%")
    print(f"Product Context: {repr(context.get('product_context'))}")
    print(f"Trend Context: {repr(context.get('trend_context'))}")
    print(f"Compressed Context (first 300 chars): {repr(context.get('compressed_context')[:300])}")
    print("-"*50)
