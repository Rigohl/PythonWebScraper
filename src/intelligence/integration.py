"""
Intelligence Integration Layer

This module integrates the autonomous learning brain with the existing scraper
infrastructure, providing seamless intelligence enhancement without breaking
existing functionality. Now supports both Hybrid Brain and legacy systems.
"""

import logging
import time
from functools import wraps
from typing import Any, Dict, Optional

# Support both hybrid and legacy brain systems
try:
    from .hybrid_brain import HybridBrain

    HYBRID_AVAILABLE = True
except ImportError:
    HYBRID_AVAILABLE = False
    # Define a placeholder for type hints
    HybridBrain = Any

from .autonomous_brain import create_session_from_result, get_learning_brain

logger = logging.getLogger(__name__)


class IntelligenceIntegration:
    """
    Integration layer that adds intelligence to the scraper without modifying core code.

    This class acts as a bridge between the learning brain and the scraper components,
    providing intelligent enhancements while maintaining backward compatibility.

    Now supports HybridBrain (IA-A + IA-B combined) for enhanced intelligence.
    """

    def __init__(self, brain: Optional[Any] = None):
        # Initialize brain system
        if brain is not None:
            self.brain = brain
            self.brain_type = (
                "hybrid" if hasattr(brain, "simple_brain") else "autonomous"
            )
        else:
            # Fallback to autonomous brain
            self.brain = get_learning_brain()
            self.brain_type = "autonomous"

        self.enabled = True
        self.performance_tracking = {}

        logger.info(
            f"🧠 Intelligence integration initialized with {self.brain_type} brain"
        )

    def enhance_configuration(self, domain: str) -> Dict[str, Any]:
        """
        Enhance configuration for a domain using available intelligence.
        Compatible with both hybrid and autonomous brain systems.
        """
        if not self.enabled:
            return {}

        try:
            if self.brain_type == "hybrid":
                # Use hybrid brain optimization
                return self.brain.get_optimization_config(domain)
            else:
                # Use autonomous brain optimization
                strategy = self.brain.get_optimal_strategy(domain, f"https://{domain}")
                if strategy:
                    return {
                        "delay": strategy.request_delay,
                        "user_agent_pattern": strategy.user_agent_pattern,
                        "retry_count": strategy.retry_strategy.max_retries,
                        "timeout": strategy.timeout,
                    }
                return {}

        except Exception as e:
            logger.error(f"Intelligence configuration error for {domain}: {e}")
            return {}

    def enhance_scraper_config(
        self, url: str, base_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhance scraper configuration with learned intelligence.

        Takes a base configuration and enhances it with AI-learned optimizations.
        """
        if not self.enabled:
            return base_config

        try:
            from urllib.parse import urlparse

            domain = urlparse(url).netloc

            # Get domain-specific optimizations
            optimizations = self.enhance_configuration(domain)

            # Merge with base config, giving priority to learned strategies
            enhanced_config = base_config.copy()

            # Apply intelligent enhancements based on optimizations
            if optimizations:
                # Apply optimization with confidence check (for legacy compatibility)
                confidence = optimizations.get("predicted_success_rate", 0.5)
                if confidence > 0.3:  # Only apply if confident
                    enhanced_config.update(
                        {
                            "delay": optimizations.get(
                                "delay", base_config.get("delay", 1.0)
                            ),
                            "user_agent": optimizations.get(
                                "user_agent_pattern", base_config.get("user_agent")
                            ),
                            "max_retries": optimizations.get(
                                "retry_count", base_config.get("max_retries", 3)
                            ),
                            "timeout": optimizations.get(
                                "timeout", base_config.get("timeout", 15)
                            ),
                        }
                    )

                    # Add intelligence metadata
                    enhanced_config["_intelligence"] = {
                        "brain_confidence": confidence,
                        "brain_type": self.brain_type,
                        "learned_strategy": True,
                        "optimization_source": (
                            "hybrid" if self.brain_type == "hybrid" else "autonomous"
                        ),
                    }

                    logger.info(
                        f"Enhanced config for {domain} with {confidence:.2f} confidence ({self.brain_type} brain)"
                    )

            return enhanced_config

        except Exception as e:
            logger.error(f"Error enhancing scraper config: {e}")
            return base_config

    def learn_from_scrape_result(
        self, result, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Learn from a completed scrape result.

        This should be called after each scraping operation to feed data to the brain.
        Compatible with both hybrid and autonomous brain systems.
        """
        if not self.enabled:
            return

        try:
            if self.brain_type == "hybrid":
                # Use hybrid brain learning
                self.brain.record_scraping_result(result, context)
            else:
                # Use autonomous brain learning (legacy mode)
                # Extract context information
                response_time = context.get("response_time", 0.0) if context else 0.0
                retry_count = context.get("retry_count", 0) if context else 0
                user_agent = context.get("user_agent", "") if context else ""
            delay_used = context.get("delay_used", 1.0) if context else 1.0

            # Create learning session
            session = create_session_from_result(
                result, response_time, retry_count, user_agent, delay_used
            )

            # Feed to brain
            self.brain.learn_from_session(session)

            # Track our own performance
            self._track_performance(session)

        except Exception as e:
            logger.error(f"Error learning from scrape result: {e}")

    def get_intelligence_report(self) -> Dict[str, Any]:
        """Get a comprehensive intelligence report."""
        try:
            summary = self.brain.get_intelligence_summary()

            # Add integration-specific metrics
            summary.update(
                {
                    "integration_status": "enabled" if self.enabled else "disabled",
                    "performance_improvements": self._calculate_improvements(),
                    "recommendation": self._get_recommendation(),
                }
            )

            return summary

        except Exception as e:
            logger.error(f"Error generating intelligence report: {e}")
            return {"error": str(e)}

    def enable_intelligence(self) -> None:
        """Enable intelligence features."""
        self.enabled = True
        logger.info("Intelligence features enabled")

    def disable_intelligence(self) -> None:
        """Disable intelligence features (fallback to base behavior)."""
        self.enabled = False
        logger.info("Intelligence features disabled")

    def _track_performance(self, session) -> None:
        """Track performance improvements from intelligence."""
        try:
            domain = session.domain
            if domain not in self.performance_tracking:
                self.performance_tracking[domain] = {
                    "sessions": [],
                    "baseline_success": 0.5,
                    "current_success": 0.5,
                }

            tracking = self.performance_tracking[domain]
            tracking["sessions"].append(
                {
                    "timestamp": session.timestamp,
                    "success": session.success,
                    "response_time": session.response_time,
                }
            )

            # Keep only recent sessions (last 50)
            tracking["sessions"] = tracking["sessions"][-50:]

            # Update success rate
            recent_success = sum(1 for s in tracking["sessions"] if s["success"])
            tracking["current_success"] = recent_success / len(tracking["sessions"])

        except Exception as e:
            logger.error(f"Error tracking performance: {e}")

    def _calculate_improvements(self) -> Dict[str, float]:
        """Calculate performance improvements from intelligence."""
        try:
            improvements = {}

            for domain, tracking in self.performance_tracking.items():
                if len(tracking["sessions"]) >= 10:
                    improvement = (
                        tracking["current_success"] - tracking["baseline_success"]
                    )
                    improvements[domain] = improvement

            if improvements:
                avg_improvement = sum(improvements.values()) / len(improvements)
                return {
                    "average_improvement": avg_improvement,
                    "domains_improved": len(
                        [v for v in improvements.values() if v > 0]
                    ),
                    "total_domains": len(improvements),
                }

            return {
                "average_improvement": 0.0,
                "domains_improved": 0,
                "total_domains": 0,
            }

        except Exception as e:
            logger.error(f"Error calculating improvements: {e}")
            return {}

    def _get_recommendation(self) -> str:
        """Get recommendation based on current intelligence state."""
        try:
            summary = self.brain.get_intelligence_summary()

            if summary.get("total_sessions", 0) < 50:
                return "Continue scraping to build intelligence. Need more data for optimal performance."

            efficiency = summary.get("learning_efficiency", 0)
            if efficiency > 0.8:
                return "Intelligence system is performing excellently. Scraper is highly optimized."
            elif efficiency > 0.5:
                return "Intelligence system is working well. Gradual improvements detected."
            elif efficiency > 0.2:
                return "Intelligence system is learning. Some improvements detected."
            else:
                return "Intelligence system needs more diverse data. Try scraping different domains."

        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return "Intelligence system status unknown."

    def get_intelligence_metrics(self) -> dict:
        """Obtiene métricas actuales del sistema de inteligencia para mostrar en TUI."""
        try:
            if not self.brain:
                return {
                    "domains_learned": 0,
                    "total_sessions": 0,
                    "avg_success_rate": 0.0,
                    "patterns_identified": 0,
                    "strategies_optimized": 0,
                    "last_learning": "Sistema no inicializado",
                }

            if self.brain_type == "hybrid":
                # Usar métricas del sistema híbrido
                hybrid_stats = self.brain.get_comprehensive_stats()

                return {
                    "domains_learned": len(hybrid_stats["simple_brain"]["domains"]),
                    "total_sessions": hybrid_stats["autonomous_brain"][
                        "learning_sessions"
                    ],
                    "avg_success_rate": self._calculate_avg_success_rate(
                        hybrid_stats["simple_brain"]["domains"]
                    ),
                    "patterns_identified": hybrid_stats["autonomous_brain"][
                        "total_patterns"
                    ],
                    "strategies_optimized": hybrid_stats["autonomous_brain"][
                        "strategies_optimized"
                    ],
                    "last_learning": self._get_last_learning_time(hybrid_stats),
                    "brain_type": "hybrid",
                    "top_domains": [
                        d["domain"]
                        for d in hybrid_stats.get("top_performing_domains", [])[:3]
                    ],
                    "learning_insights": hybrid_stats.get("learning_insights", []),
                }
            else:
                # Usar métricas del sistema autónomo (legacy)
                # Obtener estadísticas del cerebro de aprendizaje
                brain_stats = self.brain.get_domain_intelligence()
                total_domains = len(brain_stats)
                total_sessions = sum(
                    stats.total_sessions for stats in brain_stats.values()
                )

                # Calcular tasa de éxito promedio
                success_rates = []
                patterns_count = 0
                strategies_count = 0

                for domain_stats in brain_stats.values():
                    if domain_stats.total_sessions > 0:
                        success_rate = (
                            domain_stats.success_count / domain_stats.total_sessions
                        )
                        success_rates.append(success_rate)
                    patterns_count += len(domain_stats.common_patterns)
                    strategies_count += len(domain_stats.optimal_strategies)

                avg_success_rate = (
                    sum(success_rates) / len(success_rates) if success_rates else 0.0
                )

                # Obtener información de la última sesión de seguimiento de rendimiento
                last_learning = "Nunca"
                latest_time = 0
                for tracking in self.performance_tracking.values():
                    if tracking["sessions"]:
                        last_session_time = max(
                            s["timestamp"] for s in tracking["sessions"]
                        )
                        if last_session_time > latest_time:
                            latest_time = last_session_time

                if latest_time > 0:
                    import datetime

                    last_learning = datetime.datetime.fromtimestamp(
                        latest_time
                    ).strftime("%H:%M:%S")

                return {
                    "domains_learned": total_domains,
                    "total_sessions": total_sessions,
                    "avg_success_rate": avg_success_rate,
                    "patterns_identified": patterns_count,
                    "strategies_optimized": strategies_count,
                    "last_learning": last_learning,
                    "brain_type": "autonomous",
                }
        except Exception as e:
            logger.error(f"Error getting intelligence metrics: {e}")
            return {
                "domains_learned": 0,
                "total_sessions": 0,
                "avg_success_rate": 0.0,
                "patterns_identified": 0,
                "strategies_optimized": 0,
                "last_learning": f"Error: {str(e)}",
            }

    def _calculate_avg_success_rate(self, domains_data: dict) -> float:
        """Calcula la tasa de éxito promedio de los dominios del Brain simple"""
        if not domains_data:
            return 0.0

        success_rates = []
        for domain_stats in domains_data.values():
            visits = domain_stats.get("visits", 0)
            success = domain_stats.get("success", 0)
            if visits > 0:
                success_rates.append(success / visits)

        return sum(success_rates) / len(success_rates) if success_rates else 0.0

    def _get_last_learning_time(self, hybrid_stats: dict) -> str:
        """Obtiene el tiempo del último aprendizaje del sistema híbrido"""
        try:
            recent_events = hybrid_stats.get("simple_brain", {}).get(
                "recent_events", []
            )
            if recent_events:
                # El último evento del Brain simple
                return recent_events[-1].get("timestamp", "Desconocido")
            return "Nunca"
        except Exception:
            return "Error al obtener tiempo"


# Global integration instance
_global_integration: Optional[IntelligenceIntegration] = None


def get_intelligence_integration() -> IntelligenceIntegration:
    """Get the global intelligence integration instance."""
    global _global_integration
    if _global_integration is None:
        _global_integration = IntelligenceIntegration()
    return _global_integration


def intelligent_scraper_decorator(scraper_func):
    """
    Decorator that adds intelligence to any scraper function.

    Usage:
    @intelligent_scraper_decorator
    def my_scraper_function(url, config):
        # ... scraping logic ...
        return result
    """

    @wraps(scraper_func)
    def wrapper(url, config=None, *args, **kwargs):
        integration = get_intelligence_integration()

        # Enhance configuration with intelligence
        if config is None:
            config = {}

        start_time = time.time()
        enhanced_config = integration.enhance_scraper_config(url, config)

        try:
            # Call original scraper function
            result = scraper_func(url, enhanced_config, *args, **kwargs)

            # Prepare context for learning
            context = {
                "response_time": time.time() - start_time,
                "retry_count": enhanced_config.get("_retry_count", 0),
                "user_agent": enhanced_config.get("user_agent", ""),
                "delay_used": enhanced_config.get("delay", 1.0),
            }

            # Learn from result
            integration.learn_from_scrape_result(result, context)

            return result

        except Exception as e:
            # Learn from failures too
            class FailureResult:
                def __init__(self, url, error):
                    self.url = url
                    self.status = "FAILED"
                    self.content_text = ""
                    self.extracted_data = None
                    self.error_message = str(error)

            failure_result = FailureResult(url, e)
            context = {
                "response_time": time.time() - start_time,
                "retry_count": enhanced_config.get("_retry_count", 0),
                "user_agent": enhanced_config.get("user_agent", ""),
                "delay_used": enhanced_config.get("delay", 1.0),
            }

            integration.learn_from_scrape_result(failure_result, context)
            raise

    return wrapper
