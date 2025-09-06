"""
Intelligence Module for Autonomous Web Scraper + Hybrid Brain System

This module provides autonomous learning capabilities that make the scraper
more intelligent and adaptive over time, plus legacy compatibility.

Components:
- Brain (IA-A): Lightweight event tracking and domain heuristics
- AutonomousLearningBrain (IA-B): Deep learning patterns and strategy optimization
- HybridBrain: Unified system combining both IA-A and IA-B intelligence
- IntelligenceIntegration: Integration layer with existing scraper
- Legacy components: LLMExtractor, RLAgent
"""


# Legacy imports for backward compatibility (use lazy imports to avoid heavy deps at import time)
def _lazy_import(name: str, package: str):
    """Import a symbol on first access and cache it in module globals.

    Usage: call _lazy_import('RLAgent', '..rl_agent') to import when needed.
    """
    if name in globals() and globals()[name] is not None:
        return globals()[name]
    try:
        module = __import__(package, fromlist=[name])
        obj = getattr(module, name)
        globals()[name] = obj
        return obj
    except Exception:
        globals()[name] = None
        return None


def get_LLMExtractor():
    """Return the LLMExtractor class or None if not available."""
    return _lazy_import("LLMExtractor", "..llm_extractor")


def get_RLAgent():
    """Return the RLAgent class or None if not available."""
    return _lazy_import("RLAgent", "..rl_agent")


# Backwards-compatible proxies (the tests or callers can call get_LLMExtractor()/get_RLAgent()
# or import the names and check for None). We intentionally do NOT import heavy libs here.
LLMExtractor = None
RLAgent = None

# New autonomous intelligence components
try:
    # IA-A Brain system
    pass

    # IA-B Autonomous Learning system

    # Hybrid system combining IA-A + IA-B
    from .hybrid_brain import get_hybrid_brain

    # Integration layer (updated to use HybridBrain)
    from .integration import IntelligenceIntegration

    # Knowledge and autonomous learning systems
    # Singleton function for hybrid integration
    def get_intelligence_integration() -> IntelligenceIntegration:
        """Obtiene la instancia singleton de IntelligenceIntegration con HybridBrain"""
        global _integration_instance
        if "_integration_instance" not in globals():
            # Usar el HybridBrain en lugar del AutonomousLearningBrain
            hybrid_brain = get_hybrid_brain()
            globals()["_integration_instance"] = IntelligenceIntegration(
                brain=hybrid_brain
            )
        return globals()["_integration_instance"]

    # All exports including new intelligence
    __all__ = [
        # Legacy components
        "LLMExtractor",
        "RLAgent",
        # IA-A Brain components
        "Brain",
        "ExperienceEvent",
        # IA-B Autonomous Learning components
        "AutonomousLearningBrain",
        "ScrapingSession",
        "DomainIntelligence",
        "get_learning_brain",
        "create_session_from_result",
        # Hybrid system (IA-A + IA-B)
        "HybridBrain",
        "get_hybrid_brain",
        # Integration layer
        "IntelligenceIntegration",
        "get_intelligence_integration",
        "intelligent_scraper_decorator",
        # Knowledge and learning systems
        "KnowledgeStore",
        "KnowledgeSeeder",
        "AutonomousPatchGenerator",
        "NeuralBrain",
        "AdvancedReasoningSystem",
        "AdvancedMemorySystem",
        "EmotionalBrain",
        "MetacognitiveBrain",
    ]

except ImportError as e:
    # Print the specific error for debugging
    print(f"Import error in intelligence module: {e}")
    # Fallback if new components fail to import
    __all__ = ["LLMExtractor", "RLAgent"]

__version__ = "2.0.0"  # Bumped for hybrid system
