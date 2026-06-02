import unittest
from unittest.mock import MagicMock, patch
import numpy as np

from rag.wikipedia_loader import clean_text, chunk_text, search_and_load
from rag.embeddings import EmbeddingModel
from rag.vector_store import FaissVectorStore, VectorStoreManager
from rag.retriever import Retriever
from rag.context_compressor import compress_context, build_system_prompt


class TestWikipediaLoader(unittest.TestCase):
    def test_clean_text(self):
        text = "This is a sentence [1]. This is another sentence [citation needed]."
        cleaned = clean_text(text)
        self.assertEqual(cleaned, "This is a sentence . This is another sentence .")

        # Test spacing and newlines
        text_with_spaces = "Hello   world \n\n\n next line"
        cleaned_spaces = clean_text(text_with_spaces)
        self.assertEqual(cleaned_spaces, "Hello world \n\n next line")

    def test_chunk_text(self):
        # Text shorter than chunk_size
        text = "Short text"
        chunks = chunk_text(text, chunk_size=50, overlap=10)
        self.assertEqual(chunks, ["Short text"])

        # Long text chunking
        long_text = "abcdefghijklmnopqrstuvwxyz"  # 26 chars
        chunks = chunk_text(long_text, chunk_size=10, overlap=2)
        # Expected:
        # chunk 1: 0 to 10 -> "abcdefghij"
        # chunk 2: 8 to 18 -> "ijklmnopqr"
        # chunk 3: 16 to 26 -> "qrstuvwxyz"
        self.assertTrue(len(chunks) >= 3)
        self.assertEqual(chunks[0], "abcdefghij")
        self.assertEqual(chunks[1], "ijklmnopqr")
        self.assertEqual(chunks[-1], "qrstuvwxyz")

    @patch("wikipediaapi.Wikipedia")
    def test_search_and_load(self, mock_wiki_class):
        mock_wiki = MagicMock()
        mock_wiki_class.return_value = mock_wiki
        
        # Mock search results titles
        mock_wiki.search.return_value = ["Python (programming language)", "Monty Python"]
        
        # Mock pages
        mock_page_1 = MagicMock()
        mock_page_1.exists.return_value = True
        mock_page_1.title = "Python (programming language)"
        mock_page_1.fullurl = "https://en.wikipedia.org/wiki/Python"
        mock_page_1.text = "Python is a high-level language."
        
        mock_page_2 = MagicMock()
        mock_page_2.exists.return_value = True
        mock_page_2.title = "Monty Python"
        mock_page_2.fullurl = "https://en.wikipedia.org/wiki/Monty_Python"
        mock_page_2.text = "Monty Python is a comedy group."
        
        def page_side_effect(title):
            if title == "Python (programming language)":
                return mock_page_1
            return mock_page_2
            
        mock_wiki.page.side_effect = page_side_effect

        results = search_and_load("Python", max_pages=2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["title"], "Python (programming language)")
        self.assertEqual(results[0]["url"], "https://en.wikipedia.org/wiki/Python")
        self.assertEqual(results[0]["text"], "Python is a high-level language.")


class TestEmbeddings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # We can load the real model since it is already cached in the local environment
        cls.embedding_model = EmbeddingModel()

    def test_embedding_dimensions(self):
        self.assertIsNotNone(self.embedding_model.dim)
        self.assertEqual(self.embedding_model.dim, 384)  # all-MiniLM-L6-v2 has 384 dimensions

    def test_embed_texts(self):
        texts = ["Hello world", "RAG pipelines are awesome"]
        vectors = self.embedding_model.embed_texts(texts)
        self.assertEqual(vectors.shape, (2, 384))
        
        # Check normalization (norm should be extremely close to 1)
        norms = np.linalg.norm(vectors, axis=1)
        for norm in norms:
            self.assertAlmostEqual(norm, 1.0, places=5)

    def test_embed_query(self):
        vector = self.embedding_model.embed_query("Query search")
        self.assertEqual(vector.shape, (384,))
        self.assertAlmostEqual(np.linalg.norm(vector), 1.0, places=5)


class TestVectorStore(unittest.TestCase):
    def setUp(self):
        self.dim = 384
        self.store = FaissVectorStore(self.dim)

    def test_add_and_search(self):
        texts = ["The quick brown fox", "Fast AI orchestrator", "Fast API server running"]
        # Create mock vectors with distinct signatures
        vectors = np.zeros((3, self.dim), dtype="float32")
        vectors[0, 0] = 1.0  # first concept
        vectors[1, 100] = 1.0  # second concept
        vectors[2, 100] = 0.9  # close to second concept
        vectors[2, 200] = 0.43

        self.store.add(texts, vectors, metadatas=[{"topic": "fox"}, {"topic": "ai"}, {"topic": "api"}])

        # Search for something close to second concept
        query = np.zeros(self.dim, dtype="float32")
        query[100] = 1.0

        results = self.store.search(query, top_k=2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["text"], "Fast AI orchestrator")
        self.assertEqual(results[0]["metadata"]["topic"], "ai")
        self.assertEqual(results[1]["text"], "Fast API server running")


class TestRetriever(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.embedding_model = EmbeddingModel()

    def setUp(self):
        self.retriever = Retriever(self.embedding_model)

    def test_index_wikipedia(self):
        wiki_pages = [
            {
                "title": "FastAPI",
                "url": "https://fastapi.tiangolo.com",
                "text": "FastAPI is a modern, fast (high-performance), web framework for building APIs."
            }
        ]
        self.retriever.index_wikipedia(wiki_pages)
        
        # Test that we can search it
        results = self.retriever.retrieve("web framework", top_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["store"], "wiki")
        self.assertIn("FastAPI", results[0]["text"])

    def test_index_user_memory(self):
        mock_session_store = MagicMock()
        mock_session_store.get_timeline.return_value = [
            {"role": "user", "content": "I am looking for pricing packages", "timestamp": "2026-06-01T12:00:00"},
            {"role": "assistant", "content": "Our basic plan is $10/month", "timestamp": "2026-06-01T12:01:00"}
        ]
        
        self.retriever.index_user_memory("user_123", mock_session_store)
        
        results = self.retriever.retrieve("pricing", top_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["store"], "memory")
        self.assertIn("pricing", results[0]["text"])


class TestContextCompressor(unittest.TestCase):
    def test_compress_context_short(self):
        retrieved = [{"text": "Hello world"}]
        compressed = compress_context(retrieved, max_chars=100)
        self.assertEqual(compressed, "Hello world")

    def test_compress_context_long(self):
        chunk1 = "This is chunk number one of the RAG system."
        chunk2 = "Here is some more interesting content about our customer support agents."
        chunk3 = "Finally, we have pricing packages and SSO details for enterprise clients."
        retrieved = [{"text": chunk1}, {"text": chunk2}, {"text": chunk3}]
        
        # We set max_chars to be small so it triggers compression
        compressed = compress_context(retrieved, max_chars=50)
        self.assertTrue("..." in compressed)

    def test_build_system_prompt(self):
        prompt = build_system_prompt("User asked about SSO.", "SSO is supported on the Enterprise plan.")
        self.assertIn("Current Year: 2026", prompt)
        self.assertIn("User asked about SSO.", prompt)
        self.assertIn("SSO is supported on the Enterprise plan.", prompt)


if __name__ == "__main__":
    unittest.main()
