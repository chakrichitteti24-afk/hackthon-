from .embeddings import embed
from .vector_store import store
import numpy as np
from typing import List, Dict


def retrieve(query: str, k: int = 3) -> List[Dict]:
    """Retrieve top-k documents from the FAISS store for *query*."""
    emb = embed(query)
    if isinstance(emb, np.ndarray) and emb.ndim == 1:
        q = emb
    else:
        q = emb[0]
    results = store.search(q, k)
    return results
"""Retriever glue: index Wikipedia, session memory and run semantic retrieval."""
from typing import List, Dict, Optional

from .embeddings import EmbeddingModel
from .vector_store import FaissVectorStore, VectorStoreManager
from .wikipedia_loader import chunk_text


class Retriever:
    def __init__(self, embedding_model: EmbeddingModel):
        self.embedding_model = embedding_model
        # ensure we know the embedding dimension
        if getattr(self.embedding_model, "dim", None) is None:
            # lazy probe
            v = self.embedding_model.embed_texts(["probe"])  # type: ignore
            self.embedding_model.dim = v.shape[1]

        self.manager = VectorStoreManager()
        # create default stores
        dim = int(self.embedding_model.dim)
        self.manager.add_store("wiki", FaissVectorStore(dim))
        self.manager.add_store("memory", FaissVectorStore(dim))
        self.manager.add_store("conversation", FaissVectorStore(dim))

    def index_wikipedia(self, wiki_pages: List[Dict[str, str]]):
        """Index a list of Wikipedia page dicts from `search_and_load`.

        Each page should contain `title`, `url`, `text`.
        """
        texts = []
        metadatas = []
        for p in wiki_pages:
            title = p.get("title")
            url = p.get("url")
            text = p.get("text") or ""
            chunks = chunk_text(text)
            for i, c in enumerate(chunks):
                texts.append(c)
                metadatas.append({"source": "wiki", "title": title, "url": url, "chunk_index": i})

        if texts:
            vectors = self.embedding_model.embed_texts(texts)
            self.manager.stores["wiki"].add(texts, vectors, metadatas=metadatas)

    def index_user_memory(self, user_id: str, session_store_module) -> None:
        """Index the user's session timeline into the `memory` store.

        `session_store_module` should expose `get_timeline(user_id)` which
        returns a list of message dicts.
        """
        timeline = session_store_module.get_timeline(user_id)
        texts = []
        metadatas = []
        for msg in timeline:
            role = msg.get("role")
            content = msg.get("content", "")
            ts = msg.get("timestamp")
            # keep small label with role/timestamp for provenance
            for i, chunk in enumerate(chunk_text(content)):
                texts.append(chunk)
                metadatas.append({"source": "session", "user_id": user_id, "role": role, "timestamp": ts, "chunk_index": i})

        if texts:
            vectors = self.embedding_model.embed_texts(texts)
            self.manager.stores["memory"].add(texts, vectors, metadatas=metadatas)

    def index_conversation(self, conversation_texts: List[str], metadatas: Optional[List[Dict]] = None) -> None:
        """Index arbitrary conversation-like texts into the `conversation` store."""
        if not conversation_texts:
            return
        vectors = self.embedding_model.embed_texts(conversation_texts)
        self.manager.stores["conversation"].add(conversation_texts, vectors, metadatas=metadatas)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """Run a combined retrieval over all stores and return top-k chunks."""
        qv = self.embedding_model.embed_query(query)
        results = self.manager.search_combined(qv, top_k=top_k)
        return results
