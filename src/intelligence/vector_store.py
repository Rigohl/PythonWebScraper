"""
Vector Store for Curiosity System

This module provides vector storage and similarity search capabilities for the
curiosity system. It supports both FAISS (when available) and SQLite fallback
for storing and retrieving text embeddings.
"""

import logging
import sqlite3
import json
import asyncio
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import numpy as np

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

from .embedding_adapter import EmbeddingResult
from .. import settings

logger = logging.getLogger(__name__)

@dataclass
class VectorSearchResult:
    """Result of a vector similarity search"""
    id: str
    text: str
    embedding: List[float]
    similarity: float
    metadata: Dict[str, Any]

@dataclass
class StoredVector:
    """Vector stored in the database"""
    id: str
    text: str
    embedding: List[float]
    metadata: Dict[str, Any]
    timestamp: float

class VectorStore:
    """
    Vector store that supports both FAISS and SQLite for similarity search.
    Provides a unified interface for storing and retrieving text embeddings.
    """

    def __init__(self, db_path: Optional[str] = None, use_faiss: bool = True):
        self.db_path = db_path or settings.CURIOSITY_VECTOR_DB_PATH
        self.use_faiss = use_faiss and FAISS_AVAILABLE and settings.CURIOSITY_VECTOR_STORE_FAISS
        self.dimensions = settings.CURIOSITY_EMBEDDING_DIMENSIONS

        # SQLite connection
        self.conn = None
        self._init_sqlite()

        # FAISS index
        self.faiss_index = None
        self.id_mapping = {}  # Maps FAISS indices to database IDs
        self.reverse_mapping = {}  # Maps database IDs to FAISS indices

        if self.use_faiss:
            self._init_faiss()
        else:
            logger.info("Using SQLite-only vector store (FAISS not available or disabled)")

    def _init_sqlite(self):
        """Initialize SQLite database for vector storage."""
        try:
            # Ensure directory exists
            db_dir = Path(self.db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)

            self.conn = sqlite3.connect(self.db_path)
            self._create_tables()
            logger.info(f"SQLite vector store initialized at: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize SQLite: {e}")
            raise

    def _create_tables(self):
        """Create necessary tables for vector storage."""
        cursor = self.conn.cursor()

        # Main vectors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vectors (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                embedding TEXT NOT NULL,  -- JSON array of floats
                metadata TEXT,  -- JSON metadata
                timestamp REAL NOT NULL,
                created_at REAL DEFAULT (strftime('%s', 'now'))
            )
        ''')

        # Index for faster timestamp queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_vectors_timestamp
            ON vectors(timestamp)
        ''')

        # Index for metadata queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_vectors_metadata
            ON vectors(metadata)
        ''')

        self.conn.commit()

    def _init_faiss(self):
        """Initialize FAISS index for fast similarity search."""
        try:
            # Create L2 distance index
            self.faiss_index = faiss.IndexFlatL2(self.dimensions)

            # Load existing vectors into FAISS
            self._load_vectors_to_faiss()

            logger.info(f"FAISS index initialized with {self.faiss_index.ntotal} vectors")
        except Exception as e:
            logger.error(f"Failed to initialize FAISS: {e}")
            self.use_faiss = False

    def _load_vectors_to_faiss(self):
        """Load existing vectors from SQLite into FAISS index."""
        if not self.use_faiss or not self.faiss_index:
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id, embedding FROM vectors ORDER BY timestamp')

            vectors = []
            ids = []

            for row in cursor.fetchall():
                vector_id, embedding_json = row
                embedding = json.loads(embedding_json)

                if len(embedding) == self.dimensions:
                    vectors.append(embedding)
                    ids.append(vector_id)

            if vectors:
                vectors_array = np.array(vectors, dtype=np.float32)
                self.faiss_index.add(vectors_array)

                # Update mappings
                for i, vector_id in enumerate(ids):
                    self.id_mapping[i] = vector_id
                    self.reverse_mapping[vector_id] = i

        except Exception as e:
            logger.error(f"Failed to load vectors to FAISS: {e}")
            self.use_faiss = False

    async def store_vector(self, vector_id: str, embedding_result: EmbeddingResult,
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store a vector in the database.

        Args:
            vector_id: Unique identifier for the vector
            embedding_result: EmbeddingResult from EmbeddingAdapter
            metadata: Optional metadata dictionary

        Returns:
            True if stored successfully
        """
        try:
            timestamp = asyncio.get_event_loop().time()
            metadata_json = json.dumps(metadata or {})
            embedding_json = json.dumps(embedding_result.embedding)

            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO vectors
                (id, text, embedding, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (vector_id, embedding_result.text, embedding_json, metadata_json, timestamp))

            self.conn.commit()

            # Add to FAISS if available
            if self.use_faiss and self.faiss_index:
                await self._add_to_faiss(vector_id, embedding_result.embedding)

            logger.debug(f"Stored vector: {vector_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to store vector {vector_id}: {e}")
            return False

    async def _add_to_faiss(self, vector_id: str, embedding: List[float]):
        """Add vector to FAISS index."""
        if not self.use_faiss or not self.faiss_index:
            return

        try:
            vector_array = np.array([embedding], dtype=np.float32)
            self.faiss_index.add(vector_array)

            # Update mappings
            index = self.faiss_index.ntotal - 1
            self.id_mapping[index] = vector_id
            self.reverse_mapping[vector_id] = index

        except Exception as e:
            logger.error(f"Failed to add vector to FAISS: {e}")

    async def search_similar(self, query_embedding: List[float], limit: int = 10,
                           threshold: Optional[float] = None) -> List[VectorSearchResult]:
        """
        Search for similar vectors using the query embedding.

        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results
            threshold: Minimum similarity threshold (0-1)

        Returns:
            List of similar vectors with similarity scores
        """
        if self.use_faiss and self.faiss_index and self.faiss_index.ntotal > 0:
            return await self._search_faiss(query_embedding, limit, threshold)
        else:
            return await self._search_sqlite(query_embedding, limit, threshold)

    async def _search_faiss(self, query_embedding: List[float], limit: int,
                           threshold: Optional[float]) -> List[VectorSearchResult]:
        """Search using FAISS index."""
        try:
            query_array = np.array([query_embedding], dtype=np.float32)

            # Search for similar vectors
            distances, indices = self.faiss_index.search(query_array, min(limit * 2, self.faiss_index.ntotal))

            results = []
            for distance, index in zip(distances[0], indices[0]):
                if index == -1:  # No more results
                    break

                vector_id = self.id_mapping.get(index)
                if not vector_id:
                    continue

                # Get vector data from database
                stored_vector = await self._get_vector_by_id(vector_id)
                if not stored_vector:
                    continue

                # Convert L2 distance to similarity (cosine-like)
                similarity = 1.0 / (1.0 + distance)  # Simple conversion

                if threshold and similarity < threshold:
                    continue

                results.append(VectorSearchResult(
                    id=stored_vector.id,
                    text=stored_vector.text,
                    embedding=stored_vector.embedding,
                    similarity=similarity,
                    metadata=stored_vector.metadata
                ))

                if len(results) >= limit:
                    break

            return results

        except Exception as e:
            logger.error(f"FAISS search failed: {e}")
            return await self._search_sqlite(query_embedding, limit, threshold)

    async def _search_sqlite(self, query_embedding: List[float], limit: int,
                           threshold: Optional[float]) -> List[VectorSearchResult]:
        """Fallback search using SQLite (cosine similarity)."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id, text, embedding, metadata FROM vectors')

            results = []
            for row in cursor.fetchall():
                vector_id, text, embedding_json, metadata_json = row
                stored_embedding = json.loads(embedding_json)
                metadata = json.loads(metadata_json) if metadata_json else {}

                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_embedding, stored_embedding)

                if threshold and similarity < threshold:
                    continue

                results.append(VectorSearchResult(
                    id=vector_id,
                    text=text,
                    embedding=stored_embedding,
                    similarity=similarity,
                    metadata=metadata
                ))

            # Sort by similarity and limit results
            results.sort(key=lambda x: x.similarity, reverse=True)
            return results[:limit]

        except Exception as e:
            logger.error(f"SQLite search failed: {e}")
            return []

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)

            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            return max(0.0, min(1.0, dot_product / (norm1 * norm2)))

        except Exception:
            return 0.0

    async def _get_vector_by_id(self, vector_id: str) -> Optional[StoredVector]:
        """Get vector data by ID from database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT text, embedding, metadata, timestamp FROM vectors WHERE id = ?',
                          (vector_id,))

            row = cursor.fetchone()
            if not row:
                return None

            text, embedding_json, metadata_json, timestamp = row
            embedding = json.loads(embedding_json)
            metadata = json.loads(metadata_json) if metadata_json else {}

            return StoredVector(
                id=vector_id,
                text=text,
                embedding=embedding,
                metadata=metadata,
                timestamp=timestamp
            )

        except Exception as e:
            logger.error(f"Failed to get vector {vector_id}: {e}")
            return None

    async def delete_vector(self, vector_id: str) -> bool:
        """
        Delete a vector from the store.

        Args:
            vector_id: ID of vector to delete

        Returns:
            True if deleted successfully
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM vectors WHERE id = ?', (vector_id,))
            self.conn.commit()

            # Remove from FAISS if available
            if self.use_faiss and vector_id in self.reverse_mapping:
                # Note: FAISS doesn't support deletion, we'd need to rebuild the index
                faiss_index = self.reverse_mapping[vector_id]
                del self.id_mapping[faiss_index]
                del self.reverse_mapping[vector_id]

            logger.debug(f"Deleted vector: {vector_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete vector {vector_id}: {e}")
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM vectors')

            count, min_time, max_time = cursor.fetchone()

            return {
                "total_vectors": count or 0,
                "using_faiss": self.use_faiss,
                "faiss_available": FAISS_AVAILABLE,
                "dimensions": self.dimensions,
                "oldest_vector": min_time,
                "newest_vector": max_time,
                "db_path": self.db_path
            }

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}

    def close(self):
        """Close the vector store and cleanup resources."""
        if self.conn:
            self.conn.close()
            self.conn = None

        # FAISS doesn't need explicit cleanup
        logger.info("Vector store closed")

# Global instance
vector_store = VectorStore()

# Factory function
def create_vector_store(db_path: Optional[str] = None, use_faiss: bool = True) -> VectorStore:
    """Create a new VectorStore instance."""
    return VectorStore(db_path=db_path, use_faiss=use_faiss)</content>
<parameter name="filePath">c:\Users\DELL\Desktop\PythonWebScraper\src\intelligence\vector_store.py
