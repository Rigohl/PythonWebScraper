"""
Emotional Brain System - Sistema de Procesamiento Emocional

Este módulo implementa un sistema emocional inspirado en neurociencia afectiva:
- Modelo Circumplex: valencia (positivo/negativo) x arousal (activación/desactivación)
- Teoría de Evaluación Cognitiva: appraisal de eventos
- Regulación Emocional: estrategias de control emocional
- Influencia en Memoria: efectos emocionales en encoding/retrieval
- Influencia en Toma de Decisiones: sesgo emocional en razonamiento
- Emociones Básicas: miedo, alegría, tristeza, ira, sorpresa, disgusto
- Estados de Ánimo: patrones emocionales prolongados
- Empatía: modelado de estados emocionales de otros
"""

import json
import logging
import math
import random
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


logger = logging.getLogger(__name__)


class BasicEmotion(Enum):
    JOY = "joy"  # Alegría
    SADNESS = "sadness"  # Tristeza
    ANGER = "anger"  # Ira
    FEAR = "fear"  # Miedo
    SURPRISE = "surprise"  # Sorpresa
    DISGUST = "disgust"  # Disgusto
    NEUTRAL = "neutral"  # Neutral


class EmotionRegulationStrategy(Enum):
    REAPPRAISAL = "reappraisal"  # Reevaluación cognitiva
    SUPPRESSION = "suppression"  # Supresión expresiva
    DISTRACTION = "distraction"  # Distracción atencional
    ACCEPTANCE = "acceptance"  # Aceptación mindful
    PROBLEM_SOLVING = "problem_solving"  # Resolución de problemas
    VENTING = "venting"  # Desahogo emocional


class AppraisalDimension(Enum):
    VALENCE = "valence"  # Positivo/Negativo
    AROUSAL = "arousal"  # Activación/Calma
    GOAL_CONGRUENCE = "goal_congruence"  # Congruente/Incongruente con objetivos
    AGENCY = "agency"  # Control personal/Externo
    CERTAINTY = "certainty"  # Certeza/Incertidumbre
    NOVELTY = "novelty"  # Familiar/Novedoso
    URGENCY = "urgency"  # Urgente/No urgente


@dataclass
class EmotionalAppraisal:
    """Evaluación cognitiva de un evento que genera emoción"""

    event_description: str
    appraisal_values: Dict[AppraisalDimension, float]  # -1 to 1
    confidence: float = 0.8
    contextual_factors: Dict[str, Any] = field(default_factory=dict)

    def get_primary_emotion(self) -> BasicEmotion:
        """Determina emoción básica basada en appraisal"""
        valence = self.appraisal_values.get(AppraisalDimension.VALENCE, 0.0)
        arousal = self.appraisal_values.get(AppraisalDimension.AROUSAL, 0.0)
        goal_congruence = self.appraisal_values.get(
            AppraisalDimension.GOAL_CONGRUENCE, 0.0
        )
        agency = self.appraisal_values.get(AppraisalDimension.AGENCY, 0.0)
        certainty = self.appraisal_values.get(AppraisalDimension.CERTAINTY, 0.0)

        # Reglas de appraisal para emociones básicas
        if valence > 0.5 and arousal > 0.3:
            return BasicEmotion.JOY
        elif valence < -0.5 and goal_congruence < -0.3:
            if agency < -0.3:  # Poco control
                return BasicEmotion.SADNESS
            else:  # Más control
                return BasicEmotion.ANGER
        elif arousal > 0.7 and certainty < -0.5:
            if valence > 0:
                return BasicEmotion.SURPRISE
            else:
                return BasicEmotion.FEAR
        elif valence < -0.3 and arousal < 0:
            return BasicEmotion.DISGUST
        else:
            return BasicEmotion.NEUTRAL

    def get_emotion_intensity(self) -> float:
        """Calcula intensidad emocional basada en arousal y congruencia"""
        arousal = abs(self.appraisal_values.get(AppraisalDimension.AROUSAL, 0.0))
        goal_importance = abs(
            self.appraisal_values.get(AppraisalDimension.GOAL_CONGRUENCE, 0.0)
        )

        intensity = (arousal + goal_importance) / 2
        return min(1.0, max(0.0, intensity))


