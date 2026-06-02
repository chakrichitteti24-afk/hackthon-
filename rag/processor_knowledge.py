"""Processor knowledge loader and FAISS indexer.

Loads `knowledge/processors.json` and indexes entries into a dedicated
`processor` FAISS store for semantic retrieval.
"""
from typing import List, Dict, Optional
import os
import json


def _knowledge_dir() -> str:
    here = os.path.dirname(__file__)
    return os.path.normpath(os.path.join(here, "..", "knowledge"))


def load_processors(knowledge_dir: Optional[str] = None) -> List[Dict]:
    if knowledge_dir is None:
        knowledge_dir = _knowledge_dir()
    items: List[Dict] = []
    path = os.path.join(knowledge_dir, "processors.json")
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


def index_processors(retriever, knowledge_dir: Optional[str] = None) -> int:
    items = load_processors(knowledge_dir)
    if not items:
        return 0

    from .vector_store import FaissVectorStore

    dim = int(retriever.embedding_model.dim)
    if "processor" not in retriever.manager.stores:
        retriever.manager.add_store("processor", FaissVectorStore(dim))

    store = retriever.manager.stores["processor"]

    texts: List[str] = []
    metadatas: List[Dict] = []
    for p in items:
        # Build a short searchable text from common fields
        name = p.get("type") or p.get("name") or ""
        strengths = ", ".join(p.get("strengths", []))
        usage = ", ".join(p.get("recommended_usage", []) or p.get("recommended_for", []))
        text = " | ".join([name, strengths, usage])
        texts.append(text)
        metadatas.append({"source": "processor", "name": name})

    vecs = retriever.embedding_model.embed_texts(texts)
    ids = store.add(texts, vecs, metadatas=metadatas)
    return len(ids)


def retrieve_processors(retriever, query: str, k: int = 3) -> List[Dict]:
    if "processor" not in retriever.manager.stores:
        return []
    try:
        qv = retriever.embedding_model.embed_query(query)
        return retriever.manager.stores["processor"].search(qv, top_k=k)
    except Exception:
        return []


__all__ = ["load_processors", "index_processors", "retrieve_processors"]
