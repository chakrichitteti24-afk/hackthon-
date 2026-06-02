"""Tiny example showing RAG pipeline usage inside OmniFlow backend.

This file is intended as a usage example and integration snippet — it does
not run by itself in production. Use it as a reference for calling the RAG
components from request handlers or agents.
"""
from .embeddings import EmbeddingModel
from .retriever import Retriever
from .wikipedia_loader import search_and_load
from .context_compressor import compress_context, build_system_prompt


def run_rag_query(user_id: str, query: str, session_store_module, max_wiki_pages: int = 3):
    """Run the RAG flow for a single user query and return the system prompt + retrieved chunks.

    Steps executed:
    - load wiki pages for the query
    - index wiki pages (in-memory)
    - index user session memory
    - perform semantic retrieval (top 3 chunks)
    - compress context and build the system prompt
    """
    emb = EmbeddingModel()
    retriever = Retriever(emb)

    # 1) Wikipedia
    wiki_pages = search_and_load(query, max_pages=max_wiki_pages)
    retriever.index_wikipedia(wiki_pages)

    # 2) user memory (session store)
    retriever.index_user_memory(user_id, session_store_module)

    # 3) retrieve
    retrieved = retriever.retrieve(query, top_k=3)

    # 4) compress and build a small prompt
    wiki_context = compress_context([r for r in retrieved if r.get("store") == "wiki"]) or ""
    memory_context = compress_context([r for r in retrieved if r.get("store") == "memory"]) or ""
    prompt = build_system_prompt(memory_context, wiki_context)

    return {"prompt": prompt, "retrieved": retrieved}