@dataclass
class EmotionalState:
    """Estado emocional actual del sistema"""

    primary_emotion: BasicEmotion
    intensity: float
    valence: float  # -1 (negative) to 1 (positive)
    arousal: float  # -1 (calm) to 1 (excited)

    # Componentes específicos
    physiological_response: Dict[str, float] = field(default_factory=dict)
    cognitive_effects: Dict[str, float] = field(default_factory=dict)
    behavioral_tendencies: Dict[str, float] = field(default_factory=dict)

    # Metadatos temporales
    onset_time: float = field(default_factory=time.time)
    duration: float = 0.0
    decay_rate: float = 0.9  # Rate de decaimiento por minuto

    def update_duration(self):
        """Actualiza duración del estado emocional"""
        current_time = time.time()
        self.duration = current_time - self.onset_time

    def apply_decay(self, time_elapsed_minutes: float = 1.0):
        """Aplica decay temporal a la intensidad emocional"""
        decay_factor = math.pow(self.decay_rate, time_elapsed_minutes)
        self.intensity *= decay_factor

        # Ajustar arousal y valence proporcionalmente
        self.arousal *= decay_factor
        if self.valence != 0:
            self.valence = (
                self.valence * decay_factor if abs(self.valence) > 0.1 else 0.0
            )

    def blend_with_emotion(
        self, other_emotion: "EmotionalState", blend_factor: float = 0.3
    ):
        """Mezcla estado actual con nueva emoción"""

        # Weighted average de componentes principales
        self.intensity = (
            1 - blend_factor
        ) * self.intensity + blend_factor * other_emotion.intensity
        self.valence = (
            1 - blend_factor
        ) * self.valence + blend_factor * other_emotion.valence
        self.arousal = (
            1 - blend_factor
        ) * self.arousal + blend_factor * other_emotion.arousal

        # Si la nueva emoción es más intensa, puede cambiar la emoción primaria
        if other_emotion.intensity > self.intensity * 1.2:
            self.primary_emotion = other_emotion.primary_emotion


@dataclass
class MoodState:
    """Estado de ánimo de más larga duración"""

    mood_label: str  # "optimistic", "pessimistic", "anxious", "confident", etc.
    valence_bias: float  # Sesgo hacia valencia positiva/negativa
    arousal_baseline: float  # Línea base de activación
    duration_hours: float = 0.0
    stability: float = 0.8  # Resistencia a cambios

    onset_time: float = field(default_factory=time.time)

    def influence_emotion(self, emotion: EmotionalState) -> EmotionalState:
        """Influye en una emoción basado en el estado de ánimo"""

        # Mood sesga la interpretación emocional
        emotion.valence += self.valence_bias * 0.2
        emotion.arousal += (self.arousal_baseline - emotion.arousal) * 0.1

        # Clamp values
        emotion.valence = max(-1.0, min(1.0, emotion.valence))
        emotion.arousal = max(-1.0, min(1.0, emotion.arousal))

        return emotion

    def update_from_emotions(self, recent_emotions: List[EmotionalState]):
        """Actualiza mood basado en emociones recientes"""
        if not recent_emotions:
            return

        # Calcular tendencias emocionales
        avg_valence = statistics.mean([e.valence for e in recent_emotions])
        avg_arousal = statistics.mean([e.arousal for e in recent_emotions])

        # Actualizar mood con inercia
        learning_rate = 0.1 / self.stability
        self.valence_bias += (avg_valence - self.valence_bias) * learning_rate
        self.arousal_baseline += (avg_arousal - self.arousal_baseline) * learning_rate


