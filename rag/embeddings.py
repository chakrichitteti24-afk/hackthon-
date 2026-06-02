from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Union, List

_MODEL: "SentenceTransformer|None" = None


def _get_model() -> SentenceTransformer:
    global _MODEL
    if _MODEL is None:
        # lightweight, fast model suitable for RAG in demos
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _MODEL


def embed(texts: Union[str, List[str]]):
    """Return float32 embeddings for a single string or list of strings.

    Args:
        texts: input text or list of texts

    Returns:
        numpy.ndarray shape (n, dim) dtype float32
    """
    model = _get_model()
    single = isinstance(texts, str)
    if single:
        texts = [texts]
    emb = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    emb = np.asarray(emb, dtype="float32")
    return emb[0] if single else emb
"""Embedding utilities using SentenceTransformers.

Provides a small wrapper around `sentence_transformers.SentenceTransformer`.
"""
from typing import Iterable, List


class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        try:
            from sentence_transformers import SentenceTransformer
        except Exception as e:
            raise RuntimeError("Please install sentence-transformers (pip install sentence-transformers)") from e

        self.model = SentenceTransformer(model_name)
        # SentenceTransformer provides a helper to get the embedding dimension
        try:
            self.dim = self.model.get_embedding_dimension()
        except Exception:
            # fallback to first embedding size after an encode
            self.dim = None

    def embed_texts(self, texts: Iterable[str], batch_size: int = 32, normalize: bool = True):
        """Encode a list of texts into numpy vectors.

        Returns a NumPy array of shape (n, dim).
        """
        import numpy as np

        vectors = self.model.encode(list(texts), batch_size=batch_size, show_progress_bar=False, convert_to_numpy=True)
        if normalize:
            # safe normalize
            norms = (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-12)
            vectors = vectors / norms
        return vectors

    def embed_query(self, text: str):
        return self.embed_texts([text])[0]
