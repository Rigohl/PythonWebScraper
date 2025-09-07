"""
Novelty Detector for Curiosity System

This module detects novel content by combining multiple signals:
- Semantic similarity using embeddings
- Neural network activation patterns
- Text-based novelty cues (keywords, patterns)
- Temporal novelty (recency-based)
"""

import asyncio
import hashlib
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from .. import settings
from .embedding_adapter import EmbeddingAdapter, EmbeddingResult
from .vector_store import VectorSearchResult, VectorStore

logger = logging.getLogger(__name__)


@dataclass
class NoveltyScore:
    """Comprehensive novelty score combining multiple signals"""

    overall_score: float  # 0.0 to 1.0, higher = more novel
    semantic_novelty: float  # Based on embedding similarity
    neural_novelty: float  # Based on neural network patterns
    text_novelty: float  # Based on text patterns and keywords
    temporal_novelty: float  # Based on recency
    confidence: float  # Confidence in the novelty assessment
    reasons: List[str]  # Human-readable reasons for the score


@dataclass
class NoveltyAnalysis:
    """Complete novelty analysis result"""

    content: str
    score: NoveltyScore
    similar_items: List[VectorSearchResult]
    novelty_cues: List[str]
    analysis_timestamp: float


class NoveltyDetector:
    """
    Detects novel content using multiple complementary approaches.
    Combines semantic similarity, neural signals, and text analysis.
    """

    def __init__(
        self,
        embedding_adapter: Optional[EmbeddingAdapter] = None,
        vector_store: Optional[VectorStore] = None,
    ):
        self.embedding_adapter = embedding_adapter
        self.vector_store = vector_store

        # Novelty detection parameters
        self.similarity_threshold = settings.CURIOSITY_NOVELTY_THRESHOLD
        self.neural_threshold = settings.CURIOSITY_NEURAL_NOVELTY_THRESHOLD
        self.temporal_decay_hours = settings.CURIOSITY_TEMPORAL_DECAY_HOURS

        # Text novelty patterns
        self.novelty_keywords = self._load_novelty_keywords()
        self.novelty_patterns = self._compile_patterns()

        logger.info("NoveltyDetector initialized")

    def _load_novelty_keywords(self) -> Set[str]:
        """Load keywords that indicate novelty."""
        # Could be loaded from config file in the future
        return {
            "new",
            "novel",
            "innovative",
            "breakthrough",
            "discovery",
            "unprecedented",
            "revolutionary",
            "groundbreaking",
            "pioneering",
            "emerging",
            "cutting-edge",
            "state-of-the-art",
            "advanced",
            "latest",
            "recent",
            "update",
            "announcement",
            "release",
        }

    def _compile_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns for novelty detection."""
        patterns = [
            # Date patterns indicating recency
            r"\b(2024|2025)\b",
            r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+(2024|2025)\b",
            # Version patterns
            r"\bv?\d+\.\d+(\.\d+)*\b",
            # Update/change indicators
            r"\b(updated?|changed?|modified?|released?)\b",
            r"\b(new version|latest version|recent version)\b",
        ]

        return [re.compile(pattern, re.IGNORECASE) for pattern in patterns]

    async def analyze_novelty(
        self, content: str, context: Optional[Dict[str, Any]] = None
    ) -> NoveltyAnalysis:
        """
        Perform complete novelty analysis on content.

        Args:
            content: Text content to analyze
            context: Optional context information

        Returns:
            Complete novelty analysis
        """
        if not content or not content.strip():
            return self._empty_analysis(content)

        analysis_timestamp = asyncio.get_event_loop().time()

        # Generate embedding for semantic analysis
        embedding_result = (
            await self.embedding_adapter.generate_embedding(content)
            if self.embedding_adapter
            else None
        )

        # Find similar content
        similar_items = []
        if embedding_result and self.vector_store:
            similar_items = await self.vector_store.search_similar(
                embedding_result.embedding, limit=5, threshold=self.similarity_threshold
            )

        # Calculate different novelty components
        semantic_novelty = self._calculate_semantic_novelty(similar_items)
        text_novelty = self._calculate_text_novelty(content)
        temporal_novelty = self._calculate_temporal_novelty(content, analysis_timestamp)
        neural_novelty = self._calculate_neural_novelty(content, context)

        # Combine scores with weights
        overall_score = self._combine_scores(
            semantic_novelty, neural_novelty, text_novelty, temporal_novelty
        )

        # Calculate confidence based on available signals
        confidence = self._calculate_confidence(
            embedding_result, similar_items, content
        )

        # Generate reasons
        reasons = self._generate_reasons(
            semantic_novelty,
            neural_novelty,
            text_novelty,
            temporal_novelty,
            similar_items,
        )

        # Extract novelty cues
        novelty_cues = self._extract_novelty_cues(content)

        score = NoveltyScore(
            overall_score=overall_score,
            semantic_novelty=semantic_novelty,
            neural_novelty=neural_novelty,
            text_novelty=text_novelty,
            temporal_novelty=temporal_novelty,
            confidence=confidence,
            reasons=reasons,
        )

        return NoveltyAnalysis(
            content=content,
            score=score,
            similar_items=similar_items,
            novelty_cues=novelty_cues,
            analysis_timestamp=analysis_timestamp,
        )

    def _calculate_semantic_novelty(
        self, similar_items: List[VectorSearchResult]
    ) -> float:
        """Calculate novelty based on semantic similarity to existing content."""
        if not similar_items:
            return 1.0  # Completely novel if no similar items

        # Use the highest similarity as the novelty inverse
        max_similarity = max(item.similarity for item in similar_items)

        # Novelty = 1 - similarity (with some smoothing)
        novelty = 1.0 - (max_similarity * 0.9)  # Dampen the effect slightly

        return max(0.0, min(1.0, novelty))

    def _calculate_text_novelty(self, content: str) -> float:
        """Calculate novelty based on text patterns and keywords."""
        if not content:
            return 0.0

        content_lower = content.lower()
        score = 0.0

        # Keyword-based novelty
        keyword_matches = sum(
            1 for keyword in self.novelty_keywords if keyword in content_lower
        )
        keyword_score = min(1.0, keyword_matches / 3.0)  # Cap at 3 keywords
        score += keyword_score * 0.6

        # Pattern-based novelty
        pattern_matches = sum(
            1 for pattern in self.novelty_patterns if pattern.search(content)
        )
        pattern_score = min(1.0, pattern_matches / 2.0)  # Cap at 2 patterns
        score += pattern_score * 0.4

        return score

    def _calculate_temporal_novelty(self, content: str, current_time: float) -> float:
        """Calculate novelty based on temporal indicators."""
        # Look for recent dates in content
        recent_date_patterns = [
            r"\b2024\b",
            r"\b2025\b",
            r"\b(january|february|march|april|may|june)\s+\d{1,2},?\s+(2024|2025)\b",
        ]

        score = 0.0
        for pattern in recent_date_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                score = 0.8  # High novelty for recent dates
                break

        # Decay over time (simulate temporal novelty decay)
        hours_old = (current_time - asyncio.get_event_loop().time()) / 3600
        if hours_old > 0:
            decay_factor = max(0.1, 1.0 - (hours_old / self.temporal_decay_hours))
            score *= decay_factor

        return score

    def _calculate_neural_novelty(
        self, content: str, context: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate novelty based on neural network patterns."""
        # This is a simplified version - in a real implementation, this would
        # use actual neural network activations or complexity measures

        if not context:
            return 0.5  # Neutral score without context

        # Use content length and complexity as proxy for neural novelty
        length_score = min(
            1.0, len(content) / 1000
        )  # Longer content might be more novel
        complexity_score = self._calculate_text_complexity(content)

        # Combine with context factors
        context_boost = 0.0
        if context.get("is_from_web", False):
            context_boost += 0.2  # Web content might be more novel
        if context.get("is_user_generated", False):
            context_boost += 0.1  # User content might be novel

        neural_score = length_score * 0.4 + complexity_score * 0.4 + context_boost * 0.2
        return max(0.0, min(1.0, neural_score))

    def _calculate_text_complexity(self, content: str) -> float:
        """Calculate text complexity as a novelty signal."""
        if not content:
            return 0.0

        # Simple complexity metrics
        words = content.split()
        sentences = re.split(r"[.!?]+", content)

        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        avg_sentence_length = len(words) / len(sentences) if sentences else 0

        # Normalize to 0-1 range
        word_complexity = min(1.0, avg_word_length / 10.0)
        sentence_complexity = min(1.0, avg_sentence_length / 20.0)

        return (word_complexity + sentence_complexity) / 2.0

    def _combine_scores(
        self, semantic: float, neural: float, text: float, temporal: float
    ) -> float:
        """Combine different novelty scores into an overall score."""
        # Weighted combination
        weights = {"semantic": 0.4, "neural": 0.3, "text": 0.2, "temporal": 0.1}

        overall = (
            semantic * weights["semantic"]
            + neural * weights["neural"]
            + text * weights["text"]
            + temporal * weights["temporal"]
        )

        return max(0.0, min(1.0, overall))

    def _calculate_confidence(
        self,
        embedding_result: Optional[EmbeddingResult],
        similar_items: List[VectorSearchResult],
        content: str,
    ) -> float:
        """Calculate confidence in the novelty assessment."""
        confidence = 0.5  # Base confidence

        # Higher confidence with embedding
        if embedding_result:
            confidence += 0.2

        # Higher confidence with similar items to compare against
        if similar_items:
            confidence += 0.2

        # Higher confidence with substantial content
        if len(content) > 100:
            confidence += 0.1

        return min(1.0, confidence)

    def _generate_reasons(
        self,
        semantic: float,
        neural: float,
        text: float,
        temporal: float,
        similar_items: List[VectorSearchResult],
    ) -> List[str]:
        """Generate human-readable reasons for the novelty score."""
        reasons = []

        if semantic > 0.7:
            reasons.append(
                "High semantic novelty - content differs significantly from known items"
            )
        elif semantic < 0.3:
            reasons.append(
                "Low semantic novelty - content similar to existing knowledge"
            )

        if neural > 0.6:
            reasons.append("Neural patterns suggest novel content structure")
        elif neural < 0.4:
            reasons.append("Neural patterns indicate familiar content structure")

        if text > 0.5:
            reasons.append(
                "Text contains novelty indicators (keywords, patterns, dates)"
            )
        elif text < 0.3:
            reasons.append("Text lacks novelty indicators")

        if temporal > 0.5:
            reasons.append("Content appears temporally recent")
        elif temporal < 0.3:
            reasons.append("Content appears temporally stale")

        if similar_items:
            max_similarity = max(item.similarity for item in similar_items)
            reasons.append(".2f")

        return reasons

    def _extract_novelty_cues(self, content: str) -> List[str]:
        """Extract specific cues that indicate novelty."""
        cues = []

        # Extract novelty keywords
        content_lower = content.lower()
        for keyword in self.novelty_keywords:
            if keyword in content_lower:
                cues.append(f"Keyword: {keyword}")

        # Extract matching patterns
        for pattern in self.novelty_patterns:
            match = pattern.search(content)
            if match:
                cues.append(f"Pattern: {match.group()}")

        return cues

    def _empty_analysis(self, content: str) -> NoveltyAnalysis:
        """Return empty analysis for invalid content."""
        score = NoveltyScore(
            overall_score=0.0,
            semantic_novelty=0.0,
            neural_novelty=0.0,
            text_novelty=0.0,
            temporal_novelty=0.0,
            confidence=0.0,
            reasons=["Invalid or empty content"],
        )

        return NoveltyAnalysis(
            content=content,
            score=score,
            similar_items=[],
            novelty_cues=[],
            analysis_timestamp=asyncio.get_event_loop().time(),
        )

    def is_novel(
        self, analysis: NoveltyAnalysis, threshold: Optional[float] = None
    ) -> bool:
        """
        Determine if content should be considered novel based on analysis.

        Args:
            analysis: NoveltyAnalysis result
            threshold: Override threshold (uses config default if None)

        Returns:
            True if content is considered novel
        """
        threshold = threshold or self.similarity_threshold
        return analysis.score.overall_score >= threshold


# Global instance
novelty_detector = NoveltyDetector()


# Factory function
def create_novelty_detector(
    embedding_adapter: Optional[EmbeddingAdapter] = None,
    vector_store: Optional[VectorStore] = None,
) -> NoveltyDetector:
    """Create a new NoveltyDetector instance."""
    return NoveltyDetector(embedding_adapter, vector_store)
