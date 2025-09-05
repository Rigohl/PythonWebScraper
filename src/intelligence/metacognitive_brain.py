"""
Metacognitive Brain System - Sistema de Metacognición

Este módulo implementa capacidades metacognitivas inspiradas en psicología cognitiva:
- Meta-memoria: conocimiento sobre la propia memoria
- Meta-razonamiento: monitoreo y control de procesos de razonamiento
- Meta-aprendizaje: aprender cómo aprender mejor
- Auto-reflexión: capacidad de introspección y autoconocimiento
- Teoría de la Mente: modelado de estados mentales propios y ajenos
- Consciencia de la consciencia: awareness de los propios procesos conscientes
- Regulación metacognitiva: control de estrategias cognitivas
- Confianza metacognitiva: calibración de la confianza en el propio conocimiento
"""

import json
import logging
import math
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set, Callable
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)

class MetacognitiveProcess(Enum):
    MONITORING = "monitoring"           # Monitoreo de procesos cognitivos
    CONTROL = "control"                # Control de estrategias cognitivas
    EVALUATION = "evaluation"          # Evaluación de resultados
    PLANNING = "planning"              # Planificación de estrategias
    REFLECTION = "reflection"          # Reflexión sobre experiencias

class ConfidenceLevel(Enum):
    VERY_LOW = "very_low"              # 0.0-0.2
    LOW = "low"                        # 0.2-0.4
    MODERATE = "moderate"              # 0.4-0.6
    HIGH = "high"                      # 0.6-0.8
    VERY_HIGH = "very_high"            # 0.8-1.0

class CognitiveStrategy(Enum):
    SYSTEMATIC_SEARCH = "systematic_search"         # Búsqueda sistemática
    HEURISTIC_SEARCH = "heuristic_search"          # Búsqueda heurística
    ANALOGICAL_REASONING = "analogical_reasoning"   # Razonamiento analógico
    CASE_BASED_REASONING = "case_based_reasoning"   # Razonamiento basado en casos
    TRIAL_AND_ERROR = "trial_and_error"            # Ensayo y error
    DECOMPOSITION = "decomposition"                 # Descomposición de problemas
    ABSTRACTION = "abstraction"                     # Abstracción
    PATTERN_MATCHING = "pattern_matching"           # Reconocimiento de patrones

@dataclass
class MetacognitiveKnowledge:
    """Conocimiento metacognitivo sobre los propios procesos cognitivos"""

    # Meta-memoria: conocimiento sobre la propia memoria
    memory_strengths: Dict[str, float] = field(default_factory=dict)  # Fortalezas de memoria por dominio
    memory_weaknesses: Dict[str, float] = field(default_factory=dict)  # Debilidades de memoria
    forgetting_patterns: Dict[str, List[float]] = field(default_factory=dict)  # Patrones de olvido

    # Meta-razonamiento: conocimiento sobre el propio razonamiento
    reasoning_preferences: Dict[str, float] = field(default_factory=dict)  # Preferencias de razonamiento
    reasoning_biases: Dict[str, float] = field(default_factory=dict)  # Sesgos conocidos
    reasoning_accuracy: Dict[str, List[float]] = field(default_factory=dict)  # Precisión por tipo

    # Meta-aprendizaje: conocimiento sobre el propio aprendizaje
    learning_styles: Dict[str, float] = field(default_factory=dict)  # Estilos de aprendizaje
    optimal_conditions: Dict[str, Any] = field(default_factory=dict)  # Condiciones óptimas
    learning_curves: Dict[str, List[float]] = field(default_factory=dict)  # Curvas de aprendizaje

    # Auto-conocimiento general
    cognitive_capacity: Dict[str, float] = field(default_factory=dict)  # Capacidades cognitivas
    attention_patterns: Dict[str, float] = field(default_factory=dict)  # Patrones atencionales
    motivation_factors: Dict[str, float] = field(default_factory=dict)  # Factores motivacionales

    def update_memory_knowledge(self, domain: str, performance: float, task_type: str):
        """Actualiza conocimiento sobre memoria"""
        if domain not in self.memory_strengths:
            self.memory_strengths[domain] = 0.5

        # Actualizar con learning rate adaptativo
        learning_rate = 0.1
        self.memory_strengths[domain] += learning_rate * (performance - self.memory_strengths[domain])

        # Registrar patrones de olvido
        if domain not in self.forgetting_patterns:
            self.forgetting_patterns[domain] = []
        self.forgetting_patterns[domain].append(1 - performance)

        # Mantener solo últimos 20 registros
        if len(self.forgetting_patterns[domain]) > 20:
            self.forgetting_patterns[domain] = self.forgetting_patterns[domain][-20:]

    def update_reasoning_knowledge(self, reasoning_type: str, accuracy: float, confidence: float):
        """Actualiza conocimiento sobre razonamiento"""
        if reasoning_type not in self.reasoning_accuracy:
            self.reasoning_accuracy[reasoning_type] = []

        self.reasoning_accuracy[reasoning_type].append(accuracy)

        # Calcular calibración (qué tan bien calibrada está la confianza)
        if len(self.reasoning_accuracy[reasoning_type]) > 5:
            recent_accuracy = statistics.mean(self.reasoning_accuracy[reasoning_type][-5:])
            calibration_error = abs(confidence - recent_accuracy)

            # Actualizar preferencias basado en calibración
            if reasoning_type not in self.reasoning_preferences:
                self.reasoning_preferences[reasoning_type] = 0.5

            if calibration_error < 0.2:  # Bien calibrado
                self.reasoning_preferences[reasoning_type] = min(1.0,
                    self.reasoning_preferences[reasoning_type] + 0.05)
            else:  # Mal calibrado
                self.reasoning_preferences[reasoning_type] = max(0.1,
                    self.reasoning_preferences[reasoning_type] - 0.05)

    def update_learning_knowledge(self, domain: str, learning_rate: float, conditions: Dict[str, Any]):
        """Actualiza conocimiento sobre aprendizaje"""
        if domain not in self.learning_curves:
            self.learning_curves[domain] = []

        self.learning_curves[domain].append(learning_rate)

        # Analizar condiciones óptimas
        if domain not in self.optimal_conditions:
            self.optimal_conditions[domain] = conditions.copy()
        else:
            # Promediar condiciones que llevan a buen aprendizaje
            if learning_rate > 0.7:  # Buen aprendizaje
                for key, value in conditions.items():
                    if isinstance(value, (int, float)):
                        current = self.optimal_conditions[domain].get(key, value)
                        self.optimal_conditions[domain][key] = (current + value) / 2

