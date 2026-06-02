import faiss
import numpy as np
import json
import os
from typing import List, Dict, Optional

DIMENSION = 384
INDEX_FILE = os.path.join(os.path.dirname(__file__), "index.faiss")
DOCS_FILE = os.path.join(os.path.dirname(__file__), "documents.json")


class VectorStore:
    def __init__(self, dimension: int = DIMENSION):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents: List[Dict] = []
        self._next_id = 0

        # Try to load persisted index and documents (best-effort)
        try:
            if os.path.exists(DOCS_FILE) and os.path.exists(INDEX_FILE):
                with open(DOCS_FILE, "r", encoding="utf-8") as f:
                    self.documents = json.load(f)
                    if self.documents:
                        self._next_id = max(d.get("id", 0) for d in self.documents) + 1
                self.index = faiss.read_index(INDEX_FILE)
        except Exception:
            # Fall back to empty index on any error
            self.index = faiss.IndexFlatL2(self.dimension)

    def add_documents(self, texts: List[str], embeddings: np.ndarray, metas: Optional[List[Dict]] = None) -> None:
        if metas is None:
            metas = [{} for _ in texts]
        embeddings = np.asarray(embeddings, dtype="float32")
        if embeddings.ndim == 1:
            embeddings = np.expand_dims(embeddings, axis=0)
        if embeddings.shape[1] != self.dimension:
            raise ValueError("Embedding dimension mismatch")

        self.index.add(embeddings)
        for i, text in enumerate(texts):
            doc = {"id": self._next_id, "text": text, "meta": metas[i]}
            self.documents.append(doc)
            self._next_id += 1
        self._persist()

    def search(self, query_embedding: np.ndarray, k: int = 3) -> List[Dict]:
        q = np.asarray(query_embedding, dtype="float32")
        if q.ndim == 1:
            q = np.expand_dims(q, axis=0)
        distances, indices = self.index.search(q, k)
        results: List[Dict] = []
        for idx in indices[0]:
            if idx >= 0 and idx < len(self.documents):
                results.append(self.documents[idx])
        return results

    def _persist(self) -> None:
        try:
            faiss.write_index(self.index, INDEX_FILE)
            with open(DOCS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.documents, f, ensure_ascii=False, indent=2)
        except Exception:
            # Persistence is best-effort; don't fail the pipeline
            pass


# Module-level default store for quick usage
store = VectorStore()
"""FAISS-backed vector store for storing embeddings and metadata.

This module provides a small, testable in-memory manager that keeps a FAISS
index and a Python dict for metadata and original text. It supports add/search
and optional persist/load of the index and metadata.
"""
from typing import Any, Dict, Iterable, List, Optional
import os


