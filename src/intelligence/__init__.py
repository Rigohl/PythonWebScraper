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

# Legacy imports for backward compatibility
from ..llm_extractor import LLMExtractor
from ..rl_agent import RLAgent

# New autonomous intelligence components
try:
    # IA-A Brain system
    from .brain import Brain, ExperienceEvent

    # IA-B Autonomous Learning system
    from .autonomous_brain import (
        AutonomousLearningBrain,
        ScrapingSession,
        DomainIntelligence,
        get_learning_brain,
        create_session_from_result
    )

    # Hybrid system combining IA-A + IA-B
    from .hybrid_brain import HybridBrain, get_hybrid_brain

    # Integration layer (updated to use HybridBrain)
    from .integration import (
        IntelligenceIntegration,
        intelligent_scraper_decorator
    )

    # Knowledge and autonomous learning systems
    from .knowledge_store import KnowledgeStore
    
    from .neural_brain import NeuralBrain
    from .advanced_reasoning import AdvancedReasoningSystem
    from .advanced_memory import AdvancedMemorySystem
    from .emotional_brain import EmotionalBrain
    from .metacognitive_brain import MetacognitiveBrain

    # Singleton function for hybrid integration
    def get_intelligence_integration() -> IntelligenceIntegration:
        """Obtiene la instancia singleton de IntelligenceIntegration con HybridBrain"""
        global _integration_instance
        if '_integration_instance' not in globals():
            # Usar el HybridBrain en lugar del AutonomousLearningBrain
            hybrid_brain = get_hybrid_brain()
            globals()['_integration_instance'] = IntelligenceIntegration(brain=hybrid_brain)
        return globals()['_integration_instance']

    # All exports including new intelligence
    __all__ = [
        # Legacy components
        "LLMExtractor", "RLAgent",
        # IA-A Brain components
        "Brain", "ExperienceEvent",
        # IA-B Autonomous Learning components
        'AutonomousLearningBrain',
        'ScrapingSession',
        'DomainIntelligence',
        'get_learning_brain',
        'create_session_from_result',
        # Hybrid system (IA-A + IA-B)
        'HybridBrain',
        'get_hybrid_brain',
        # Integration layer
        'IntelligenceIntegration',
        'get_intelligence_integration',
        'intelligent_scraper_decorator',
        # Knowledge and learning systems
        'KnowledgeStore',
        'KnowledgeSeeder',
        'AutonomousPatchGenerator',
        'NeuralBrain',
        'AdvancedReasoningSystem',
        'AdvancedMemorySystem',
        'EmotionalBrain',
        'MetacognitiveBrain'
    ]

except ImportError as e:
    # Fallback if new components fail to import
    __all__ = ["LLMExtractor", "RLAgent"]

__version__ = "2.0.0"  # Bumped for hybrid system
