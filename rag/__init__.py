"""RAG helpers for OmniFlow AI

This package provides lightweight FAISS-backed retrieval, embeddings,
Wikidata lookup helpers, and simple memory/context utilities used by the
OmniFlow pipeline. Files are intentionally small and dependency-light so
they can be extended or replaced safely.
"""

from . import embeddings, vector_store, retriever, wikidata_loader, memory_store, compressor, pipeline

__all__ = [
    "embeddings",
    "vector_store",
    "retriever",
    "wikidata_loader",
    "memory_store",
    "compressor",
    "pipeline",
]
"""OmniFlow RAG helpers package.

Expose small utilities for Wikipedia loading, embeddings, FAISS storage,
retrieval and simple context compression used by the RAG pipeline.
"""
from .wikipedia_loader import search_and_load, chunk_text, clean_text
from .embeddings import EmbeddingModel
from .vector_store import FaissVectorStore, VectorStoreManager
from .retriever import Retriever
from .context_compressor import compress_context, build_system_prompt

__all__ = [
    "search_and_load",
    "chunk_text",
    "clean_text",
    "EmbeddingModel",
    "FaissVectorStore",
    "VectorStoreManager",
    "Retriever",
    "compress_context",
    "build_system_prompt",
]
