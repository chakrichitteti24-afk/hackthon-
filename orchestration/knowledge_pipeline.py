"""Knowledge pipeline to assemble context for RAG-enabled agents.

This module provides a `KnowledgePipeline` class that lazily initializes
an embedding model and retriever, indexes product knowledge, and exposes
`build_context` to return memory, product, wikidata and compressed RAG
context for a given user query.
"""
from typing import Dict, Any, List
import logging

from rag.embeddings import EmbeddingModel
from rag.retriever import Retriever
from rag.product_knowledge import index_knowledge, retrieve_products
from rag.brand_knowledge import index_brands, retrieve_brands
from rag.wikidata_loader import search_wikidata
from rag.processor_knowledge import index_processors
from rag.gpu_knowledge import index_gpus
from rag.memory_store import get_compact_memory
from rag.context_compressor import compress_context
from search.wiki_search import should_use_wikipedia
from search.wiki_search import search_wikipedia
import os
import json


class KnowledgePipeline:
    def __init__(self):
        self.embedding_model = None
        self.retriever = None
        self._indexed = False

    def ensure_init(self):
        if self.embedding_model is None:
            try:
                self.embedding_model = EmbeddingModel()
                self.retriever = Retriever(self.embedding_model)
                # index product knowledge (best-effort)
                try:
                    count = index_knowledge(self.retriever)
                    self._indexed = count > 0
                    logging.info("KnowledgePipeline: indexed %d product items", count)
                except Exception as exc:
                    logging.debug("KnowledgePipeline: product indexing failed: %s", exc)
                # index trend intelligence into a dedicated 'trend' store
                try:
                    trend_count = 0
                    trend_items = self._load_trends()
                    if trend_items:
                        # ensure trend store exists
                        from rag.vector_store import FaissVectorStore

                        dim = int(self.embedding_model.dim)
                        if "trend" not in self.retriever.manager.stores:
                            self.retriever.manager.add_store("trend", FaissVectorStore(dim))
                        # prepare texts and metadatas
                        texts = [json.dumps(t, ensure_ascii=False) for t in trend_items]
                        metas = [{"source": "trend", "trend": t.get("trend") or ""} for t in trend_items]
                        vecs = self.embedding_model.embed_texts(texts)
                        self.retriever.manager.stores["trend"].add(texts, vecs, metadatas=metas)
                        trend_count = len(texts)
                    logging.info("KnowledgePipeline: indexed %d trend items", trend_count)
                except Exception as exc:
                    logging.debug("KnowledgePipeline: trend indexing failed: %s", exc)
                # index brand database
                try:
                    brand_count = index_brands(self.retriever)
                    logging.info("KnowledgePipeline: indexed %d brand items", brand_count)
                except Exception as exc:
                    logging.debug("KnowledgePipeline: brand indexing failed: %s", exc)
                # index processor database
                try:
                    proc_count = index_processors(self.retriever)
                    logging.info("KnowledgePipeline: indexed %d processor items", proc_count)
                except Exception as exc:
                    logging.debug("KnowledgePipeline: processor indexing failed: %s", exc)

                # index GPU database
                try:
                    gpu_count = index_gpus(self.retriever)
                    logging.info("KnowledgePipeline: indexed %d GPU items", gpu_count)
                except Exception as exc:
                    logging.debug("KnowledgePipeline: GPU indexing failed: %s", exc)
            except Exception as exc:
                logging.exception("KnowledgePipeline initialization failed: %s", exc)

    def build_context(self, user_id: str, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Build and return contextual pieces for the given user and query.

        Implements the Hybrid Knowledge Engine retrieval ordering:
        - Product queries: Product KB -> Customer Memory -> Trend Intelligence -> FAISS
        - Technology queries: Wikipedia -> Wikidata -> FAISS

        Returns a dict containing memory_context, product_context, wiki_context,
        faiss_results, compressed_context, confidence (0-100), and sources list.
        """
        self.ensure_init()
        sources: List[str] = []
        confidence = 0

        # Helper: load trend intelligence files (cached)
        product_context = ""
        memory_context = ""
        wiki_context = ""
        faiss_results = []
        brand_context = ""
        trend_context = ""

        # Determine query type heuristically
        q = (query or "").lower()
        product_keywords = ["laptop", "phone", "smartphone", "appliance", "tv", "recommend", "price", "spec", "model", "buy", "availability"]
        tech_keywords = ["technology", "cpu", "gpu", "benchmark", "ai", "architecture", "performance", "inference"]

        is_product = any(k in q for k in product_keywords)
        is_tech = any(k in q for k in tech_keywords)

        # PRODUCT FLOW
        if is_product and not is_tech:
            # 1) Product Knowledge
            try:
                product_matches = retrieve_products(self.retriever, query, k=top_k)
                if product_matches:
                    # concise product_context for prompt
                    product_context = "\n".join([f"{r.get('text','')}" for r in product_matches])
                    sources.append("Product Database")
                    confidence += 40
            except Exception:
                product_matches = []

            # 2) Customer Memory
            try:
                memory_context = get_compact_memory(user_id)
                if memory_context and len(memory_context.strip()) > 8:
                    sources.append("Customer Memory")
                    confidence += 20
            except Exception:
                memory_context = ""

            # 2b) Brand Database
            try:
                brand_matches = retrieve_brands(self.retriever, query, k=top_k)
                if brand_matches:
                    brand_context = "\n".join([f"{b.get('text','')}" for b in brand_matches])
                    sources.append("Brand Database")
                    confidence += 15
            except Exception:
                brand_context = ""

            # 3) Trend Intelligence
            try:
                trends = self._load_trends()
                relevant = []
                for t in trends:
                    txt = (t.get("trend", "") + " " + t.get("summary", "") + " " + " ".join(t.get("brands", []))).lower()
                    if any(tok for tok in q.split() if len(tok) > 3 and tok in txt) or any(b.lower() in q for b in t.get("brands", [])):
                        relevant.append(t)
                if relevant:
                    trend_context = "\n".join([f"{t.get('year')}: {t.get('trend')} - {t.get('growth')}" for t in relevant])
                    sources.append("Trend Intelligence")
                    confidence += 15
            except Exception:
                trend_context = ""

            # 4) FAISS retrieval across stores (product/memory/trend)
            try:
                # ensure user's session memory is indexed into the retriever so FAISS can search it
                try:
                    import importlib

                    session_mod = importlib.import_module("memory.session_store")
                    if self.retriever:
                        self.retriever.index_user_memory(user_id, session_mod)
                except Exception:
                    pass

                if self.retriever:
                    faiss_results = self.retriever.retrieve(query, top_k=top_k)
                    if faiss_results:
                        sources.append("FAISS")
                        confidence += 25
            except Exception:
                faiss_results = []

        # TECHNOLOGY FLOW
        elif is_tech and not is_product:
            # 1) Wikipedia
            try:
                if should_use_wikipedia(query):
                    wiki_data = search_wikipedia(query)
                    if wiki_data.get("success"):
                        wiki_context = wiki_data.get("summary", "")
                        sources.append("Wikipedia")
                        confidence += 30
            except Exception:
                wiki_context = ""

            # 2) Wikidata
            try:
                wd = search_wikidata(query, max_results=top_k)
                if wd.get("success") and wd.get("results"):
                    wikidata_snips = [f"{r.get('label')} - {r.get('description','')}" for r in wd.get("results", [])]
                    if wikidata_snips:
                        wiki_context = (wiki_context + "\n" + "\n".join(wikidata_snips)).strip()
                        sources.append("Wikidata")
                        confidence += 30
            except Exception:
                pass

            # 3) FAISS
            try:
                try:
                    import importlib

                    session_mod = importlib.import_module("memory.session_store")
                    if self.retriever:
                        self.retriever.index_user_memory(user_id, session_mod)
                except Exception:
                    pass

                if self.retriever:
                    faiss_results = self.retriever.retrieve(query, top_k=top_k)
                    if faiss_results:
                        sources.append("FAISS")
                        confidence += 25
            except Exception:
                faiss_results = []

        # DEFAULT / MIXED: run a conservative combined retrieval
        else:
            try:
                product_matches = retrieve_products(self.retriever, query, k=top_k)
                if product_matches:
                    product_context = "\n".join([f"{r.get('text','')}" for r in product_matches])
                    sources.append("Product Database")
                    confidence += 30
            except Exception:
                product_matches = []

            try:
                memory_context = get_compact_memory(user_id)
                if memory_context and len(memory_context.strip()) > 8:
                    sources.append("Customer Memory")
                    confidence += 15
            except Exception:
                memory_context = ""

            try:
                if should_use_wikipedia(query):
                    wiki_data = search_wikipedia(query)
                    if wiki_data.get("success"):
                        wiki_context = wiki_data.get("summary", "")
                        sources.append("Wikipedia")
                        confidence += 20
            except Exception:
                wiki_context = ""

            try:
                try:
                    import importlib

                    session_mod = importlib.import_module("memory.session_store")
                    if self.retriever:
                        self.retriever.index_user_memory(user_id, session_mod)
                except Exception:
                    pass

                if self.retriever:
                    faiss_results = self.retriever.retrieve(query, top_k=top_k)
                    if faiss_results:
                        sources.append("FAISS")
                        confidence += 20
            except Exception:
                faiss_results = []

        # Compose compressed context for LLM prompts (preserve provenance)
        # merge found pieces: prefer memory, products, trends, wiki, faiss
        merged_parts = []
        if memory_context:
            merged_parts.append({"text": memory_context})
        if product_context:
            merged_parts.append({"text": product_context})
        if brand_context:
            merged_parts.append({"text": brand_context})
        if trend_context:
            merged_parts.append({"text": trend_context})
        if wiki_context:
            merged_parts.append({"text": wiki_context})
        if faiss_results:
            merged_parts.extend(faiss_results)

        compressed_context = compress_context(merged_parts, max_chars=2000)

        # Cap confidence to [5, 98]
        if confidence <= 0:
            confidence = 5
        if confidence > 98:
            confidence = 98

        return {
            "memory_context": memory_context,
            "product_context": product_context,
            "wiki_context": wiki_context,
            "faiss_results": faiss_results,
            "trend_context": trend_context,
            "compressed_context": compressed_context,
            "confidence": int(confidence),
            "sources": sources,
        }

    def _load_trends(self) -> List[Dict[str, Any]]:
        """Load trend intelligence files from the knowledge directory.

        Looks for `ai_trends.json`, `gpu_trends.json`, and `market_trends.json`.
        """
        try:
            root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            knowledge_dir = os.path.join(root, "knowledge")
            out: List[Dict[str, Any]] = []
            for fn in ("ai_trends.json", "gpu_trends.json", "market_trends.json"):
                path = os.path.join(knowledge_dir, fn)
                if not os.path.exists(path):
                    continue
                try:
                    with open(path, "r", encoding="utf-8") as fh:
                        data = json.load(fh)
                        if isinstance(data, list):
                            out.extend(data)
                except Exception:
                    continue
            return out
        except Exception:
            return []


__all__ = ["KnowledgePipeline"]
