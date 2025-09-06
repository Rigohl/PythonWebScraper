"""
Autonomous Learning Brain for Web Scraper

This module implements an intelligent learning system that makes the scraper more autonomous
and intelligent by learning from each scraping session. It analyzes patterns, success rates,
and adapts scraping strategies automatically.

Features:
- Pattern recognition from successful scrapes
- Adaptive strategy selection based on domain characteristics
- Performance optimization through learning
- Autonomous decision making for scraping parameters
- Memory of successful configurations per domain
"""

import json
import logging
import statistics
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ScrapingSession:
    """Represents a single scraping session with performance metrics."""

    domain: str
    url: str
    timestamp: float
    success: bool
    response_time: float
    content_length: int
    status_code: int
    retry_count: int
    user_agent: str
    delay_used: float
    extraction_quality: float  # 0.0 to 1.0
    patterns_found: List[str]
    errors: List[str]


@dataclass
class DomainIntelligence:
    """Intelligence gathered about a specific domain."""

    domain: str
    total_attempts: int
    success_rate: float
    avg_response_time: float
    optimal_delay: float
    preferred_user_agent: str
    common_patterns: List[str]
    error_patterns: List[str]
    last_updated: float
    content_types: Dict[str, int]
    best_strategies: List[str]


class AutonomousLearningBrain:
    """
    Intelligent learning system that makes the scraper autonomous and adaptive.

    This brain learns from every scraping operation and continuously improves
    the scraper's performance through pattern recognition and strategy optimization.
    """

    def __init__(self, data_path: str = "data/learning_history.json"):
        self.data_path = Path(data_path)
        self.data_path.parent.mkdir(exist_ok=True)

        # Learning data storage
        self.domain_intelligence: Dict[str, DomainIntelligence] = {}
        self.session_history: List[ScrapingSession] = []
        self.pattern_library: Dict[str, List[str]] = {}

        # Learning parameters
        self.learning_rate = 0.1
        self.memory_decay = 0.7
        self.min_sessions_for_intelligence = 5

        # Load existing knowledge
        self._load_intelligence()

        logger.info(
            "AutonomousLearningBrain initialized with intelligence on %d domains",
            len(self.domain_intelligence),
        )

    def learn_from_session(self, session: ScrapingSession) -> None:
        """
        Learn from a completed scraping session.

        Analyzes the session results and updates the brain's knowledge about
        optimal strategies, patterns, and domain-specific behavior.
        """
        try:
            # Add session to history
            self.session_history.append(session)

            # Update domain intelligence
            self._update_domain_intelligence(session)

            # Extract and learn patterns
            self._learn_patterns(session)

            # Optimize strategies
            self._optimize_strategies(session.domain)

            # Persist learning
            self._save_intelligence()

            logger.info(
                f"Learned from session: {session.domain} (success: {session.success})"
            )

        except Exception as e:
            logger.error(f"Error learning from session: {e}")

    def get_optimal_strategy(self, domain: str, url: str) -> Dict[str, Any]:
        """
        Get the optimal scraping strategy for a given domain/URL based on learned intelligence.

        Returns adaptive configuration that maximizes success probability.
        """
        try:
            # Check if we have intelligence for this domain
            if domain in self.domain_intelligence:
                intel = self.domain_intelligence[domain]

                strategy = {
                    "delay": max(intel.optimal_delay, 0.5),  # Never go below 0.5s
                    "user_agent": intel.preferred_user_agent,
                    "max_retries": 3 if intel.success_rate > 0.8 else 5,
                    "timeout": 15 if intel.avg_response_time < 5 else 30,
                    "expected_patterns": intel.common_patterns[:5],
                    "avoid_patterns": intel.error_patterns[:3],
                    "confidence": min(intel.total_attempts / 10.0, 1.0),
                }

                # Adaptive adjustments based on success rate
                if intel.success_rate < 0.5:
                    strategy["delay"] *= 1.5  # More conservative
                    strategy["max_retries"] += 2
                elif intel.success_rate > 0.9:
                    strategy["delay"] *= 0.8  # More aggressive

                logger.info(
                    f"Providing learned strategy for {domain} (confidence: {strategy['confidence']:.2f})"
                )
                return strategy

            else:
                # Default adaptive strategy for unknown domains
                return self._get_default_adaptive_strategy(url)

        except Exception as e:
            logger.error(f"Error getting optimal strategy: {e}")
            return self._get_default_adaptive_strategy(url)

    def predict_success_probability(
        self, domain: str, strategy: Dict[str, Any]
    ) -> float:
        """
        Predict the probability of success for a given domain with a specific strategy.

        Uses learned patterns to estimate likelihood of successful scraping.
        """
        try:
            if domain not in self.domain_intelligence:
                return 0.5  # Unknown domain, neutral probability

            intel = self.domain_intelligence[domain]
            base_probability = intel.success_rate

            # Adjust based on strategy alignment with learned preferences
            adjustments = 0.0

            if strategy.get("user_agent") == intel.preferred_user_agent:
                adjustments += 0.1

            if abs(strategy.get("delay", 1.0) - intel.optimal_delay) < 0.5:
                adjustments += 0.1
            else:
                adjustments -= 0.05

            # Consider pattern matching
            expected_patterns = strategy.get("expected_patterns", [])
            pattern_match_score = len(
                set(expected_patterns) & set(intel.common_patterns)
            ) / max(len(intel.common_patterns), 1)
            adjustments += pattern_match_score * 0.1

            return max(0.0, min(1.0, base_probability + adjustments))

        except Exception as e:
            logger.error(f"Error predicting success: {e}")
            return 0.5

    def get_intelligence_summary(self) -> Dict[str, Any]:
        """Get a summary of the brain's current intelligence."""
        try:
            total_sessions = len(self.session_history)
            successful_sessions = sum(1 for s in self.session_history if s.success)

            return {
                "total_sessions": total_sessions,
                "overall_success_rate": successful_sessions / max(total_sessions, 1),
                "domains_learned": len(self.domain_intelligence),
                "patterns_discovered": len(self.pattern_library),
                "top_domains": sorted(
                    [
                        (d, intel.total_attempts)
                        for d, intel in self.domain_intelligence.items()
                    ],
                    key=lambda x: x[1],
                    reverse=True,
                )[:10],
                "learning_efficiency": self._calculate_learning_efficiency(),
            }
        except Exception as e:
            logger.error(f"Error generating intelligence summary: {e}")
            return {}

    def _update_domain_intelligence(self, session: ScrapingSession) -> None:
        """Update intelligence for a specific domain based on session results."""
        domain = session.domain

        if domain not in self.domain_intelligence:
            # Create new intelligence entry
            self.domain_intelligence[domain] = DomainIntelligence(
                domain=domain,
                total_attempts=0,
                success_rate=0.0,
                avg_response_time=0.0,
                optimal_delay=1.0,
                preferred_user_agent=session.user_agent,
                common_patterns=[],
                error_patterns=[],
                last_updated=time.time(),
                content_types={},
                best_strategies=[],
            )

        intel = self.domain_intelligence[domain]

        # Update basic metrics
        intel.total_attempts += 1

        # Update success rate (weighted average)
        old_success_rate = intel.success_rate
        intel.success_rate = old_success_rate * self.memory_decay + (
            1.0 if session.success else 0.0
        ) * (1 - self.memory_decay)

        # Update response time (weighted average)
        intel.avg_response_time = (
            intel.avg_response_time * self.memory_decay
            + session.response_time * (1 - self.memory_decay)
        )

        # Update optimal delay based on success and response time
        if session.success and session.response_time < intel.avg_response_time:
            intel.optimal_delay = intel.optimal_delay * 0.9 + session.delay_used * 0.1
        elif not session.success:
            intel.optimal_delay = min(
                intel.optimal_delay * 1.1, 5.0
            )  # Increase but cap at 5s

        # Update preferred user agent based on success
        if session.success:
            intel.preferred_user_agent = session.user_agent

        # Update patterns
        if session.success and session.patterns_found:
            for pattern in session.patterns_found:
                if pattern not in intel.common_patterns:
                    intel.common_patterns.append(pattern)

        if not session.success and session.errors:
            for error in session.errors:
                if error not in intel.error_patterns:
                    intel.error_patterns.append(error)

        intel.last_updated = time.time()

    def _learn_patterns(self, session: ScrapingSession) -> None:
        """Extract and learn patterns from session data."""
        try:
            # Learn URL patterns
            url_pattern = self._extract_url_pattern(session.url)
            domain_patterns = self.pattern_library.setdefault(session.domain, [])

            if url_pattern not in domain_patterns and session.success:
                domain_patterns.append(url_pattern)

            # Learn content patterns from successful extractions
            if session.success and session.patterns_found:
                for pattern in session.patterns_found:
                    if pattern not in domain_patterns:
                        domain_patterns.append(pattern)

        except Exception as e:
            logger.error(f"Error learning patterns: {e}")

    def _optimize_strategies(self, domain: str) -> None:
        """Optimize scraping strategies for a domain based on accumulated data."""
        try:
            if domain not in self.domain_intelligence:
                return

            intel = self.domain_intelligence[domain]

            # Only optimize if we have enough data
            if intel.total_attempts < self.min_sessions_for_intelligence:
                return

            # Get recent sessions for this domain
            recent_sessions = [
                s for s in self.session_history[-50:] if s.domain == domain
            ]

            if not recent_sessions:
                return

            # Analyze successful vs failed sessions
            successful = [s for s in recent_sessions if s.success]
            failed = [s for s in recent_sessions if not s.success]

            # Update best strategies
            strategies = []

            if successful:
                avg_delay = statistics.mean(s.delay_used for s in successful)
                common_ua = max(
                    set(s.user_agent for s in successful),
                    key=lambda x: sum(1 for s in successful if s.user_agent == x),
                )

                strategies.append(f"optimal_delay:{avg_delay:.2f}")
                strategies.append(f"preferred_ua:{hash(common_ua) % 1000}")

            intel.best_strategies = strategies[:5]  # Keep top 5

        except Exception as e:
            logger.error(f"Error optimizing strategies: {e}")

    def _extract_url_pattern(self, url: str) -> str:
        """Extract a generalized pattern from a URL."""
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)

            # Create a pattern by removing specific IDs and values
            path_parts = parsed.path.split("/")
            generalized_parts = []

            for part in path_parts:
                if part.isdigit():
                    generalized_parts.append("{id}")
                elif len(part) > 20:  # Likely a hash or token
                    generalized_parts.append("{token}")
                else:
                    generalized_parts.append(part)

            return f"{parsed.netloc}{'/' + '/'.join(generalized_parts) if generalized_parts else ''}"

        except Exception as e:
            logger.debug(f"Error extracting URL pattern: {e}")
            return url

    def _get_default_adaptive_strategy(self, url: str) -> Dict[str, Any]:
        """Get default adaptive strategy for unknown domains."""
        return {
            "delay": 1.0,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "max_retries": 3,
            "timeout": 15,
            "expected_patterns": [],
            "avoid_patterns": [],
            "confidence": 0.0,
        }

    def _calculate_learning_efficiency(self) -> float:
        """Calculate how efficiently the brain is learning."""
        try:
            if len(self.session_history) < 10:
                return 0.0

            # Compare recent success rate vs overall
            recent_sessions = self.session_history[-20:]
            overall_sessions = self.session_history

            recent_success = sum(1 for s in recent_sessions if s.success) / len(
                recent_sessions
            )
            overall_success = sum(1 for s in overall_sessions if s.success) / len(
                overall_sessions
            )

            # Efficiency is how much better we're doing recently
            return max(0.0, (recent_success - overall_success) + 0.5)

        except Exception as e:
            logger.error(f"Error calculating learning efficiency: {e}")
            return 0.0

    def _load_intelligence(self) -> None:
        """Load previously saved intelligence from disk."""
        try:
            if self.data_path.exists():
                with open(self.data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Load domain intelligence
                for domain_data in data.get("domains", []):
                    domain = domain_data["domain"]
                    self.domain_intelligence[domain] = DomainIntelligence(**domain_data)

                # Load pattern library
                self.pattern_library = data.get("patterns", {})

                logger.info(
                    f"Loaded intelligence for {len(self.domain_intelligence)} domains"
                )

        except Exception as e:
            logger.warning(f"Could not load previous intelligence: {e}")

    def _save_intelligence(self) -> None:
        """Save current intelligence to disk."""
        try:
            data = {
                "domains": [
                    asdict(intel) for intel in self.domain_intelligence.values()
                ],
                "patterns": self.pattern_library,
                "last_save": time.time(),
            }

            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Error saving intelligence: {e}")


# Global brain instance
_global_brain: Optional[AutonomousLearningBrain] = None


def get_learning_brain() -> AutonomousLearningBrain:
    """Get the global learning brain instance."""
    global _global_brain
    if _global_brain is None:
        _global_brain = AutonomousLearningBrain()
    return _global_brain


def create_session_from_result(
    result,
    response_time: float = 0.0,
    retry_count: int = 0,
    user_agent: str = "",
    delay_used: float = 1.0,
) -> ScrapingSession:
    """Create a ScrapingSession from a ScrapeResult for learning."""
    try:
        from urllib.parse import urlparse

        domain = urlparse(result.url).netloc

        # Calculate extraction quality based on content
        quality = 0.0
        if result.status == "SUCCESS":
            quality = 0.8
            if result.content_text and len(result.content_text) > 100:
                quality += 0.1
            if result.extracted_data:
                quality += 0.1

        # Extract patterns from successful results
        patterns = []
        if result.status == "SUCCESS" and result.content_text:
            # Simple pattern extraction
            if "price" in result.content_text.lower():
                patterns.append("has_price")
            if "product" in result.content_text.lower():
                patterns.append("has_product")
            if "article" in result.content_text.lower():
                patterns.append("has_article")

        # Extract errors from failed results
        errors = []
        if result.status != "SUCCESS":
            errors.append(f"status_{result.status}")
            if hasattr(result, "error_message") and result.error_message:
                errors.append(result.error_message)

        return ScrapingSession(
            domain=domain,
            url=result.url,
            timestamp=time.time(),
            success=(result.status == "SUCCESS"),
            response_time=response_time,
            content_length=len(result.content_text or ""),
            status_code=getattr(result, "status_code", 200),
            retry_count=retry_count,
            user_agent=user_agent,
            delay_used=delay_used,
            extraction_quality=quality,
            patterns_found=patterns,
            errors=errors,
        )

    except Exception as e:
        logger.error(f"Error creating session from result: {e}")
        # Return a minimal session
        return ScrapingSession(
            domain="unknown",
            url=result.url if hasattr(result, "url") else "unknown",
            timestamp=time.time(),
            success=False,
            response_time=0.0,
            content_length=0,
            status_code=500,
            retry_count=0,
            user_agent="",
            delay_used=1.0,
            extraction_quality=0.0,
            patterns_found=[],
            errors=["session_creation_error"],
        )