class EmotionRegulator:
    """Sistema de regulación emocional"""

    def __init__(self):
        self.regulation_strategies = {
            EmotionRegulationStrategy.REAPPRAISAL: self._cognitive_reappraisal,
            EmotionRegulationStrategy.SUPPRESSION: self._emotional_suppression,
            EmotionRegulationStrategy.DISTRACTION: self._attentional_distraction,
            EmotionRegulationStrategy.ACCEPTANCE: self._mindful_acceptance,
            EmotionRegulationStrategy.PROBLEM_SOLVING: self._problem_focused_coping,
            EmotionRegulationStrategy.VENTING: self._emotional_venting,
        }

        self.strategy_effectiveness = {
            EmotionRegulationStrategy.REAPPRAISAL: 0.8,
            EmotionRegulationStrategy.SUPPRESSION: 0.4,
            EmotionRegulationStrategy.DISTRACTION: 0.6,
            EmotionRegulationStrategy.ACCEPTANCE: 0.7,
            EmotionRegulationStrategy.PROBLEM_SOLVING: 0.9,
            EmotionRegulationStrategy.VENTING: 0.5,
        }

        self.recent_strategy_use = defaultdict(int)

    def regulate_emotion(
        self,
        emotion: EmotionalState,
        strategy: EmotionRegulationStrategy,
        context: Dict[str, Any] = None,
    ) -> EmotionalState:
        """Aplica estrategia de regulación emocional"""

        if strategy not in self.regulation_strategies:
            return emotion

        # Aplicar estrategia específica
        regulated_emotion = self.regulation_strategies[strategy](emotion, context or {})

        # Efectividad basada en la estrategia y contexto
        effectiveness = self.strategy_effectiveness[strategy]

        # Reducir efectividad si se usa demasiado la misma estrategia
        if self.recent_strategy_use[strategy] > 3:
            effectiveness *= 0.7

        # Aplicar regulación
        regulation_strength = effectiveness * (
            emotion.intensity / 2
        )  # Más fuerte para emociones más intensas

        regulated_emotion.intensity *= 1 - regulation_strength
        regulated_emotion.arousal *= 1 - regulation_strength * 0.7

        # Registro de uso
        self.recent_strategy_use[strategy] += 1

        return regulated_emotion

    def _cognitive_reappraisal(
        self, emotion: EmotionalState, context: Dict[str, Any]
    ) -> EmotionalState:
        """Reevaluación cognitiva - cambiar interpretación del evento"""
        new_emotion = EmotionalState(
            primary_emotion=emotion.primary_emotion,
            intensity=emotion.intensity,
            valence=emotion.valence,
            arousal=emotion.arousal,
        )

        # Reappraisal reduce intensidad y puede cambiar valence
        if emotion.valence < 0:  # Emociones negativas
            new_emotion.valence = min(
                emotion.valence + 0.3, 0.5
            )  # Hacer menos negativo

        new_emotion.cognitive_effects["reappraisal_applied"] = 1.0
        return new_emotion

    def _emotional_suppression(
        self, emotion: EmotionalState, context: Dict[str, Any]
    ) -> EmotionalState:
        """Supresión expresiva - inhibir expresión emocional"""
        new_emotion = EmotionalState(
            primary_emotion=emotion.primary_emotion,
            intensity=emotion.intensity,
            valence=emotion.valence,
            arousal=emotion.arousal,
        )

        # Supresión reduce arousal pero mantiene valence
        new_emotion.arousal *= 0.6
        new_emotion.behavioral_tendencies["expression_suppressed"] = 1.0

        # Puede tener efectos negativos a largo plazo
        new_emotion.physiological_response["tension"] = 0.7

        return new_emotion

    def _attentional_distraction(
        self, emotion: EmotionalState, context: Dict[str, Any]
    ) -> EmotionalState:
        """Distracción atencional - enfocar atención en otra cosa"""
        new_emotion = EmotionalState(
            primary_emotion=emotion.primary_emotion,
            intensity=emotion.intensity * 0.7,  # Reducir intensidad
            valence=emotion.valence,
            arousal=emotion.arousal * 0.8,
        )

        new_emotion.cognitive_effects["attention_diverted"] = 1.0
        return new_emotion

    def _mindful_acceptance(
        self, emotion: EmotionalState, context: Dict[str, Any]
    ) -> EmotionalState:
        """Aceptación mindful - aceptar emoción sin juzgar"""
        new_emotion = EmotionalState(
            primary_emotion=emotion.primary_emotion,
            intensity=emotion.intensity,
            valence=emotion.valence,
            arousal=emotion.arousal * 0.7,  # Reduce arousal manteniendo awareness
        )

        new_emotion.cognitive_effects["mindful_awareness"] = 1.0
        new_emotion.behavioral_tendencies["acceptance"] = 1.0

        return new_emotion

    def _problem_focused_coping(
        self, emotion: EmotionalState, context: Dict[str, Any]
    ) -> EmotionalState:
        """Resolución de problemas - abordar causa de la emoción"""
        new_emotion = EmotionalState(
            primary_emotion=emotion.primary_emotion,
            intensity=emotion.intensity,
            valence=emotion.valence,
            arousal=emotion.arousal,
        )

        # Si hay problemas solucionables, reduce emoción negativa
        if emotion.valence < 0 and context.get("solvable_problem", False):
            new_emotion.intensity *= 0.6
            new_emotion.valence = min(new_emotion.valence + 0.4, 0.8)

        new_emotion.cognitive_effects["problem_solving_active"] = 1.0

        return new_emotion

    def _emotional_venting(
        self, emotion: EmotionalState, context: Dict[str, Any]
    ) -> EmotionalState:
        """Desahogo emocional - expresar emoción"""
        new_emotion = EmotionalState(
            primary_emotion=emotion.primary_emotion,
            intensity=emotion.intensity * 0.8,
            valence=emotion.valence,
            arousal=emotion.arousal * 0.6,
        )

        new_emotion.behavioral_tendencies["emotional_expression"] = 1.0
        new_emotion.physiological_response["tension_release"] = 0.8

        return new_emotion

    def suggest_regulation_strategy(
        self, emotion: EmotionalState, context: Dict[str, Any] = None
    ) -> EmotionRegulationStrategy:
        """Sugiere estrategia de regulación basada en emoción y contexto"""

        context = context or {}

        # Reglas heurísticas para selección de estrategia
        if emotion.intensity < 0.3:
            return EmotionRegulationStrategy.ACCEPTANCE

        if emotion.primary_emotion == BasicEmotion.ANGER and emotion.intensity > 0.7:
            return EmotionRegulationStrategy.REAPPRAISAL

        if emotion.primary_emotion == BasicEmotion.FEAR:
            if context.get("controllable", False):
                return EmotionRegulationStrategy.PROBLEM_SOLVING
            else:
                return EmotionRegulationStrategy.ACCEPTANCE

        if emotion.primary_emotion == BasicEmotion.SADNESS:
            if context.get("social_support", False):
                return EmotionRegulationStrategy.VENTING
            else:
                return EmotionRegulationStrategy.REAPPRAISAL

        if emotion.arousal > 0.8:
            return EmotionRegulationStrategy.DISTRACTION

        # Default
        return EmotionRegulationStrategy.REAPPRAISAL