@dataclass
class MetacognitiveMonitor:
    """Monitor de procesos cognitivos en tiempo real"""
    current_strategy: Optional[CognitiveStrategy] = None
    strategy_start_time: float = 0.0
    strategy_effectiveness: float = 0.5

    # Estado del monitoreo
    cognitive_load: float = 0.5  # Carga cognitiva actual (0-1)
    attention_focus: float = 0.8  # Nivel de foco atencional (0-1)
    processing_speed: float = 0.7  # Velocidad de procesamiento (0-1)

    # Métricas de proceso
    errors_detected: int = 0
    corrections_made: int = 0
    strategy_switches: int = 0

    # Historia de monitoreo
    monitoring_log: List[Dict[str, Any]] = field(default_factory=list)

    def start_monitoring(self, strategy: CognitiveStrategy, task_context: Dict[str, Any]):
        """Inicia monitoreo de una estrategia cognitiva"""
        self.current_strategy = strategy
        self.strategy_start_time = time.time()
        self.errors_detected = 0
        self.corrections_made = 0

        self.monitoring_log.append({
            "timestamp": self.strategy_start_time,
            "event": "strategy_started",
            "strategy": strategy.value,
            "context": task_context,
            "cognitive_load": self.cognitive_load,
            "attention_focus": self.attention_focus
        })

    def detect_cognitive_conflict(self, reasoning_outputs: List[Dict[str, Any]]) -> bool:
        """Detecta conflictos en procesos de razonamiento"""
        if len(reasoning_outputs) < 2:
            return False

        # Analizar consistencia entre outputs
        confidences = [output.get("confidence", 0.5) for output in reasoning_outputs]
        conclusions = [output.get("conclusion") for output in reasoning_outputs]

        # Conflict si hay baja confianza promedio
        avg_confidence = statistics.mean(confidences)
        if avg_confidence < 0.4:
            self.errors_detected += 1
            return True

        # Conflict si las conclusiones son muy diferentes
        if len(set(str(c) for c in conclusions)) > len(conclusions) * 0.7:
            self.errors_detected += 1
            return True

        return False

    def assess_strategy_effectiveness(self, performance_metrics: Dict[str, float]) -> float:
        """Evalúa efectividad de la estrategia actual"""
        if not self.current_strategy:
            return 0.5

        # Factores de efectividad
        accuracy = performance_metrics.get("accuracy", 0.5)
        speed = performance_metrics.get("speed", 0.5)
        confidence = performance_metrics.get("confidence", 0.5)

        # Penalizar por errores
        error_penalty = self.errors_detected * 0.1

        # Beneficio por correcciones
        correction_bonus = self.corrections_made * 0.05

        effectiveness = (accuracy * 0.5 + speed * 0.3 + confidence * 0.2) - error_penalty + correction_bonus
        self.strategy_effectiveness = max(0.0, min(1.0, effectiveness))

        return self.strategy_effectiveness

    def update_cognitive_load(self, task_complexity: float, time_pressure: float,
                            working_memory_usage: float):
        """Actualiza estimación de carga cognitiva"""
        # Modelo simple de carga cognitiva
        complexity_load = task_complexity * 0.4
        pressure_load = time_pressure * 0.3
        memory_load = working_memory_usage * 0.3

        new_load = complexity_load + pressure_load + memory_load

        # Suavizar cambios
        self.cognitive_load = self.cognitive_load * 0.7 + new_load * 0.3
        self.cognitive_load = max(0.0, min(1.0, self.cognitive_load))

        # Actualizar foco atencional inversamente relacionado con carga
        if self.cognitive_load > 0.8:
            self.attention_focus = max(0.3, self.attention_focus - 0.1)
        elif self.cognitive_load < 0.3:
            self.attention_focus = min(1.0, self.attention_focus + 0.05)

