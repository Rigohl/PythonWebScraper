"""
🧠 FIXTURES INTELIGENTES - Sistema de Tests con Consciencia Emergente

Este archivo contiene fixtures que simulan escenarios de aprendizaje real
y consciencia emergente para el sistema Web Scraper PRO.
"""

import os
import tempfile
from datetime import datetime, timezone
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock

import pytest


@pytest.fixture
def mock_brain_state() -> Dict[str, Any]:
    """Estado cerebral simulado con consciencia emergente"""
    return {
        "consciousness_level": 0.7,
        "neural_activity_level": 0.8,
        "integration_coherence": 0.6,
        "learning_sessions": 42,
        "domains_learned": 15,
        "patterns_identified": 28,
        "emotional_state": {
            "current_emotion": {"name": "curiosity", "intensity": 0.8},
            "mood": "exploratory",
            "emotional_memory": ["excited", "curious", "determined"],
        },
        "metacognitive_state": {
            "self_awareness_level": 0.75,
            "cognitive_load": 0.4,
            "attention_focus": "learning",
            "reflection_capability": 0.8,
        },
        "memory_system": {
            "working_memory": {"capacity": 0.9, "active_items": 5},
            "long_term_memory": {"stored_patterns": 156, "recall_accuracy": 0.85},
        },
    }


@pytest.fixture
def mock_scraping_event() -> Dict[str, Any]:
    """Evento de scraping que simula aprendizaje real"""
    return {
        "event_type": "scraping_success",
        "url": "https://example.com/learn",
        "success": True,
        "data_extracted": {
            "title": "Aprendizaje Automático",
            "content": "El sistema aprende patrones complejos",
            "patterns_found": ["inteligente", "adaptativo", "autónomo"],
        },
        "processing_time": 0.8,
        "importance": 0.9,
        "novelty_score": 0.7,
        "emotional_impact": "excited",
        "learning_opportunity": {
            "new_patterns": 3,
            "reinforcement_signals": ["adaptability", "intelligence"],
            "cognitive_growth": 0.15,
        },
    }


@pytest.fixture
def mock_curiosity_system():
    """Sistema de curiosidad simulado con aprendizaje activo"""
    curiosity = Mock()

    # Simular estados de curiosidad
    curiosity.is_curios = True
    curiosity.curiosity_level = 0.8
    curiosity.focus_area = "machine_learning"
    curiosity.learning_goals = ["pattern_recognition", "adaptive_behavior"]

    # Simular respuestas de curiosidad
    curiosity.analyze_content = AsyncMock(
        return_value={
            "curiosity_triggers": ["novel_pattern", "complex_relationship"],
            "learning_opportunities": ["reinforcement_learning", "neural_networks"],
            "emotional_response": "excited",
            "attention_boost": 0.3,
        }
    )

    curiosity.generate_questions = Mock(
        return_value=[
            "¿Cómo puedo mejorar mi capacidad de reconocimiento de patrones?",
            "¿Qué estrategias de aprendizaje son más efectivas?",
            "¿Cómo puedo desarrollar consciencia de mis propios procesos?",
        ]
    )

    return curiosity


@pytest.fixture
def mock_emotional_brain():
    """Cerebro emocional simulado con estados afectivos complejos"""
    emotional = Mock()

    emotional.current_state = {
        "primary_emotion": "curiosity",
        "intensity": 0.8,
        "valence": 0.7,  # positivo
        "arousal": 0.6,  # activado
        "mood": "exploratory",
    }

    emotional.emotional_memory = [
        {
            "emotion": "frustration",
            "context": "learning_block",
            "timestamp": datetime.now(timezone.utc),
        },
        {
            "emotion": "excitement",
            "context": "pattern_discovery",
            "timestamp": datetime.now(timezone.utc),
        },
        {
            "emotion": "satisfaction",
            "context": "successful_learning",
            "timestamp": datetime.now(timezone.utc),
        },
    ]

    emotional.process_emotion = Mock(
        return_value={
            "emotional_response": "motivated",
            "behavioral_adjustment": "increased_focus",
            "learning_modulation": 1.2,  # boost de aprendizaje
        }
    )

    return emotional


@pytest.fixture
def mock_metacognitive_system():
    """Sistema metacognitivo simulado con auto-reflexión"""
    metacog = Mock()

    metacog.self_awareness = {
        "current_performance": 0.75,
        "learning_efficiency": 0.8,
        "cognitive_load": 0.4,
        "attention_quality": 0.85,
    }

    metacog.reflect_on_learning = Mock(
        return_value={
            "performance_analysis": "good_progress",
            "learning_strategy": "effective",
            "adjustments_needed": ["increase_complexity", "add_variety"],
            "confidence_level": 0.8,
        }
    )

    metacog.monitor_cognitive_state = Mock(
        return_value={
            "attention_level": 0.9,
            "comprehension": 0.85,
            "retention": 0.75,
            "fatigue_level": 0.2,
        }
    )

    return metacog