class EmotionalMemoryInfluencer:
    """Influye en la formación y recuperación de memorias basado en estado emocional"""

    def __init__(self):
        self.emotion_memory_weights = {
            BasicEmotion.JOY: 1.2,  # Memorias positivas se fortalecen
            BasicEmotion.FEAR: 1.5,  # Memorias de miedo son muy fuertes
            BasicEmotion.ANGER: 1.1,  # Memorias de ira moderadamente fuertes
            BasicEmotion.SADNESS: 0.9,  # Memorias tristes pueden ser suprimidas
            BasicEmotion.SURPRISE: 1.3,  # Eventos sorpresivos son memorables
            BasicEmotion.DISGUST: 1.0,  # Neutral
            BasicEmotion.NEUTRAL: 1.0,  # Sin modificación
        }

    def influence_encoding(
        self, memory_content: Dict[str, Any], emotional_state: EmotionalState
    ) -> Dict[str, Any]:
        """Influye en el encoding de memoria basado en estado emocional"""

        # Copiar contenido original
        influenced_memory = memory_content.copy()

        # Añadir contexto emocional
        influenced_memory["emotional_context"] = {
            "emotion": emotional_state.primary_emotion.value,
            "intensity": emotional_state.intensity,
            "valence": emotional_state.valence,
            "arousal": emotional_state.arousal,
        }

        # Modificar strength basado en emoción
        emotion_weight = self.emotion_memory_weights.get(
            emotional_state.primary_emotion, 1.0
        )
        intensity_bonus = emotional_state.intensity * 0.5

        influenced_memory["emotional_strength_multiplier"] = (
            emotion_weight + intensity_bonus
        )

        # Memorias de alta arousal tienen más detalles
        if emotional_state.arousal > 0.7:
            influenced_memory["enhanced_encoding"] = True
            influenced_memory["vividness"] = min(
                1.0, 0.8 + emotional_state.arousal * 0.2
            )

        # Memorias negativas intensas pueden crear evitación
        if emotional_state.valence < -0.5 and emotional_state.intensity > 0.8:
            influenced_memory["avoidance_tendency"] = True

        return influenced_memory

    def influence_retrieval(
        self, retrieval_cues: List[str], current_emotion: EmotionalState
    ) -> Dict[str, float]:
        """Influye en la recuperación de memorias basado en emoción actual"""

        cue_weights = {}

        for cue in retrieval_cues:
            base_weight = 1.0

            # Mood congruent memory: memorias congruentes con estado actual son más accesibles
            if current_emotion.valence > 0.3:  # Estado positivo
                if any(
                    positive_word in cue.lower()
                    for positive_word in ["success", "good", "happy", "win"]
                ):
                    base_weight *= 1.4
                elif any(
                    negative_word in cue.lower()
                    for negative_word in ["fail", "error", "bad", "lose"]
                ):
                    base_weight *= 0.7

            elif current_emotion.valence < -0.3:  # Estado negativo
                if any(
                    negative_word in cue.lower()
                    for negative_word in ["fail", "error", "bad", "lose"]
                ):
                    base_weight *= 1.4
                elif any(
                    positive_word in cue.lower()
                    for positive_word in ["success", "good", "happy", "win"]
                ):
                    base_weight *= 0.7

            # Alta arousal facilita recuperación de memorias de alta arousal
            if current_emotion.arousal > 0.7:
                if any(
                    arousing_word in cue.lower()
                    for arousing_word in [
                        "urgent",
                        "critical",
                        "important",
                        "emergency",
                    ]
                ):
                    base_weight *= 1.3

            cue_weights[cue] = base_weight

        return cue_weights