@dataclass
class MetacognitiveController:
    """Controlador de estrategias metacognitivas"""
    available_strategies: Dict[CognitiveStrategy, Dict[str, Any]] = field(default_factory=dict)
    strategy_success_history: Dict[CognitiveStrategy, List[float]] = field(default_factory=dict)
    strategy_preferences: Dict[CognitiveStrategy, float] = field(default_factory=dict)

    def __post_init__(self):
        """Inicializa estrategias disponibles"""
        self.available_strategies = {
            CognitiveStrategy.SYSTEMATIC_SEARCH: {
                "description": "Búsqueda exhaustiva y ordenada",
                "best_for": ["complex_problems", "high_accuracy_needed"],
                "cognitive_cost": 0.8,
                "time_cost": 0.9,
                "accuracy_potential": 0.9
            },
            CognitiveStrategy.HEURISTIC_SEARCH: {
                "description": "Búsqueda basada en heurísticas",
                "best_for": ["time_pressure", "familiar_problems"],
                "cognitive_cost": 0.4,
                "time_cost": 0.3,
                "accuracy_potential": 0.7
            },
            CognitiveStrategy.ANALOGICAL_REASONING: {
                "description": "Razonamiento por analogía",
                "best_for": ["novel_problems", "pattern_recognition"],
                "cognitive_cost": 0.6,
                "time_cost": 0.5,
                "accuracy_potential": 0.8
            },
            CognitiveStrategy.DECOMPOSITION: {
                "description": "Descomposición en subproblemas",
                "best_for": ["complex_problems", "systematic_approach"],
                "cognitive_cost": 0.7,
                "time_cost": 0.7,
                "accuracy_potential": 0.85
            }
        }

        # Inicializar preferencias neutras
        for strategy in self.available_strategies:
            self.strategy_preferences[strategy] = 0.5

    def select_strategy(self, task_context: Dict[str, Any],
                       cognitive_state: Dict[str, float]) -> CognitiveStrategy:
        """Selecciona estrategia óptima basada en contexto y estado"""

        task_type = task_context.get("type", "general")
        complexity = task_context.get("complexity", 0.5)
        time_pressure = task_context.get("time_pressure", 0.5)
        familiarity = task_context.get("familiarity", 0.5)

        cognitive_load = cognitive_state.get("cognitive_load", 0.5)
        attention_focus = cognitive_state.get("attention_focus", 0.8)

        strategy_scores = {}

        for strategy, properties in self.available_strategies.items():
            score = 0.0

            # Score base por preferencia histórica
            score += self.strategy_preferences.get(strategy, 0.5) * 0.3

            # Ajustar por contexto
            if complexity > 0.7 and strategy in [CognitiveStrategy.SYSTEMATIC_SEARCH,
                                                CognitiveStrategy.DECOMPOSITION]:
                score += 0.3

            if time_pressure > 0.7 and properties["time_cost"] < 0.5:
                score += 0.3

            if familiarity > 0.7 and strategy == CognitiveStrategy.HEURISTIC_SEARCH:
                score += 0.2

            if familiarity < 0.3 and strategy == CognitiveStrategy.ANALOGICAL_REASONING:
                score += 0.2

            # Ajustar por estado cognitivo
            if cognitive_load > 0.8 and properties["cognitive_cost"] > 0.7:
                score -= 0.4  # Evitar estrategias costosas cuando hay alta carga

            if attention_focus < 0.5 and strategy == CognitiveStrategy.SYSTEMATIC_SEARCH:
                score -= 0.3  # Evitar estrategias que requieren mucho foco

            # Bonus por éxito histórico
            if strategy in self.strategy_success_history:
                recent_success = statistics.mean(self.strategy_success_history[strategy][-5:])
                score += recent_success * 0.2

            strategy_scores[strategy] = max(0.0, score)

        # Seleccionar estrategia con mayor score
        best_strategy = max(strategy_scores.items(), key=lambda x: x[1])[0]

        return best_strategy

    def update_strategy_success(self, strategy: CognitiveStrategy, success_rate: float):
        """Actualiza historial de éxito de estrategia"""
        if strategy not in self.strategy_success_history:
            self.strategy_success_history[strategy] = []

        self.strategy_success_history[strategy].append(success_rate)

        # Mantener solo últimos 20 registros
        if len(self.strategy_success_history[strategy]) > 20:
            self.strategy_success_history[strategy] = self.strategy_success_history[strategy][-20:]

        # Actualizar preferencias
        if success_rate > 0.7:
            self.strategy_preferences[strategy] = min(1.0,
                self.strategy_preferences[strategy] + 0.05)
        elif success_rate < 0.3:
            self.strategy_preferences[strategy] = max(0.1,
                self.strategy_preferences[strategy] - 0.05)

    def should_switch_strategy(self, current_performance: Dict[str, float],
                             time_elapsed: float, target_performance: Dict[str, float]) -> bool:
        """Determina si debe cambiar de estrategia"""

        # Tiempo mínimo antes de considerar cambio
        if time_elapsed < 30:  # 30 segundos
            return False

        # Compara performance actual vs objetivo
        accuracy_gap = target_performance.get("accuracy", 0.8) - current_performance.get("accuracy", 0.5)
        speed_gap = target_performance.get("speed", 0.7) - current_performance.get("speed", 0.5)

        # Switch si hay grandes gaps
        if accuracy_gap > 0.3 or speed_gap > 0.3:
            return True

        # Switch si performance está empeorando consistentemente
        # (esto requeriría historia de performance que no tenemos aquí)

        return False

