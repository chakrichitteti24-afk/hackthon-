import os
import json
from typing import List, Dict, Any

from .retriever import retrieve as faiss_retrieve
from .wikidata_loader import search_wikidata
from .memory_store import get_customer_memory
from .compressor import compress_context


def detect_intent(query: str) -> str:
    q = (query or "").lower()
    recommend_keywords = ["recommend", "compare", "best", "which", "suggest", "advise", "why", "explain", "analyze", "trend"]
    if any(w in q for w in recommend_keywords):
        return "recommend"
    return "ask"


def model_route(query: str) -> str:
    # simple routing rules per requirements
    short = len((query or "").split()) <= 10
    if not short:
        return "gemini"
    return "groq"


def _load_product_knowledge() -> List[Dict[str, Any]]:
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    candidates = []
    knowledge_dir = os.path.join(root, "artifacts", "knowledge")
    if not os.path.exists(knowledge_dir):
        return []
    for fn in os.listdir(knowledge_dir):
        if fn.endswith(".json"):
            path = os.path.join(knowledge_dir, fn)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    docs = json.load(f)
                    if isinstance(docs, list):
                        candidates.extend(docs)
            except Exception:
                continue
    return candidates


_PRODUCT_KB = None


def _ensure_product_kb():
    global _PRODUCT_KB
    if _PRODUCT_KB is None:
        _PRODUCT_KB = _load_product_knowledge()
    return _PRODUCT_KB


def find_products(query: str, k: int = 3) -> List[Dict[str, Any]]:
    kb = _ensure_product_kb() or []
    q = (query or "").lower()
    matches = []
    for p in kb:
        txt = json.dumps(p).lower()
        if any(tok in txt for tok in q.split() if len(tok) > 2):
            matches.append(p)
    # fallback: return first k
    if not matches:
        return kb[:k]
    return matches[:k]


def build_context(user_id: str, query: str, k: int = 3) -> Dict[str, Any]:
    """Assemble the multi-source context used to construct an LLM prompt."""
    intent = detect_intent(query)
    routing = model_route(query)

    memory = get_customer_memory(user_id)
    products = find_products(query, k=k)

    # Wikidata lookup for the query and for product names
    wikidata_results = []
    try:
        wikidata_results = search_wikidata(query, limit=3)
        for p in products[:2]:
            name = p.get("name") or p.get("title")
            if name:
                wikidata_results.extend(search_wikidata(name, limit=2))
    except Exception:
        wikidata_results = wikidata_results or []

    faiss_results = []
    try:
        faiss_results = faiss_retrieve(query, k=k)
    except Exception:
        faiss_results = []

    product_context = json.dumps(products, ensure_ascii=False, indent=2)
    memory_context = json.dumps(memory, ensure_ascii=False, indent=2)
    wikidata_context = json.dumps(wikidata_results, ensure_ascii=False, indent=2)
    faiss_context = json.dumps(faiss_results, ensure_ascii=False, indent=2)

    merged = f"\n\nMEMORY:\n{memory_context}\n\nPRODUCTS:\n{product_context}\n\nKNOWLEDGE:\n{wikidata_context}\n\nFAISS:\n{faiss_context}\n"

    compressed = compress_context(merged, max_chars=3000)

    system_prompt = f"""
Current Year: 2026

You are OmniFlow AI.

You are a professional sales executive.

Use retrieved context as primary source.

Never hallucinate products.

If confidence is low, ask follow-up questions.

CONTEXT:

{compressed}

"""

    return {
        "intent": intent,
        "route": routing,
        "context": compressed,
        "system_prompt": system_prompt,
        "components": {
            "memory": memory,
            "products": products,
            "wikidata": wikidata_results,
            "faiss": faiss_results,
        },
    }


def example_run():
    # Demonstration harness that doesn't call external LLMs.
    res = build_context("demo_user", "Recommend a gaming laptop under 150000", k=3)
    print("--- SYSTEM PROMPT ---")
    print(res["system_prompt"])
    print("--- SOURCES ---")
    for k, v in res["components"].items():
        print(f"{k}: {len(v) if isinstance(v, list) else '1'} items")


if __name__ == "__main__":
    example_run()
