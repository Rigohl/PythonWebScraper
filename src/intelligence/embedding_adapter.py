"""
Embedding Adapter for Curiosity System

This module provides text embeddings for the curiosity system using OpenAI's
embedding models. It serves as a bridge between the curiosity system and
the existing LLM infrastructure.
"""

import logging
import asyncio
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import numpy as np

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..adapters.llm_adapter import LLMAdapter
from .. import settings

logger = logging.getLogger(__name__)

@dataclass
class EmbeddingResult:
    """Result of embedding generation"""
    text: str
    embedding: List[float]
    model: str
    dimensions: int
    tokens_used: int = 0

class EmbeddingAdapter:
    """
    Adapter for generating text embeddings using OpenAI's embedding models.
    Provides a clean interface for the curiosity system to generate embeddings.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.LLM_API_KEY
        self.model = model or settings.CURIOSITY_EMBEDDING_MODEL
        self.dimensions = settings.CURIOSITY_EMBEDDING_DIMENSIONS
        self.client = None

        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI not available. EmbeddingAdapter will use fallback mode.")
            return

        if not self.api_key:
            logger.warning("No OpenAI API key provided. EmbeddingAdapter will use fallback mode.")
            return

        try:
            self.client = OpenAI(api_key=self.api_key)
            logger.info(f"EmbeddingAdapter initialized with model: {self.model}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None

    async def generate_embedding(self, text: str) -> Optional[EmbeddingResult]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            EmbeddingResult or None if failed
        """
        if not self.client or not OPENAI_AVAILABLE:
            return self._fallback_embedding(text)

        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return None

        try:
            # Clean and prepare text
            cleaned_text = text.strip()
            if len(cleaned_text) > 8000:  # OpenAI limit
                cleaned_text = cleaned_text[:8000]
                logger.debug("Text truncated to 8000 characters for embedding")

            # Generate embedding
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.embeddings.create(
                    input=[cleaned_text],
                    model=self.model
                )
            )

            embedding = response.data[0].embedding
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0

            return EmbeddingResult(
                text=cleaned_text,
                embedding=embedding,
                model=self.model,
                dimensions=len(embedding),
                tokens_used=tokens_used
            )

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return self._fallback_embedding(text)

    async def generate_embeddings_batch(self, texts: List[str]) -> List[Optional[EmbeddingResult]]:
        """
        Generate embeddings for multiple texts in batch.

        Args:
            texts: List of texts to embed

        Returns:
            List of EmbeddingResult objects (or None for failures)
        """
        if not self.client or not OPENAI_AVAILABLE:
            return [self._fallback_embedding(text) for text in texts]

        # Filter out empty texts
        valid_texts = []
        indices = []
        for i, text in enumerate(texts):
            if text and text.strip():
                valid_texts.append(text.strip()[:8000])  # Truncate if needed
                indices.append(i)

        if not valid_texts:
            return [None] * len(texts)

        try:
            # Generate embeddings in batch
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.embeddings.create(
                    input=valid_texts,
                    model=self.model
                )
            )

            # Reconstruct results in original order
            results = [None] * len(texts)
            for i, (original_idx, data) in enumerate(zip(indices, response.data)):
                embedding = data.embedding
                tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0

                results[original_idx] = EmbeddingResult(
                    text=valid_texts[i],
                    embedding=embedding,
                    model=self.model,
                    dimensions=len(embedding),
                    tokens_used=tokens_used
                )

            return results

        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            return [self._fallback_embedding(text) for text in texts]

    def _fallback_embedding(self, text: str) -> Optional[EmbeddingResult]:
        """
        Generate a simple fallback embedding when OpenAI is not available.
        Uses basic text features as a poor man's embedding.
        """
        if not text or not text.strip():
            return None

        try:
            # Simple text features as fallback
            cleaned_text = text.strip().lower()

            # Basic features
            features = [
                len(cleaned_text),  # Length
                len(cleaned_text.split()),  # Word count
                sum(ord(c) for c in cleaned_text) / len(cleaned_text),  # Average char code
                cleaned_text.count(' '),  # Space count
                cleaned_text.count('.'),  # Sentence count
                cleaned_text.count(','),  # Comma count
            ]

            # Pad to target dimensions with zeros
            embedding = features + [0.0] * (self.dimensions - len(features))

            return EmbeddingResult(
                text=cleaned_text,
                embedding=embedding,
                model="fallback",
                dimensions=self.dimensions,
                tokens_used=0
            )

        except Exception as e:
            logger.error(f"Fallback embedding failed: {e}")
            return None

    def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)

            # Ensure result is between 0 and 1
            return max(0.0, min(1.0, similarity))

        except Exception as e:
            logger.error(f"Failed to calculate cosine similarity: {e}")
            return 0.0

    def is_available(self) -> bool:
        """Check if the embedding adapter is properly configured and available."""
        return self.client is not None and OPENAI_AVAILABLE and bool(self.api_key)

    def get_status(self) -> Dict[str, Any]:
        """Get status information about the embedding adapter."""
        return {
            "available": self.is_available(),
            "model": self.model,
            "dimensions": self.dimensions,
            "openai_available": OPENAI_AVAILABLE,
            "api_key_configured": bool(self.api_key)
        }

# Global instance for easy access
embedding_adapter = EmbeddingAdapter()

# Factory function
def create_embedding_adapter(api_key: Optional[str] = None, model: Optional[str] = None) -> EmbeddingAdapter:
    """Create a new EmbeddingAdapter instance."""
    return EmbeddingAdapter(api_key=api_key, model=model)</content>
<parameter name="filePath">c:\Users\DELL\Desktop\PythonWebScraper\src\intelligence\embedding_adapter.py
