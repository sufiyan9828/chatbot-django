import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import CrossEncoder
from rank_bm25 import BM25Okapi
from .observability import observability
import logging
import uuid
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Manages long-term memory using Hybrid Search (Vector + Keyword).
    - Vector: ChromaDB (Semantic understanding)
    - Keyword: BM25 (Exact matching for IDs, specific terms)
    - Reranking: Cross-Encoder (Quality assurance)
    """

    def __init__(self, persistence_path="chroma_db"):
        self.persistence_path = persistence_path

        # 1. Vector Store (ChromaDB)
        try:
            self.embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            self.client = chromadb.PersistentClient(path=persistence_path)
            self.collection = self.client.get_or_create_collection(
                name="chatbot_memory", embedding_function=self.embedder
            )
            logger.info(f"MemoryManager initialized at {persistence_path}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.collection = None

        # 2. Keyword Index (BM25) - In-memory for this demo
        # In a real production system, use Elasticsearch/Opensearch
        self.documents = []  # List of text documents
        self.bm25 = None
        self._load_local_indices()

        # 3. Reranker (Cross-Encoder)
        try:
            # Efficient reranker model
            self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        except Exception as e:
            logger.warning(f"Reranker could not be loaded: {e}")
            self.reranker = None

    def _load_local_indices(self):
        """Rebuild BM25 index from ChromaDB"""
        if not self.collection:
            return

        try:
            # Fetch all documents to build BM25 index
            data = self.collection.get()
            if data and data["documents"]:
                self.documents = data["documents"]
                tokenized_corpus = [doc.split(" ") for doc in self.documents]
                self.bm25 = BM25Okapi(tokenized_corpus)
        except Exception as e:
            logger.error(f"Failed to load BM25 index: {e}")

    def add_memory(self, text: str, metadata: Dict[str, Any] = None):
        """Add memory to both Vector and Keyword indices."""
        if not self.collection:
            return

        try:
            mem_id = str(uuid.uuid4())

            # Add to Vector Store
            self.collection.add(
                documents=[text], metadatas=[metadata or {}], ids=[mem_id]
            )

            # Add to Keyword Index (Rebuild for simplicity in this demo)
            self.documents.append(text)
            tokenized_corpus = [doc.split(" ") for doc in self.documents]
            self.bm25 = BM25Okapi(tokenized_corpus)

            logger.info(f"Added memory: {text[:50]}...")
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")

    @observability.trace(name="memory_search")
    def search_memory(self, query: str, n_results: int = 5) -> List[str]:
        """
        Hybrid Semantic Search with Reranking.
        1. Retrieve candidates via Vector Search (Semantic)
        2. Retrieve candidates via BM25 (Keyword)
        3. Dedup and Rerank results
        """
        if not self.collection:
            return []

        candidates = set()

        # 1. Vector Search
        try:
            vector_res = self.collection.query(query_texts=[query], n_results=n_results)
            if vector_res["documents"]:
                for doc in vector_res["documents"][0]:
                    candidates.add(doc)
        except Exception as e:
            logger.error(f"Vector search failed: {e}")

        # 2. Keyword Search (BM25)
        if self.bm25:
            try:
                tokenized_query = query.split(" ")
                keyword_res = self.bm25.get_top_n(
                    tokenized_query, self.documents, n=n_results
                )
                for doc in keyword_res:
                    candidates.add(doc)
            except Exception as e:
                logger.error(f"Keyword search failed: {e}")

        # If no candidates, return empty
        if not candidates:
            return []

        unique_candidates = list(candidates)

        # 3. Reranking
        if self.reranker:
            try:
                # Pair query with each candidate
                pairs = [[query, doc] for doc in unique_candidates]
                scores = self.reranker.predict(pairs)

                # Sort by score descending
                scored_results = sorted(
                    zip(unique_candidates, scores), key=lambda x: x[1], reverse=True
                )

                # Return top N
                return [doc for doc, score in scored_results[:n_results]]
            except Exception as e:
                logger.error(f"Reranking failed: {e}")
                return unique_candidates[:n_results]

        return unique_candidates[:n_results]


# Global instance
memory_manager = MemoryManager()
