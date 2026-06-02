"""Brand knowledge loader and FAISS indexer.

Loads `knowledge/brands.json` and indexes brand entries into a dedicated
`brand` FAISS store for semantic retrieval.
"""
from typing import List, Dict, Optional
import os
import json


def _knowledge_dir() -> str:
    here = os.path.dirname(__file__)
    return os.path.normpath(os.path.join(here, "..", "knowledge"))


def load_brands(knowledge_dir: Optional[str] = None) -> List[Dict]:
    if knowledge_dir is None:
        knowledge_dir = _knowledge_dir()
    items: List[Dict] = []
    path = os.path.join(knowledge_dir, "brands.json")
    if not os.path.exists(path):
        return items
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            if isinstance(data, list):
                items.extend(data)
    except Exception:
        pass
    return items


def index_brands(retriever, knowledge_dir: Optional[str] = None) -> int:
    """Index brand entries into the retriever as a `brand` store.

    Returns the number of indexed brand items.
    """
    items = load_brands(knowledge_dir)
    if not items:
        return 0

    # Ensure brand store exists
    from .vector_store import FaissVectorStore

    dim = int(retriever.embedding_model.dim)
    if "brand" not in retriever.manager.stores:
        retriever.manager.add_store("brand", FaissVectorStore(dim))

    store = retriever.manager.stores["brand"]

    texts: List[str] = []
    metadatas: List[Dict] = []
    for b in items:
        name = b.get("name", "")
        pos = b.get("positioning", "")
        series = ", ".join(b.get("popular_series", []))
        text = f"{name} | {pos} | {series}"
        texts.append(text)
        metadatas.append({"source": "brand", "name": name})

    vectors = retriever.embedding_model.embed_texts(texts)
    ids = store.add(texts, vectors, metadatas=metadatas)
    return len(ids)


def retrieve_brands(retriever, query: str, k: int = 3) -> List[Dict]:
    if "brand" not in retriever.manager.stores:
        return []
    try:
        qv = retriever.embedding_model.embed_query(query)
        return retriever.manager.stores["brand"].search(qv, top_k=k)
    except Exception:
        return []


__all__ = ["load_brands", "index_brands", "retrieve_brands"]