class EmotionalDecisionInfluencer:
    """Influye en la toma de decisiones basado en estado emocional"""

    def __init__(self):
        self.emotion_decision_biases = {
            BasicEmotion.FEAR: {
                "risk_tolerance": -0.6,  # Más adverso al riesgo
                "optimism_bias": -0.4,  # Menos optimista
                "time_preference": 0.3,  # Prefiere beneficios inmediatos
            },
            BasicEmotion.JOY: {
                "risk_tolerance": 0.3,  # Ligeramente más tolerante al riesgo
                "optimism_bias": 0.6,  # Más optimista
                "time_preference": -0.2,  # Puede esperar por mejores resultados
            },
            BasicEmotion.ANGER: {
                "risk_tolerance": 0.5,  # Más propenso a tomar riesgos
                "optimism_bias": -0.2,  # Ligeramente pesimista
                "time_preference": 0.4,  # Impaciente
            },
            BasicEmotion.SADNESS: {
                "risk_tolerance": -0.3,  # Algo adverso al riesgo
                "optimism_bias": -0.5,  # Pesimista
                "time_preference": 0.1,  # Ligeramente impaciente
            },
        }

    def influence_decision(
        self, decision_options: List[Dict[str, Any]], emotional_state: EmotionalState
    ) -> List[Dict[str, Any]]:
        """Influye en evaluación de opciones de decisión"""

        biases = self.emotion_decision_biases.get(emotional_state.primary_emotion, {})

        influenced_options = []

        for option in decision_options:
            influenced_option = option.copy()

            # Aplicar sesgos emocionales
            risk_level = option.get("risk_level", 0.5)
            expected_outcome = option.get("expected_outcome", 0.5)
            time_to_benefit = option.get("time_to_benefit", 0.5)

            # Ajustar evaluaciones basado en sesgos emocionales
            risk_bias = biases.get("risk_tolerance", 0.0) * emotional_state.intensity
            optimism_bias = biases.get("optimism_bias", 0.0) * emotional_state.intensity
            time_bias = biases.get("time_preference", 0.0) * emotional_state.intensity

            # Calcular nueva valoración
            risk_penalty = risk_level * abs(risk_bias) if risk_bias < 0 else 0
            optimism_boost = optimism_bias * 0.3
            time_penalty = time_to_benefit * abs(time_bias) if time_bias > 0 else 0

            adjusted_value = (
                expected_outcome + optimism_boost - risk_penalty - time_penalty
            )
            adjusted_value = max(0.0, min(1.0, adjusted_value))

            influenced_option["emotional_adjustment"] = {
                "original_value": expected_outcome,
                "adjusted_value": adjusted_value,
                "risk_bias": risk_bias,
                "optimism_bias": optimism_bias,
                "time_bias": time_bias,
            }

            influenced_options.append(influenced_option)

        return influenced_options