class ConfidenceCalibrator:
    """Calibra la confianza metacognitiva"""

    def __init__(self):
        self.calibration_history: Dict[str, List[Tuple[float, float]]] = defaultdict(list)  # (confidence, actual)
        self.domain_calibrations: Dict[str, float] = {}  # Factor de calibración por dominio

    def calibrate_confidence(self, raw_confidence: float, domain: str,
                           context: Dict[str, Any] = None) -> float:
        """Calibra confianza cruda basada en historial"""

        if domain not in self.domain_calibrations:
            return raw_confidence

        calibration_factor = self.domain_calibrations[domain]

        # Aplicar calibración
        if calibration_factor > 1.0:  # Overconfianza histórica
            calibrated = raw_confidence / calibration_factor
        else:  # Underconfianza histórica
            calibrated = raw_confidence * (2 - calibration_factor)

        return max(0.0, min(1.0, calibrated))

    def update_calibration(self, domain: str, predicted_confidence: float,
                          actual_performance: float):
        """Actualiza calibración basada en resultado real"""

        self.calibration_history[domain].append((predicted_confidence, actual_performance))

        # Mantener solo últimos 50 registros
        if len(self.calibration_history[domain]) > 50:
            self.calibration_history[domain] = self.calibration_history[domain][-50:]

        # Recalcular factor de calibración
        if len(self.calibration_history[domain]) >= 10:
            confidences, actuals = zip(*self.calibration_history[domain][-20:])

            # Calcular bias promedio
            bias = statistics.mean([c - a for c, a in zip(confidences, actuals)])

            # Factor de calibración
            if bias > 0:  # Overconfianza
                self.domain_calibrations[domain] = 1.0 + bias
            elif bias < 0:  # Underconfianza
                self.domain_calibrations[domain] = max(0.1, 1.0 + bias)
            else:
                self.domain_calibrations[domain] = 1.0

    def get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Convierte confianza numérica a nivel categórico"""
        if confidence < 0.2:
            return ConfidenceLevel.VERY_LOW
        elif confidence < 0.4:
            return ConfidenceLevel.LOW
        elif confidence < 0.6:
            return ConfidenceLevel.MODERATE
        elif confidence < 0.8:
            return ConfidenceLevel.HIGH
        else:
            return ConfidenceLevel.VERY_HIGH

class SelfReflectionEngine:
    """Motor de auto-reflexión y metacognición"""

    def __init__(self):
        self.reflection_triggers = {
            "performance_drop": lambda metrics: metrics.get("accuracy", 1.0) < 0.6,
            "high_uncertainty": lambda metrics: metrics.get("confidence", 1.0) < 0.4,
            "repeated_errors": lambda metrics: metrics.get("error_rate", 0.0) > 0.3,
            "strategy_ineffective": lambda metrics: metrics.get("strategy_success", 1.0) < 0.5,
            "time_limit_approaching": lambda metrics: metrics.get("time_remaining", 1.0) < 0.2
        }

        self.reflection_outcomes: List[Dict[str, Any]] = []

    def should_reflect(self, performance_metrics: Dict[str, float]) -> List[str]:
        """Determina si debe iniciarse reflexión y por qué razones"""

        triggered_reasons = []

        for trigger_name, trigger_func in self.reflection_triggers.items():
            if trigger_func(performance_metrics):
                triggered_reasons.append(trigger_name)

        return triggered_reasons

    def reflect_on_performance(self, task_context: Dict[str, Any],
                             performance_metrics: Dict[str, float],
                             cognitive_state: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza reflexión sobre performance"""

        reflection = {
            "timestamp": time.time(),
            "trigger_reasons": self.should_reflect(performance_metrics),
            "task_context": task_context,
            "performance_metrics": performance_metrics,
            "cognitive_state": cognitive_state,
            "insights": [],
            "recommendations": []
        }

        # Generar insights basados en patrones
        accuracy = performance_metrics.get("accuracy", 0.5)
        confidence = performance_metrics.get("confidence", 0.5)
        speed = performance_metrics.get("speed", 0.5)

        # Insight sobre calibración
        if abs(confidence - accuracy) > 0.3:
            if confidence > accuracy:
                reflection["insights"].append("Showing overconfidence - predicted better performance than achieved")
                reflection["recommendations"].append("Be more conservative in confidence estimates")
            else:
                reflection["insights"].append("Showing underconfidence - achieved better than expected")
                reflection["recommendations"].append("Trust in abilities more, increase confidence")

        # Insight sobre velocidad vs precisión
        if speed > 0.8 and accuracy < 0.6:
            reflection["insights"].append("High speed but low accuracy - may be rushing")
            reflection["recommendations"].append("Slow down and focus on accuracy")
        elif speed < 0.4 and accuracy > 0.8:
            reflection["insights"].append("High accuracy but low speed - may be overthinking")
            reflection["recommendations"].append("Trust initial judgments more, increase speed")

        # Insight sobre carga cognitiva
        cognitive_load = cognitive_state.get("cognitive_load", 0.5)
        if cognitive_load > 0.8 and accuracy < 0.6:
            reflection["insights"].append("High cognitive load correlating with poor performance")
            reflection["recommendations"].append("Use simpler strategies or take breaks")

        # Insight sobre estrategia
        current_strategy = cognitive_state.get("current_strategy")
        if current_strategy and performance_metrics.get("strategy_success", 1.0) < 0.5:
            reflection["insights"].append(f"Current strategy '{current_strategy}' showing poor results")
            reflection["recommendations"].append("Consider switching to alternative strategy")

        self.reflection_outcomes.append(reflection)

        return reflection

    def reflect_on_learning(self, learning_context: Dict[str, Any],
                          learning_outcomes: Dict[str, float]) -> Dict[str, Any]:
        """Reflexión sobre procesos de aprendizaje"""

        reflection = {
            "timestamp": time.time(),
            "type": "learning_reflection",
            "context": learning_context,
            "outcomes": learning_outcomes,
            "insights": [],
            "learning_recommendations": []
        }

        learning_rate = learning_outcomes.get("learning_rate", 0.5)
        retention_rate = learning_outcomes.get("retention_rate", 0.5)
        transfer_ability = learning_outcomes.get("transfer_ability", 0.5)

        # Insights sobre aprendizaje
        if learning_rate > 0.8:
            reflection["insights"].append("Fast learner in this domain")
            reflection["learning_recommendations"].append("Can handle more complex material")
        elif learning_rate < 0.3:
            reflection["insights"].append("Slow learning in this domain")
            reflection["learning_recommendations"].append("Break down material into smaller chunks")

        if retention_rate < 0.5:
            reflection["insights"].append("Poor retention - forgetting quickly")
            reflection["learning_recommendations"].append("Increase practice frequency and use spaced repetition")

        if transfer_ability < 0.4:
            reflection["insights"].append("Difficulty transferring knowledge to new situations")
            reflection["learning_recommendations"].append("Practice with more varied examples")

        return reflection