class FaissVectorStore:
    def __init__(self, embedding_dim: int):
        try:
            import faiss
        except Exception as e:
            raise RuntimeError("Please install faiss-cpu (pip install faiss-cpu)") from e

        self._faiss = __import__("faiss")
        self.dim = int(embedding_dim)
        # Use inner-product on normalized vectors to approximate cosine similarity
        index = self._faiss.IndexFlatIP(self.dim)
        self.index = self._faiss.IndexIDMap(index)

        # id counters and stores
        self._next_id = 1
        self._texts: Dict[int, str] = {}
        self._metadatas: Dict[int, Dict[str, Any]] = {}

    def _alloc_ids(self, n: int) -> List[int]:
        ids = list(range(self._next_id, self._next_id + n))
        self._next_id += n
        return ids

    def add(self, texts: Iterable[str], vectors, metadatas: Optional[Iterable[Dict[str, Any]]] = None, ids: Optional[Iterable[int]] = None):
        """Add documents to the FAISS index.

        `vectors` must be a NumPy array shaped (n, dim) or convertible to it.
        Optional `metadatas` is an iterable providing metadata per document.
        """
        import numpy as np

        arr = np.array(vectors, dtype="float32")
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)

        n = arr.shape[0]
        if arr.shape[1] != self.dim:
            raise ValueError(f"Vectors must have dimension {self.dim}, got {arr.shape[1]}")

        # normalize for cosine (IndexFlatIP expects normalized vectors for cosine similarity)
        try:
            self._faiss.normalize_L2(arr)
        except Exception:
            # fall back to manual normalize
            norms = (np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12)
            arr = arr / norms

        if ids is None:
            ids = self._alloc_ids(n)
        else:
            ids = list(map(int, ids))

        # add to faiss index
        self.index.add_with_ids(arr, np.array(ids, dtype="int64"))

        # store texts and metadata
        for i, idv in enumerate(ids):
            self._texts[int(idv)] = list(texts)[i]
            if metadatas:
                self._metadatas[int(idv)] = list(metadatas)[i]
            else:
                self._metadatas[int(idv)] = {}

        return ids

    def search(self, query_vector, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search the index for nearest neighbors to `query_vector`.

        Returns a list of dicts with keys: `id`, `score`, `text`, `metadata`.
        """
        import numpy as np

        q = np.array(query_vector, dtype="float32")
        if q.ndim == 1:
            q = q.reshape(1, -1)

        try:
            self._faiss.normalize_L2(q)
        except Exception:
            norms = (np.linalg.norm(q, axis=1, keepdims=True) + 1e-12)
            q = q / norms

        D, I = self.index.search(q, top_k)
        results: List[Dict[str, Any]] = []
        for score, idx in zip(D[0].tolist(), I[0].tolist()):
            if idx == -1:
                continue
            results.append({
                "id": int(idx),
                "score": float(score),
                "text": self._texts.get(int(idx), ""),
                "metadata": self._metadatas.get(int(idx), {}),
            })

        return results

    def save(self, path: str) -> None:
        """Persist faiss index and metadata to `path` directory."""
        os.makedirs(path, exist_ok=True)
        # save index
        index_path = os.path.join(path, "index.faiss")
        self._faiss.write_index(self.index, index_path)
        # save metadata and texts
        import json

        meta_path = os.path.join(path, "metadatas.json")
        with open(meta_path, "w", encoding="utf-8") as fh:
            json.dump({"texts": self._texts, "metadatas": self._metadatas, "next_id": self._next_id}, fh)

    @classmethod
    def load(cls, path: str):
        """Load a FaissVectorStore previously saved with `save`.

        Returns a store instance or raises on error.
        """
        try:
            import faiss
        except Exception as e:
            raise RuntimeError("Please install faiss-cpu (pip install faiss-cpu)") from e

        index_path = os.path.join(path, "index.faiss")
        meta_path = os.path.join(path, "metadatas.json")
        if not os.path.exists(index_path) or not os.path.exists(meta_path):
            raise FileNotFoundError("Index or metadata not found in path")

        index = faiss.read_index(index_path)
        # wrap in IDMap if needed
        if not isinstance(index, faiss.IndexIDMap):
            idx = faiss.IndexIDMap(index)
        else:
            idx = index

        import json
        with open(meta_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        store = cls(embedding_dim=idx.index.d)
        store.index = idx
        store._texts = {int(k): v for k, v in data.get("texts", {}).items()}
        store._metadatas = {int(k): v for k, v in data.get("metadatas", {}).items()}
        store._next_id = int(data.get("next_id", max(store._texts.keys(), default=0) + 1))
        return store


class VectorStoreManager:
    """Manage multiple named FaissVectorStore instances (wiki, memory, conversation).

    This keeps stores separate but provides a convenience search to merge
    results across the stores (ranking by score and returning top-k globally).
    """

    def __init__(self):
        self.stores: Dict[str, FaissVectorStore] = {}

    def add_store(self, name: str, store: FaissVectorStore):
        self.stores[name] = store

    def search_combined(self, query_vector, top_k: int = 3) -> List[Dict[str, Any]]:
        # gather results from each store (take a few from each to re-rank)
        all_results: List[Dict[str, Any]] = []
        for name, store in self.stores.items():
            res = store.search(query_vector, top_k=top_k)
            for r in res:
                r = dict(r)
                r["store"] = name
                all_results.append(r)

        # sort by score desc and return top_k
        all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return all_results[:top_k]
