"""Product knowledge base loader and indexer.

Loads JSON product knowledge files from the `knowledge/` directory and
indexes them into the retriever's `product` FAISS store for semantic search.
"""
from typing import List, Dict, Optional
import os
import json


def _knowledge_dir() -> str:
    # knowledge directory is a sibling of the rag package
    here = os.path.dirname(__file__)
    return os.path.normpath(os.path.join(here, "..", "knowledge"))


def load_knowledge(knowledge_dir: Optional[str] = None) -> List[Dict]:
    """Read all .json files in the knowledge directory and return a list of items."""
    if knowledge_dir is None:
        knowledge_dir = _knowledge_dir()
    items: List[Dict] = []
    if not os.path.isdir(knowledge_dir):
        return items
    for fn in os.listdir(knowledge_dir):
        if not fn.lower().endswith(".json"):
            continue
        # Skip non-product datasets (brands, trends, processors, gpu catalogs)
        if any(x in fn.lower() for x in ("brand", "trend", "processor", "market", "gpu")):
            continue
        path = os.path.join(knowledge_dir, fn)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if isinstance(data, list):
                    items.extend(data)
        except Exception:
            continue
    return items


def index_knowledge(retriever, knowledge_dir: Optional[str] = None) -> int:
    """Index product knowledge into the retriever as a `product` store.

    Returns the number of indexed items.
    """
    items = load_knowledge(knowledge_dir)
    if not items:
        return 0

    # Ensure product store exists
    if "product" not in retriever.manager.stores:
        from .vector_store import FaissVectorStore

        dim = int(retriever.embedding_model.dim)
        retriever.manager.add_store("product", FaissVectorStore(dim))

    store = retriever.manager.stores["product"]

    texts: List[str] = []
    metadatas: List[Dict] = []
    for p in items:
        # Build a short searchable text from common fields
        name = p.get("name") or f"{p.get('brand', '')} {p.get('model', '')}".strip()
        category = p.get("category", "")
        desc_parts = []
        for k in ("gpu", "price", "description", "specs", "recommended_for", "features", "details", "focus"):
            if k in p:
                val = p.get(k)
                if isinstance(val, list):
                    desc_parts.append(", ".join(val))
                else:
                    desc_parts.append(str(val))
        text = " | ".join([name, category] + [" ".join(desc_parts)])
        texts.append(text)
        metadatas.append({"source": "product", "name": name, "category": category})

    # Embed and index (use retriever's embedding model)
    vectors = retriever.embedding_model.embed_texts(texts)
    ids = store.add(texts, vectors, metadatas=metadatas)
    return len(ids)


def retrieve_products(retriever, query: str, k: int = 3) -> List[Dict]:
    """Retrieve top-k product matches from the product store (if present).

    Returns a list of result dicts or an empty list on failure.
    """
    if "product" not in retriever.manager.stores:
        return []
    try:
        qv = retriever.embedding_model.embed_query(query)
        return retriever.manager.stores["product"].search(qv, top_k=k)
    except Exception:
        return []


__all__ = ["load_knowledge", "index_knowledge", "retrieve_products"]