class MetacognitiveBrain:
    """Sistema central de metacognición"""

    def __init__(self, persist_path: str = "data/metacognitive_state.json"):
        self.persist_path = persist_path

        # Componentes centrales
        self.knowledge = MetacognitiveKnowledge()
        self.monitor = MetacognitiveMonitor()
        self.controller = MetacognitiveController()
        self.calibrator = ConfidenceCalibrator()
        self.reflector = SelfReflectionEngine()

        # Estado metacognitivo actual
        self.current_metacognitive_state = {
            "self_awareness_level": 0.7,
            "cognitive_control": 0.6,
            "strategy_flexibility": 0.8,
            "confidence_calibration": 0.5,
            "reflection_depth": 0.6
        }

        # Historia metacognitiva
        self.metacognitive_episodes: deque = deque(maxlen=50)
        self.strategy_timeline: List[Dict[str, Any]] = []

        # Cargar estado previo
        self._load_metacognitive_state()

        logger.info("🤔 Metacognitive Brain System initialized")

    def initiate_metacognitive_cycle(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Inicia un ciclo metacognitivo completo"""

        cycle_start = time.time()

        # 1. PLANNING: Seleccionar estrategia
        cognitive_state = {
            "cognitive_load": self.monitor.cognitive_load,
            "attention_focus": self.monitor.attention_focus,
            "processing_speed": self.monitor.processing_speed
        }

        selected_strategy = self.controller.select_strategy(task_context, cognitive_state)

        # 2. MONITORING: Iniciar monitoreo
        self.monitor.start_monitoring(selected_strategy, task_context)

        # 3. Registrar episodio metacognitivo
        episode = {
            "timestamp": cycle_start,
            "task_context": task_context,
            "selected_strategy": selected_strategy.value,
            "cognitive_state": cognitive_state.copy(),
            "metacognitive_state": self.current_metacognitive_state.copy()
        }

        self.metacognitive_episodes.append(episode)

        return {
            "selected_strategy": selected_strategy,
            "cognitive_state": cognitive_state,
            "monitoring_active": True,
            "cycle_id": len(self.metacognitive_episodes)
        }

    def monitor_cognitive_process(self, process_outputs: List[Dict[str, Any]],
                                performance_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Monitorea proceso cognitivo en curso"""

        # Detectar conflictos cognitivos
        conflict_detected = self.monitor.detect_cognitive_conflict(process_outputs)

        # Evaluar efectividad de estrategia
        strategy_effectiveness = self.monitor.assess_strategy_effectiveness(performance_metrics)

        # Actualizar carga cognitiva
        task_complexity = performance_metrics.get("complexity", 0.5)
        time_pressure = performance_metrics.get("time_pressure", 0.5)
        working_memory_usage = performance_metrics.get("memory_usage", 0.5)

        self.monitor.update_cognitive_load(task_complexity, time_pressure, working_memory_usage)

        # Determinar si necesita intervención
        needs_intervention = (
            conflict_detected or
            strategy_effectiveness < 0.4 or
            self.monitor.cognitive_load > 0.9
        )

        monitoring_result = {
            "conflict_detected": conflict_detected,
            "strategy_effectiveness": strategy_effectiveness,
            "cognitive_load": self.monitor.cognitive_load,
            "attention_focus": self.monitor.attention_focus,
            "needs_intervention": needs_intervention,
            "errors_detected": self.monitor.errors_detected,
            "corrections_made": self.monitor.corrections_made
        }

        # Log del monitoreo
        self.monitor.monitoring_log.append({
            "timestamp": time.time(),
            "event": "monitoring_update",
            "result": monitoring_result
        })

        return monitoring_result

    def metacognitive_control(self, monitoring_result: Dict[str, Any],
                            task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Ejerce control metacognitivo basado en monitoreo"""

        control_actions = []

        # Control por conflicto cognitivo
        if monitoring_result["conflict_detected"]:
            control_actions.append({
                "type": "conflict_resolution",
                "action": "increase_deliberation",
                "rationale": "Cognitive conflict detected, need more careful analysis"
            })

            # Incrementar foco atencional
            self.monitor.attention_focus = min(1.0, self.monitor.attention_focus + 0.1)

        # Control por baja efectividad de estrategia
        if monitoring_result["strategy_effectiveness"] < 0.4:
            # Considerar cambio de estrategia
            time_elapsed = time.time() - self.monitor.strategy_start_time
            target_performance = task_context.get("target_performance", {"accuracy": 0.8, "speed": 0.7})
            current_performance = {"accuracy": monitoring_result["strategy_effectiveness"]}

            if self.controller.should_switch_strategy(current_performance, time_elapsed, target_performance):
                cognitive_state = {
                    "cognitive_load": monitoring_result["cognitive_load"],
                    "attention_focus": monitoring_result["attention_focus"],
                    "processing_speed": self.monitor.processing_speed
                }

                new_strategy = self.controller.select_strategy(task_context, cognitive_state)

                control_actions.append({
                    "type": "strategy_switch",
                    "action": f"switch_to_{new_strategy.value}",
                    "rationale": f"Current strategy ineffective ({monitoring_result['strategy_effectiveness']:.2f})"
                })

                # Actualizar monitor
                self.monitor.strategy_switches += 1
                self.monitor.start_monitoring(new_strategy, task_context)

        # Control por alta carga cognitiva
        if monitoring_result["cognitive_load"] > 0.8:
            control_actions.append({
                "type": "load_management",
                "action": "simplify_approach",
                "rationale": f"High cognitive load ({monitoring_result['cognitive_load']:.2f})"
            })

        # Control por baja atención
        if monitoring_result["attention_focus"] < 0.5:
            control_actions.append({
                "type": "attention_regulation",
                "action": "refocus_attention",
                "rationale": f"Low attention focus ({monitoring_result['attention_focus']:.2f})"
            })

        return {
            "control_actions": control_actions,
            "metacognitive_state_updated": len(control_actions) > 0
        }

    def calibrate_confidence(self, confidence_estimate: float, domain: str,
                           context: Dict[str, Any] = None) -> Tuple[float, ConfidenceLevel]:
        """Calibra estimación de confianza"""

        calibrated_confidence = self.calibrator.calibrate_confidence(
            confidence_estimate, domain, context
        )

        confidence_level = self.calibrator.get_confidence_level(calibrated_confidence)

        return calibrated_confidence, confidence_level

    def update_metacognitive_knowledge(self, learning_episode: Dict[str, Any]):
        """Actualiza conocimiento metacognitivo basado en episodio de aprendizaje"""

        domain = learning_episode.get("domain", "general")
        task_type = learning_episode.get("task_type", "reasoning")
        performance = learning_episode.get("performance", 0.5)
        strategy_used = learning_episode.get("strategy_used")
        confidence = learning_episode.get("confidence", 0.5)

        # Actualizar conocimiento de memoria
        if "memory" in task_type.lower():
            self.knowledge.update_memory_knowledge(domain, performance, task_type)

        # Actualizar conocimiento de razonamiento
        if "reasoning" in task_type.lower():
            self.knowledge.update_reasoning_knowledge(task_type, performance, confidence)

        # Actualizar conocimiento de aprendizaje
        learning_rate = learning_episode.get("learning_rate", 0.5)
        conditions = learning_episode.get("conditions", {})
        self.knowledge.update_learning_knowledge(domain, learning_rate, conditions)

        # Actualizar éxito de estrategia
        if strategy_used:
            try:
                strategy_enum = CognitiveStrategy(strategy_used)
                self.controller.update_strategy_success(strategy_enum, performance)
            except ValueError:
                pass  # Estrategia no reconocida

        # Actualizar calibración de confianza
        self.calibrator.update_calibration(domain, confidence, performance)

    def trigger_self_reflection(self, reflection_context: Dict[str, Any]) -> Dict[str, Any]:
        """Desencadena proceso de auto-reflexión"""

        task_context = reflection_context.get("task_context", {})
        performance_metrics = reflection_context.get("performance_metrics", {})
        cognitive_state = reflection_context.get("cognitive_state", {})

        # Verificar si debe reflexionar
        should_reflect_reasons = self.reflector.should_reflect(performance_metrics)

        if should_reflect_reasons:
            # Realizar reflexión sobre performance
            performance_reflection = self.reflector.reflect_on_performance(
                task_context, performance_metrics, cognitive_state
            )

            # Si hay contexto de aprendizaje, reflexionar también sobre eso
            learning_reflection = None
            if "learning_context" in reflection_context:
                learning_context = reflection_context["learning_context"]
                learning_outcomes = reflection_context.get("learning_outcomes", {})
                learning_reflection = self.reflector.reflect_on_learning(
                    learning_context, learning_outcomes
                )

            # Actualizar estado metacognitivo basado en reflexiones
            self._update_metacognitive_state_from_reflection(performance_reflection)

            return {
                "reflection_triggered": True,
                "trigger_reasons": should_reflect_reasons,
                "performance_reflection": performance_reflection,
                "learning_reflection": learning_reflection,
                "updated_metacognitive_state": self.current_metacognitive_state
            }

        else:
            return {
                "reflection_triggered": False,
                "reason": "No reflection triggers met"
            }

    def _update_metacognitive_state_from_reflection(self, reflection: Dict[str, Any]):
        """Actualiza estado metacognitivo basado en reflexión"""

        insights = reflection.get("insights", [])
        recommendations = reflection.get("recommendations", [])

        # Actualizar self-awareness basado en insights
        if len(insights) > 2:  # Muchos insights = alta awareness
            self.current_metacognitive_state["self_awareness_level"] = min(1.0,
                self.current_metacognitive_state["self_awareness_level"] + 0.05)

        # Actualizar control cognitivo basado en recomendaciones
        if len(recommendations) > 0:
            self.current_metacognitive_state["cognitive_control"] = min(1.0,
                self.current_metacognitive_state["cognitive_control"] + 0.03)

        # Actualizar flexibilidad de estrategia si hay recomendaciones de cambio
        strategy_change_recs = [r for r in recommendations if "strategy" in r.lower()]
        if strategy_change_recs:
            self.current_metacognitive_state["strategy_flexibility"] = min(1.0,
                self.current_metacognitive_state["strategy_flexibility"] + 0.05)

        # Actualizar profundidad de reflexión
        reflection_depth = len(insights) + len(recommendations)
        if reflection_depth > 3:
            self.current_metacognitive_state["reflection_depth"] = min(1.0,
                self.current_metacognitive_state["reflection_depth"] + 0.05)

    def get_metacognitive_status(self) -> Dict[str, Any]:
        """Obtiene estado completo del sistema metacognitivo"""

        return {
            "metacognitive_state": self.current_metacognitive_state,
            "current_strategy": self.monitor.current_strategy.value if self.monitor.current_strategy else None,
            "cognitive_load": self.monitor.cognitive_load,
            "attention_focus": self.monitor.attention_focus,
            "strategy_effectiveness": self.monitor.strategy_effectiveness,
            "knowledge_summary": {
                "memory_domains": len(self.knowledge.memory_strengths),
                "reasoning_types": len(self.knowledge.reasoning_accuracy),
                "learning_domains": len(self.knowledge.learning_curves)
            },
            "recent_reflections": len(self.reflector.reflection_outcomes),
            "calibration_domains": len(self.calibrator.domain_calibrations)
        }

    def _load_metacognitive_state(self):
        """Carga estado metacognitivo persistido"""
        try:
            with open(self.persist_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Restaurar estado metacognitivo
            if "metacognitive_state" in data:
                self.current_metacognitive_state.update(data["metacognitive_state"])

            # Restaurar preferencias de estrategia
            if "strategy_preferences" in data:
                for strategy_name, preference in data["strategy_preferences"].items():
                    try:
                        strategy = CognitiveStrategy(strategy_name)
                        self.controller.strategy_preferences[strategy] = preference
                    except ValueError:
                        pass

            logger.info(f"Metacognitive state loaded from {self.persist_path}")

        except FileNotFoundError:
            logger.info("No metacognitive state found, starting fresh")
        except Exception as e:
            logger.warning(f"Failed to load metacognitive state: {e}")

    def save_metacognitive_state(self):
        """Guarda estado metacognitivo"""
        try:
            data = {
                "timestamp": time.time(),
                "metacognitive_state": self.current_metacognitive_state,
                "strategy_preferences": {
                    strategy.value: preference
                    for strategy, preference in self.controller.strategy_preferences.items()
                },
                "calibration_factors": self.calibrator.domain_calibrations,
                "recent_episodes": list(self.metacognitive_episodes)[-10:]
            }

            with open(self.persist_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Metacognitive state saved to {self.persist_path}")

        except Exception as e:
            logger.error(f"Failed to save metacognitive state: {e}")

# Función de fábrica
def create_metacognitive_brain() -> MetacognitiveBrain:
    """Crea y configura sistema metacognitivo"""
    return MetacognitiveBrain()