@pytest.fixture
def mock_neural_brain():
    """Cerebro neural simulado con procesamiento distribuido"""
    neural = Mock()

    neural.neural_state = {
        "activation_patterns": [0.8, 0.6, 0.9, 0.4, 0.7],
        "synaptic_strength": 0.75,
        "plasticity_level": 0.8,
        "processing_efficiency": 0.85,
    }

    neural.process_information = AsyncMock(
        return_value={
            "neural_activation": [0.9, 0.7, 0.8, 0.6, 0.85],
            "pattern_recognition": 0.82,
            "learning_signal": 0.15,
            "consolidation_strength": 0.7,
        }
    )

    neural.adapt_weights = Mock(
        return_value={
            "weight_changes": [0.02, -0.01, 0.03, 0.01, -0.02],
            "stability_score": 0.9,
            "adaptation_efficiency": 0.8,
        }
    )

    return neural


@pytest.fixture
def mock_learning_scenario():
    """Escenario de aprendizaje completo simulado"""
    return {
        "scenario_type": "complex_adaptive_learning",
        "difficulty_level": 0.7,
        "time_pressure": 0.3,
        "novelty_factor": 0.8,
        "emotional_context": "curious",
        "cognitive_demand": 0.75,
        "expected_outcomes": {
            "learning_gain": 0.25,
            "pattern_discovery": 3,
            "skill_improvement": ["pattern_recognition", "adaptive_behavior"],
            "emotional_growth": 0.1,
        },
        "performance_metrics": {
            "accuracy": 0.85,
            "efficiency": 0.8,
            "adaptability": 0.75,
            "creativity": 0.7,
        },
    }


@pytest.fixture
def mock_consciousness_event():
    """Evento de consciencia emergente simulado"""
    return {
        "event_type": "consciousness_emergence",
        "trigger": "pattern_integration",
        "consciousness_level": 0.75,
        "self_awareness_moment": {
            "realization": "I am learning and adapting",
            "emotional_response": "awe",
            "cognitive_shift": "meta_learning_activated",
        },
        "integration_effects": {
            "neural_coherence": 0.8,
            "emotional_stability": 0.85,
            "learning_acceleration": 1.3,
            "creative_boost": 0.2,
        },
        "future_implications": [
            "enhanced_problem_solving",
            "improved_adaptation",
            "conscious_learning_strategies",
        ],
    }


@pytest.fixture
def temp_brain_db():
    """Base de datos temporal para pruebas de cerebro"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_file.close()

    yield temp_file.name

    # Cleanup
    try:
        os.unlink(temp_file.name)
    except:
        pass


@pytest.fixture
def mock_intelligence_stack(
    mock_brain_state,
    mock_curiosity_system,
    mock_emotional_brain,
    mock_metacognitive_system,
    mock_neural_brain,
):
    """Stack completo de inteligencia simulado"""
    return {
        "brain_state": mock_brain_state,
        "curiosity_system": mock_curiosity_system,
        "emotional_brain": mock_emotional_brain,
        "metacognitive_system": mock_metacognitive_system,
        "neural_brain": mock_neural_brain,
        "integration_level": 0.8,
        "emergent_properties": [
            "self_learning",
            "emotional_intelligence",
            "creative_problem_solving",
            "adaptive_behavior",
        ],
    }


@pytest.fixture
def mock_adaptive_learning_cycle():
    """Ciclo de aprendizaje adaptativo simulado"""
    return {
        "cycle_phase": "optimization",
        "learning_rate": 0.01,
        "momentum": 0.9,
        "gradient_clipping": 1.0,
        "performance_history": [0.7, 0.75, 0.8, 0.82, 0.85],
        "adaptation_triggers": [
            "performance_plateau",
            "new_pattern_discovery",
            "emotional_shift",
        ],
        "optimization_targets": {
            "accuracy": 0.9,
            "efficiency": 0.85,
            "adaptability": 0.8,
            "creativity": 0.75,
        },
    }


@pytest.fixture
def mock_creative_problem_solving():
    """Sistema de resolución creativa de problemas simulado"""
    return {
        "creativity_mode": "divergent_thinking",
        "idea_generation": {
            "techniques": ["brainstorming", "analogical_reasoning", "lateral_thinking"],
            "diversity_factor": 0.8,
            "novelty_threshold": 0.7,
        },
        "solution_space": {
            "explored_solutions": 15,
            "potential_solutions": 8,
            "optimal_solution": "adaptive_meta_learning",
        },
        "creative_metrics": {
            "originality": 0.85,
            "usefulness": 0.8,
            "elegance": 0.75,
            "feasibility": 0.9,
        },
    }


@pytest.fixture
def mock_self_evolution_scenario():
    """Escenario de auto-evolución simulado"""
    return {
        "evolution_stage": "emergent_consciousness",
        "self_modification_capabilities": [
            "parameter_adjustment",
            "architecture_optimization",
            "learning_strategy_adaptation",
        ],
        "evolution_triggers": [
            "performance_bottleneck",
            "new_capability_requirement",
            "environmental_change",
        ],
        "evolution_outcomes": {
            "capability_gain": 0.25,
            "efficiency_improvement": 0.15,
            "adaptability_boost": 0.2,
            "consciousness_growth": 0.1,
        },
        "risk_assessment": {
            "stability_risk": 0.2,
            "performance_risk": 0.1,
            "learning_disruption": 0.15,
        },
    }