class EmotionalBrain:
    """Sistema de procesamiento emocional central"""

    def __init__(self, persist_path: str = "data/emotional_state.json"):
        self.persist_path = persist_path

        # Estado emocional actual
        self.current_emotion = EmotionalState(
            primary_emotion=BasicEmotion.NEUTRAL,
            intensity=0.1,
            valence=0.0,
            arousal=0.0,
        )

        # Estado de ánimo actual
        self.current_mood = MoodState(
            mood_label="neutral", valence_bias=0.0, arousal_baseline=0.0
        )

        # Sistemas componentes
        self.regulator = EmotionRegulator()
        self.memory_influencer = EmotionalMemoryInfluencer()
        self.decision_influencer = EmotionalDecisionInfluencer()

        # Historia emocional
        self.emotion_history: deque = deque(maxlen=100)
        self.mood_history: deque = deque(maxlen=24)  # 24 horas de historia de mood

        # Parámetros del sistema
        self.emotional_reactivity = 0.7  # Qué tan reactivo es emocionalmente
        self.mood_stability = 0.8  # Qué tan estable es el mood
        self.regulation_tendency = 0.6  # Tendencia a regular emociones

        # Cargar estado previo
        self._load_emotional_state()

        logger.info("🎭 Emotional Brain System initialized")

    def appraise_event(
        self, event_description: str, context: Dict[str, Any] = None
    ) -> EmotionalAppraisal:
        """Evalúa un evento y genera appraisal emocional"""

        context = context or {}

        # Inicializar valores de appraisal
        appraisal_values = {}

        # Heurísticas para evaluación automática
        event_lower = event_description.lower()

        # Valence (positivo/negativo)
        positive_indicators = ["success", "good", "win", "achieve", "complete", "solve"]
        negative_indicators = ["fail", "error", "problem", "bad", "lose", "break"]

        positive_score = sum(
            1 for indicator in positive_indicators if indicator in event_lower
        )
        negative_score = sum(
            1 for indicator in negative_indicators if indicator in event_lower
        )

        if positive_score > negative_score:
            appraisal_values[AppraisalDimension.VALENCE] = min(
                0.8, 0.2 + positive_score * 0.3
            )
        elif negative_score > positive_score:
            appraisal_values[AppraisalDimension.VALENCE] = max(
                -0.8, -0.2 - negative_score * 0.3
            )
        else:
            appraisal_values[AppraisalDimension.VALENCE] = 0.0

        # Arousal (activación)
        arousing_indicators = [
            "urgent",
            "critical",
            "important",
            "emergency",
            "deadline",
        ]
        arousing_score = sum(
            1 for indicator in arousing_indicators if indicator in event_lower
        )
        appraisal_values[AppraisalDimension.AROUSAL] = min(
            0.9, arousing_score * 0.4 + 0.1
        )

        # Goal congruence
        goal_congruence = context.get("goal_relevance", 0.0)
        appraisal_values[AppraisalDimension.GOAL_CONGRUENCE] = goal_congruence

        # Agency (control)
        controllable = context.get("controllable", True)
        appraisal_values[AppraisalDimension.AGENCY] = 0.6 if controllable else -0.4

        # Certainty
        certainty = context.get("certainty", 0.5)
        appraisal_values[AppraisalDimension.CERTAINTY] = (
            certainty * 2 - 1
        )  # Scale to -1, 1

        # Novelty
        familiar = context.get("familiar", False)
        appraisal_values[AppraisalDimension.NOVELTY] = -0.5 if familiar else 0.7

        # Urgency
        urgent = context.get("urgent", False)
        appraisal_values[AppraisalDimension.URGENCY] = 0.8 if urgent else 0.2

        return EmotionalAppraisal(
            event_description=event_description,
            appraisal_values=appraisal_values,
            contextual_factors=context,
        )

    def process_emotional_event(
        self, event_description: str, context: Dict[str, Any] = None
    ) -> EmotionalState:
        """Procesa un evento y genera respuesta emocional"""

        # Generar appraisal
        appraisal = self.appraise_event(event_description, context)

        # Determinar emoción primaria
        primary_emotion = appraisal.get_primary_emotion()
        intensity = appraisal.get_emotion_intensity() * self.emotional_reactivity

        # Extraer valencia y arousal
        valence = appraisal.appraisal_values.get(AppraisalDimension.VALENCE, 0.0)
        arousal = appraisal.appraisal_values.get(AppraisalDimension.AROUSAL, 0.0)

        # Crear nueva emoción
        new_emotion = EmotionalState(
            primary_emotion=primary_emotion,
            intensity=intensity,
            valence=valence,
            arousal=arousal,
        )

        # Influencia del mood actual
        new_emotion = self.current_mood.influence_emotion(new_emotion)

        # Mezclar con emoción actual
        self.current_emotion.blend_with_emotion(new_emotion, blend_factor=0.7)

        # Añadir a historia
        self.emotion_history.append(
            {
                "timestamp": time.time(),
                "event": event_description,
                "emotion": primary_emotion.value,
                "intensity": intensity,
                "valence": valence,
                "arousal": arousal,
            }
        )

        # Considerar regulación automática
        if (
            self.current_emotion.intensity > 0.8
            and random.random() < self.regulation_tendency
        ):
            strategy = self.regulator.suggest_regulation_strategy(
                self.current_emotion, context
            )
            self.current_emotion = self.regulator.regulate_emotion(
                self.current_emotion, strategy, context
            )

        logger.debug(
            f"Emotional event processed: {event_description} -> {primary_emotion.value} ({intensity:.2f})"
        )

        return self.current_emotion

    def update_mood(self):
        """Actualiza estado de ánimo basado en emociones recientes"""

        # Obtener emociones de las últimas 2 horas
        recent_cutoff = time.time() - 2 * 3600
        recent_emotions = [
            entry
            for entry in self.emotion_history
            if entry["timestamp"] > recent_cutoff
        ]

        if recent_emotions:
            # Crear objetos EmotionalState para análisis
            emotion_states = []
            for entry in recent_emotions:
                emotion_states.append(
                    EmotionalState(
                        primary_emotion=BasicEmotion(entry["emotion"]),
                        intensity=entry["intensity"],
                        valence=entry["valence"],
                        arousal=entry["arousal"],
                    )
                )

            # Actualizar mood
            self.current_mood.update_from_emotions(emotion_states)

            # Determinar nueva etiqueta de mood
            if self.current_mood.valence_bias > 0.3:
                if self.current_mood.arousal_baseline > 0.3:
                    self.current_mood.mood_label = "energetic_positive"
                else:
                    self.current_mood.mood_label = "calm_positive"
            elif self.current_mood.valence_bias < -0.3:
                if self.current_mood.arousal_baseline > 0.3:
                    self.current_mood.mood_label = "anxious"
                else:
                    self.current_mood.mood_label = "sad"
            else:
                self.current_mood.mood_label = "neutral"

    def get_emotional_state(self) -> Dict[str, Any]:
        """Obtiene estado emocional actual completo"""

        self.current_emotion.update_duration()

        return {
            "current_emotion": {
                "emotion": self.current_emotion.primary_emotion.value,
                "intensity": self.current_emotion.intensity,
                "valence": self.current_emotion.valence,
                "arousal": self.current_emotion.arousal,
                "duration_minutes": self.current_emotion.duration / 60,
            },
            "current_mood": {
                "label": self.current_mood.mood_label,
                "valence_bias": self.current_mood.valence_bias,
                "arousal_baseline": self.current_mood.arousal_baseline,
                "stability": self.current_mood.stability,
            },
            "system_parameters": {
                "emotional_reactivity": self.emotional_reactivity,
                "mood_stability": self.mood_stability,
                "regulation_tendency": self.regulation_tendency,
            },
        }

    def decay_emotions(self, time_elapsed_minutes: float = 1.0):
        """Aplica decay temporal a emociones"""
        self.current_emotion.apply_decay(time_elapsed_minutes)

        # Si la emoción se vuelve muy débil, volver a neutral
        if self.current_emotion.intensity < 0.1:
            self.current_emotion.primary_emotion = BasicEmotion.NEUTRAL
            self.current_emotion.valence *= 0.5
            self.current_emotion.arousal *= 0.5

    def influence_memory_encoding(
        self, memory_content: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Interfaz para influir en encoding de memoria"""
        return self.memory_influencer.influence_encoding(
            memory_content, self.current_emotion
        )

    def influence_memory_retrieval(self, retrieval_cues: List[str]) -> Dict[str, float]:
        """Interfaz para influir en recuperación de memoria"""
        return self.memory_influencer.influence_retrieval(
            retrieval_cues, self.current_emotion
        )

    def influence_decision_making(
        self, decision_options: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Interfaz para influir en toma de decisiones"""
        return self.decision_influencer.influence_decision(
            decision_options, self.current_emotion
        )

    def _load_emotional_state(self):
        """Carga estado emocional persistido"""
        try:
            with open(self.persist_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Restaurar parámetros básicos
            self.emotional_reactivity = data.get("emotional_reactivity", 0.7)
            self.mood_stability = data.get("mood_stability", 0.8)
            self.regulation_tendency = data.get("regulation_tendency", 0.6)

            # Restaurar mood
            mood_data = data.get("current_mood", {})
            self.current_mood.mood_label = mood_data.get("label", "neutral")
            self.current_mood.valence_bias = mood_data.get("valence_bias", 0.0)
            self.current_mood.arousal_baseline = mood_data.get("arousal_baseline", 0.0)

            logger.info(f"Emotional state loaded from {self.persist_path}")

        except FileNotFoundError:
            logger.info("No emotional state found, starting with neutral state")
        except Exception as e:
            logger.warning(f"Failed to load emotional state: {e}")

    def save_emotional_state(self):
        """Guarda estado emocional actual"""
        try:
            data = {
                "timestamp": time.time(),
                "current_emotion": {
                    "emotion": self.current_emotion.primary_emotion.value,
                    "intensity": self.current_emotion.intensity,
                    "valence": self.current_emotion.valence,
                    "arousal": self.current_emotion.arousal,
                },
                "current_mood": {
                    "label": self.current_mood.mood_label,
                    "valence_bias": self.current_mood.valence_bias,
                    "arousal_baseline": self.current_mood.arousal_baseline,
                    "stability": self.current_mood.stability,
                },
                "emotional_reactivity": self.emotional_reactivity,
                "mood_stability": self.mood_stability,
                "regulation_tendency": self.regulation_tendency,
                "recent_emotions": list(self.emotion_history)[
                    -10:
                ],  # Últimas 10 emociones
            }

            with open(self.persist_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug(f"Emotional state saved to {self.persist_path}")

        except Exception as e:
            logger.error(f"Failed to save emotional state: {e}")


# Función de fábrica
def create_emotional_brain() -> EmotionalBrain:
    """Crea y configura sistema emocional"""
    return EmotionalBrain()
