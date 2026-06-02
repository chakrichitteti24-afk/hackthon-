"""GPU knowledge loader and FAISS indexer.

Loads `knowledge/gpus.json` and indexes entries into a dedicated
`gpu` FAISS store for semantic retrieval.
"""
from typing import List, Dict, Optional
import os
import json


def _knowledge_dir() -> str:
    here = os.path.dirname(__file__)
    return os.path.normpath(os.path.join(here, "..", "knowledge"))


def load_gpus(knowledge_dir: Optional[str] = None) -> List[Dict]:
    if knowledge_dir is None:
        knowledge_dir = _knowledge_dir()
    items: List[Dict] = []
    path = os.path.join(knowledge_dir, "gpus.json")
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


def index_gpus(retriever, knowledge_dir: Optional[str] = None) -> int:
    items = load_gpus(knowledge_dir)
    if not items:
        return 0

    from .vector_store import FaissVectorStore

    dim = int(retriever.embedding_model.dim)
    if "gpu" not in retriever.manager.stores:
        retriever.manager.add_store("gpu", FaissVectorStore(dim))

    store = retriever.manager.stores["gpu"]

    texts: List[str] = []
    metadatas: List[Dict] = []
    for g in items:
        name = g.get("name") or g.get("type") or ""
        family = g.get("family", "")
        usage = ", ".join(g.get("recommended_usage", []) or g.get("recommended_for", []))
        text = " | ".join([name, family, usage])
        texts.append(text)
        metadatas.append({"source": "gpu", "name": name})

    vecs = retriever.embedding_model.embed_texts(texts)
    ids = store.add(texts, vecs, metadatas=metadatas)
    return len(ids)


def retrieve_gpus(retriever, query: str, k: int = 3) -> List[Dict]:
    if "gpu" not in retriever.manager.stores:
        return []
    try:
        qv = retriever.embedding_model.embed_query(query)
        return retriever.manager.stores["gpu"].search(qv, top_k=k)
    except Exception:
        return []


__all__ = ["load_gpus", "index_gpus", "retrieve_gpus"]
