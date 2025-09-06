"""
Advanced Reasoning System - Sistema de Lógica y Razonamiento Avanzado

Este módulo implementa múltiples formas de razonamiento:
- Razonamiento Deductivo: de general a específico
- Razonamiento Inductivo: de específico a general
- Razonamiento Abductivo: inferencia a la mejor explicación
- Lógica Difusa: manejo de incertidumbre
- Razonamiento Causal: comprensión de causa-efecto
- Lógica Modal: posibilidad y necesidad
"""

import logging
import math
import statistics
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ReasoningType(Enum):
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    FUZZY = "fuzzy"
    CAUSAL = "causal"
    MODAL = "modal"


@dataclass
class LogicalStatement:
    """Representa una afirmación lógica con truth value y confidence"""

    content: str
    truth_value: float  # 0.0 a 1.0
    confidence: float  # 0.0 a 1.0
    evidence: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    source: str = "inference"


# Fábrica para crear el sistema avanzado de razonamiento
def create_advanced_reasoning_system(*args, **kwargs):
    return AdvancedReasoningSystem(*args, **kwargs)


@dataclass
class Rule:
    """Regla lógica con antecedentes y consecuentes"""

    antecedents: List[LogicalStatement]
    consequent: LogicalStatement
    strength: float = 1.0
    rule_type: ReasoningType = ReasoningType.DEDUCTIVE
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Hypothesis:
    """Hipótesis para razonamiento abductivo"""

    explanation: str
    likelihood: float
    parsimony_score: float  # Simplicidad de la explicación
    explanatory_power: float
    evidence_support: List[str] = field(default_factory=list)

    @property
    def quality_score(self) -> float:
        """Score combinado de calidad de la hipótesis"""
        return (
            self.likelihood * 0.4
            + self.parsimony_score * 0.3
            + self.explanatory_power * 0.3
        )


class FuzzySet:
    """Conjunto difuso para lógica fuzzy"""

    def __init__(self, name: str, membership_function=None):
        self.name = name
        self.membership_function = membership_function or self._default_membership
        self.linguistic_values = {}

    def _default_membership(self, x: float) -> float:
        """Función de membresía por defecto (triangular)"""
        if 0 <= x <= 0.5:
            return 2 * x
        elif 0.5 < x <= 1:
            return 2 * (1 - x)
        return 0.0

    def membership(self, value: float) -> float:
        """Calcula el grado de membresía"""
        return self.membership_function(value)

    def add_linguistic_value(self, term: str, func):
        """Añade un valor lingüístico al conjunto"""
        self.linguistic_values[term] = func


class DeductiveReasoner:
    """Razonamiento deductivo - de principios generales a conclusiones específicas"""

    def __init__(self):
        self.rules: List[Rule] = []
        self.facts: List[LogicalStatement] = []

    def add_rule(self, rule: Rule):
        """Añade una regla deductiva"""
        self.rules.append(rule)

    def add_fact(self, fact: LogicalStatement):
        """Añade un hecho conocido"""
        self.facts.append(fact)

    def modus_ponens(
        self, rule: Rule, facts: List[LogicalStatement]
    ) -> Optional[LogicalStatement]:
        """Aplica modus ponens: Si P entonces Q, P es verdad, por tanto Q"""

        # Verificar que todos los antecedentes se cumplan
        satisfied_antecedents = 0
        min_confidence = 1.0
        evidence = []

        for antecedent in rule.antecedents:
            for fact in facts:
                if self._statements_match(antecedent, fact):
                    if fact.truth_value > 0.7:  # Umbral de verdad
                        satisfied_antecedents += 1
                        min_confidence = min(min_confidence, fact.confidence)
                        evidence.extend(fact.evidence)
                        evidence.append(f"Fact: {fact.content}")
                    break

        # Si todos los antecedentes se satisfacen, inferir el consecuente
        if satisfied_antecedents == len(rule.antecedents):
            new_confidence = min_confidence * rule.strength
            new_statement = LogicalStatement(
                content=rule.consequent.content,
                truth_value=rule.consequent.truth_value * new_confidence,
                confidence=new_confidence,
                evidence=evidence
                + [f"Deductive rule: {rule.antecedents} → {rule.consequent}"],
                source="deductive_reasoning",
            )
            return new_statement

        return None

    def _statements_match(
        self, statement1: LogicalStatement, statement2: LogicalStatement
    ) -> bool:
        """Verifica si dos statements se refieren a lo mismo"""
        # Simplificado - en implementación real usaría NLP para semantic matching
        return statement1.content.lower() == statement2.content.lower()

    def forward_chaining(self) -> List[LogicalStatement]:
        """Forward chaining: aplica reglas hasta no poder inferir más"""
        derived_facts = []
        facts_changed = True
        iterations = 0
        max_iterations = 100

        current_facts = self.facts.copy()

        while facts_changed and iterations < max_iterations:
            facts_changed = False
            iterations += 1

            for rule in self.rules:
                new_fact = self.modus_ponens(rule, current_facts)
                if new_fact and not self._fact_already_known(
                    new_fact, current_facts + derived_facts
                ):
                    derived_facts.append(new_fact)
                    current_facts.append(new_fact)
                    facts_changed = True

        return derived_facts

    def _fact_already_known(
        self, new_fact: LogicalStatement, existing_facts: List[LogicalStatement]
    ) -> bool:
        """Verifica si un hecho ya es conocido"""
        for fact in existing_facts:
            if self._statements_match(new_fact, fact):
                return True
        return False


class InductiveReasoner:
    """Razonamiento inductivo - de observaciones específicas a reglas generales"""

    def __init__(self):
        self.observations: List[Dict[str, Any]] = []
        self.patterns: List[Dict[str, Any]] = []

    def add_observation(self, observation: Dict[str, Any]):
        """Añade una observación"""
        self.observations.append({**observation, "timestamp": time.time()})

    def find_patterns(self, min_support: float = 0.7) -> List[Dict[str, Any]]:
        """Encuentra patrones inductivos en las observaciones"""
        patterns = []

        if len(self.observations) < 3:
            return patterns

        # Analizar patrones de correlación
        correlations = self._find_correlations()

        # Analizar secuencias temporales
        sequences = self._find_temporal_patterns()

        # Analizar frecuencias
        frequencies = self._find_frequency_patterns()

        # Filtrar patrones con suficiente soporte
        for pattern_type, pattern_data in [
            ("correlation", correlations),
            ("sequence", sequences),
            ("frequency", frequencies),
        ]:
            for pattern in pattern_data:
                if pattern.get("support", 0) >= min_support:
                    patterns.append(
                        {
                            "type": pattern_type,
                            "pattern": pattern,
                            "confidence": pattern.get("confidence", 0.8),
                            "inductive_strength": self._calculate_inductive_strength(
                                pattern
                            ),
                        }
                    )

        self.patterns = patterns
        return patterns

    def _find_correlations(self) -> List[Dict[str, Any]]:
        """Encuentra correlaciones entre variables"""
        correlations = []

        # Obtener todas las variables numéricas
        numeric_vars = set()
        for obs in self.observations:
            for key, value in obs.items():
                if isinstance(value, (int, float)) and key != "timestamp":
                    numeric_vars.add(key)

        # Calcular correlaciones entre pares de variables
        for var1 in numeric_vars:
            for var2 in numeric_vars:
                if var1 < var2:  # Evitar duplicados
                    correlation = self._calculate_correlation(var1, var2)
                    if abs(correlation) > 0.7:  # Correlación fuerte
                        correlations.append(
                            {
                                "variables": [var1, var2],
                                "correlation": correlation,
                                "support": len(self.observations)
                                / max(10, len(self.observations)),
                                "confidence": min(0.95, abs(correlation)),
                            }
                        )

        return correlations

    def _calculate_correlation(self, var1: str, var2: str) -> float:
        """Calcula correlación de Pearson entre dos variables"""
        values1 = []
        values2 = []

        for obs in self.observations:
            if var1 in obs and var2 in obs:
                if isinstance(obs[var1], (int, float)) and isinstance(
                    obs[var2], (int, float)
                ):
                    values1.append(obs[var1])
                    values2.append(obs[var2])

        if len(values1) < 3:
            return 0.0

        try:
            mean1 = statistics.mean(values1)
            mean2 = statistics.mean(values2)

            numerator = sum((x - mean1) * (y - mean2) for x, y in zip(values1, values2))
            denominator = math.sqrt(
                sum((x - mean1) ** 2 for x in values1)
                * sum((y - mean2) ** 2 for y in values2)
            )

            return numerator / denominator if denominator != 0 else 0.0

        except:
            return 0.0

    def _find_temporal_patterns(self) -> List[Dict[str, Any]]:
        """Encuentra patrones temporales en secuencias"""
        patterns = []

        # Ordenar observaciones por timestamp
        sorted_obs = sorted(self.observations, key=lambda x: x.get("timestamp", 0))

        # Buscar secuencias repetitivas
        sequence_length = 3
        for i in range(len(sorted_obs) - sequence_length + 1):
            sequence = sorted_obs[i : i + sequence_length]

            # Extraer patrón de la secuencia
            pattern_signature = self._extract_sequence_signature(sequence)

            if pattern_signature:
                # Buscar repeticiones del patrón
                repetitions = self._count_sequence_repetitions(
                    pattern_signature, sorted_obs
                )

                if repetitions >= 2:
                    patterns.append(
                        {
                            "sequence_signature": pattern_signature,
                            "repetitions": repetitions,
                            "support": repetitions
                            / max(1, len(sorted_obs) - sequence_length + 1),
                            "confidence": min(0.9, repetitions / 5),
                        }
                    )

        return patterns

    def _extract_sequence_signature(
        self, sequence: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Extrae la firma de una secuencia"""
        try:
            # Simplificado: usar cambios relativos en variables numéricas
            signatures = []

            for i in range(1, len(sequence)):
                prev = sequence[i - 1]
                curr = sequence[i]

                for key in prev:
                    if (
                        key in curr
                        and isinstance(prev[key], (int, float))
                        and isinstance(curr[key], (int, float))
                    ):
                        change = (
                            "inc"
                            if curr[key] > prev[key]
                            else "dec" if curr[key] < prev[key] else "same"
                        )
                        signatures.append(f"{key}:{change}")

            return "|".join(signatures) if signatures else None

        except:
            return None

    def _count_sequence_repetitions(
        self, signature: str, observations: List[Dict[str, Any]]
    ) -> int:
        """Cuenta repeticiones de un patrón de secuencia"""
        # Implementación simplificada
        return 1  # En implementación real analizaría todas las secuencias

    def _find_frequency_patterns(self) -> List[Dict[str, Any]]:
        """Encuentra patrones de frecuencia en valores categóricos"""
        patterns = []

        # Analizar frecuencias de valores categóricos
        categorical_freqs = {}

        for obs in self.observations:
            for key, value in obs.items():
                if isinstance(value, str) and key != "source":
                    if key not in categorical_freqs:
                        categorical_freqs[key] = {}
                    if value not in categorical_freqs[key]:
                        categorical_freqs[key][value] = 0
                    categorical_freqs[key][value] += 1

        # Identificar valores dominantes
        for variable, value_counts in categorical_freqs.items():
            total_count = sum(value_counts.values())

            for value, count in value_counts.items():
                frequency = count / total_count

                if frequency > 0.6:  # Valor dominante
                    patterns.append(
                        {
                            "variable": variable,
                            "dominant_value": value,
                            "frequency": frequency,
                            "support": frequency,
                            "confidence": frequency,
                        }
                    )

        return patterns

    def _calculate_inductive_strength(self, pattern: Dict[str, Any]) -> float:
        """Calcula la fuerza inductiva de un patrón"""
        support = pattern.get("support", 0)
        confidence = pattern.get("confidence", 0)

        # Más observaciones = mayor fuerza inductiva
        sample_size_factor = min(1.0, len(self.observations) / 20)

        return (support * confidence * sample_size_factor) ** 0.5


class AbductiveReasoner:
    """Razonamiento abductivo - inferencia a la mejor explicación"""

    def __init__(self):
        self.hypotheses: List[Hypothesis] = []
        self.observations: List[Dict[str, Any]] = []

    def add_observation(self, observation: Dict[str, Any]):
        """Añade una observación que necesita explicación"""
        self.observations.append(observation)

    def generate_hypotheses(self, observation: Dict[str, Any]) -> List[Hypothesis]:
        """Genera hipótesis para explicar una observación"""
        hypotheses = []

        # Generar hipótesis basadas en patrones conocidos
        hypotheses.extend(self._generate_pattern_hypotheses(observation))

        # Generar hipótesis causales
        hypotheses.extend(self._generate_causal_hypotheses(observation))

        # Generar hipóteses por analogía
        hypotheses.extend(self._generate_analogical_hypotheses(observation))

        # Ordenar por calidad
        hypotheses.sort(key=lambda h: h.quality_score, reverse=True)

        return hypotheses[:5]  # Top 5 hipótesis

    def _generate_pattern_hypotheses(
        self, observation: Dict[str, Any]
    ) -> List[Hypothesis]:
        """Genera hipótesis basadas en patrones previos"""
        hypotheses = []

        # Buscar observaciones similares en el historial
        similar_obs = self._find_similar_observations(observation)

        for sim_obs in similar_obs[:3]:  # Top 3 más similares
            explanation = f"Similar pattern to previous observation: {sim_obs.get('description', 'unknown')}"

            similarity_score = self._calculate_similarity(observation, sim_obs)

            hypothesis = Hypothesis(
                explanation=explanation,
                likelihood=similarity_score,
                parsimony_score=0.8,  # Patrones previos son simples
                explanatory_power=similarity_score * 0.9,
                evidence_support=[f"Previous observation: {sim_obs}"],
            )

            hypotheses.append(hypothesis)

        return hypotheses

    def _generate_causal_hypotheses(
        self, observation: Dict[str, Any]
    ) -> List[Hypothesis]:
        """Genera hipótesis causales"""
        hypotheses = []

        # Hipótesis causales comunes para scraping
        causal_templates = [
            {
                "condition": lambda obs: obs.get("status_code") == 403,
                "explanation": "Anti-bot detection triggered by suspicious request patterns",
                "likelihood": 0.8,
                "parsimony": 0.7,
                "power": 0.9,
            },
            {
                "condition": lambda obs: obs.get("response_time", 0) > 10,
                "explanation": "Server overload or rate limiting causing slow responses",
                "likelihood": 0.7,
                "parsimony": 0.8,
                "power": 0.8,
            },
            {
                "condition": lambda obs: obs.get("success_rate", 1) < 0.5,
                "explanation": "Website structure changed or new protection measures",
                "likelihood": 0.6,
                "parsimony": 0.6,
                "power": 0.9,
            },
        ]

        for template in causal_templates:
            if template["condition"](observation):
                hypothesis = Hypothesis(
                    explanation=template["explanation"],
                    likelihood=template["likelihood"],
                    parsimony_score=template["parsimony"],
                    explanatory_power=template["power"],
                    evidence_support=[f"Observation matches pattern: {observation}"],
                )
                hypotheses.append(hypothesis)

        return hypotheses

    def _generate_analogical_hypotheses(
        self, observation: Dict[str, Any]
    ) -> List[Hypothesis]:
        """Genera hipótesis por analogía con otros dominios"""
        hypotheses = []

        # Analogías con sistemas conocidos
        analogies = [
            {
                "domain": "immune_system",
                "explanation": "Website acting like immune system rejecting foreign requests",
                "likelihood": 0.6,
                "parsimony": 0.5,
                "power": 0.7,
            },
            {
                "domain": "traffic_control",
                "explanation": "Rate limiting like traffic lights controlling flow",
                "likelihood": 0.7,
                "parsimony": 0.8,
                "power": 0.6,
            },
        ]

        for analogy in analogies:
            if self._observation_fits_analogy(observation, analogy):
                hypothesis = Hypothesis(
                    explanation=f"{analogy['explanation']} (analogy with {analogy['domain']})",
                    likelihood=analogy["likelihood"],
                    parsimony_score=analogy["parsimony"],
                    explanatory_power=analogy["power"],
                    evidence_support=[f"Analogical reasoning from {analogy['domain']}"],
                )
                hypotheses.append(hypothesis)

        return hypotheses

    def _find_similar_observations(
        self, target: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Encuentra observaciones similares en el historial"""
        similarities = []

        for obs in self.observations:
            similarity = self._calculate_similarity(target, obs)
            if similarity > 0.3:  # Umbral mínimo de similitud
                similarities.append((similarity, obs))

        # Ordenar por similitud descendente
        similarities.sort(reverse=True)
        return [obs for _, obs in similarities]

    def _calculate_similarity(
        self, obs1: Dict[str, Any], obs2: Dict[str, Any]
    ) -> float:
        """Calcula similitud entre dos observaciones"""
        common_keys = set(obs1.keys()) & set(obs2.keys())

        if not common_keys:
            return 0.0

        similarities = []

        for key in common_keys:
            val1, val2 = obs1[key], obs2[key]

            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Similitud numérica
                max_val = max(abs(val1), abs(val2), 1)
                sim = 1 - abs(val1 - val2) / max_val
                similarities.append(sim)
            elif isinstance(val1, str) and isinstance(val2, str):
                # Similitud de strings (simplificada)
                sim = 1.0 if val1 == val2 else 0.0
                similarities.append(sim)

        return statistics.mean(similarities) if similarities else 0.0

    def _observation_fits_analogy(
        self, observation: Dict[str, Any], analogy: Dict[str, Any]
    ) -> bool:
        """Verifica si una observación encaja con una analogía"""
        # Simplificado: verificar si hay indicadores relevantes
        if analogy["domain"] == "immune_system":
            return observation.get("status_code") in [403, 429, 503]
        elif analogy["domain"] == "traffic_control":
            return observation.get("response_time", 0) > 5

        return False


class FuzzyReasoner:
    """Razonador con lógica difusa para manejar incertidumbre"""

    def __init__(self):
        self.fuzzy_sets: Dict[str, FuzzySet] = {}
        self.fuzzy_rules: List[Dict[str, Any]] = []

    def add_fuzzy_set(self, name: str, fuzzy_set: FuzzySet):
        """Añade un conjunto difuso"""
        self.fuzzy_sets[name] = fuzzy_set

    def add_fuzzy_rule(self, antecedent: str, consequent: str, strength: float = 1.0):
        """Añade una regla difusa"""
        self.fuzzy_rules.append(
            {"antecedent": antecedent, "consequent": consequent, "strength": strength}
        )

    def fuzzify(self, variable: str, value: float) -> Dict[str, float]:
        """Convierte valor crisp a valores difusos"""
        if variable not in self.fuzzy_sets:
            return {}

        fuzzy_set = self.fuzzy_sets[variable]
        memberships = {}

        for term, func in fuzzy_set.linguistic_values.items():
            memberships[term] = func(value)

        return memberships

    def fuzzy_inference(self, inputs: Dict[str, float]) -> Dict[str, float]:
        """Realiza inferencia difusa"""
        output_activations = {}

        for rule in self.fuzzy_rules:
            # Evaluar antecedente (simplificado)
            antecedent_strength = 1.0

            # Aplicar regla con strength
            if rule["consequent"] not in output_activations:
                output_activations[rule["consequent"]] = 0

            activation = antecedent_strength * rule["strength"]
            output_activations[rule["consequent"]] = max(
                output_activations[rule["consequent"]], activation
            )

        return output_activations

    def defuzzify(self, fuzzy_output: Dict[str, float]) -> float:
        """Convierte salida difusa a valor crisp (centroid method)"""
        if not fuzzy_output:
            return 0.0

        numerator = sum(
            (
                value * float(key.split("_")[-1])
                if key.split("_")[-1].isdigit()
                else value * 0.5
            )
            for key, value in fuzzy_output.items()
        )
        denominator = sum(fuzzy_output.values())

        return numerator / denominator if denominator != 0 else 0.0


class AdvancedReasoningSystem:
    """Sistema integrado de razonamiento avanzado"""

    def __init__(self):
        self.deductive = DeductiveReasoner()
        self.inductive = InductiveReasoner()
        self.abductive = AbductiveReasoner()
        self.fuzzy = FuzzyReasoner()

        self.reasoning_history: List[Dict[str, Any]] = []
        self.confidence_threshold = 0.7

        logger.info("🧠 Advanced Reasoning System initialized")

    def reason_about(
        self, problem: Dict[str, Any], reasoning_types: List[ReasoningType] = None
    ) -> Dict[str, Any]:
        """Aplica múltiples tipos de razonamiento a un problema"""

        if reasoning_types is None:
            reasoning_types = [
                ReasoningType.DEDUCTIVE,
                ReasoningType.INDUCTIVE,
                ReasoningType.ABDUCTIVE,
            ]

        results = {
            "problem": problem,
            "reasoning_results": {},
            "integrated_conclusion": None,
            "confidence": 0.0,
            "timestamp": time.time(),
        }

        # Aplicar cada tipo de razonamiento
        for reasoning_type in reasoning_types:
            if reasoning_type == ReasoningType.DEDUCTIVE:
                results["reasoning_results"]["deductive"] = (
                    self._apply_deductive_reasoning(problem)
                )
            elif reasoning_type == ReasoningType.INDUCTIVE:
                results["reasoning_results"]["inductive"] = (
                    self._apply_inductive_reasoning(problem)
                )
            elif reasoning_type == ReasoningType.ABDUCTIVE:
                results["reasoning_results"]["abductive"] = (
                    self._apply_abductive_reasoning(problem)
                )
            elif reasoning_type == ReasoningType.FUZZY:
                results["reasoning_results"]["fuzzy"] = self._apply_fuzzy_reasoning(
                    problem
                )

        # Integrar resultados
        results["integrated_conclusion"] = self._integrate_reasoning_results(
            results["reasoning_results"]
        )
        results["confidence"] = self._calculate_overall_confidence(
            results["reasoning_results"]
        )

        # Guardar en historial
        self.reasoning_history.append(results)

        return results

    def _apply_deductive_reasoning(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica razonamiento deductivo"""
        try:
            # Convertir problema a hechos lógicos
            facts = self._problem_to_facts(problem)
            for fact in facts:
                self.deductive.add_fact(fact)

            # Aplicar forward chaining
            derived_facts = self.deductive.forward_chaining()

            return {
                "type": "deductive",
                "derived_facts": [f.content for f in derived_facts],
                "confidence": (
                    statistics.mean([f.confidence for f in derived_facts])
                    if derived_facts
                    else 0
                ),
                "reasoning_steps": len(derived_facts),
            }

        except Exception as e:
            logger.warning(f"Deductive reasoning failed: {e}")
            return {"type": "deductive", "error": str(e)}

    def _apply_inductive_reasoning(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica razonamiento inductivo"""
        try:
            # Añadir problema como observación
            self.inductive.add_observation(problem)

            # Buscar patrones
            patterns = self.inductive.find_patterns()

            return {
                "type": "inductive",
                "patterns_found": len(patterns),
                "patterns": patterns,
                "confidence": (
                    statistics.mean([p.get("confidence", 0) for p in patterns])
                    if patterns
                    else 0
                ),
            }

        except Exception as e:
            logger.warning(f"Inductive reasoning failed: {e}")
            return {"type": "inductive", "error": str(e)}

    def _apply_abductive_reasoning(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica razonamiento abductivo"""
        try:
            # Generar hipótesis explicativas
            hypotheses = self.abductive.generate_hypotheses(problem)

            return {
                "type": "abductive",
                "hypotheses_count": len(hypotheses),
                "best_hypothesis": hypotheses[0].explanation if hypotheses else None,
                "hypotheses": [
                    {
                        "explanation": h.explanation,
                        "quality_score": h.quality_score,
                        "likelihood": h.likelihood,
                    }
                    for h in hypotheses
                ],
                "confidence": hypotheses[0].quality_score if hypotheses else 0,
            }

        except Exception as e:
            logger.warning(f"Abductive reasoning failed: {e}")
            return {"type": "abductive", "error": str(e)}

    def _apply_fuzzy_reasoning(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica razonamiento difuso"""
        try:
            # Convertir valores numéricos a fuzzy
            fuzzy_inputs = {}
            for key, value in problem.items():
                if isinstance(value, (int, float)):
                    fuzzy_inputs[key] = self.fuzzy.fuzzify(key, value)

            # Inferencia difusa
            fuzzy_output = self.fuzzy.fuzzy_inference(problem)

            # Defuzzificación
            crisp_output = self.fuzzy.defuzzify(fuzzy_output)

            return {
                "type": "fuzzy",
                "fuzzy_inputs": fuzzy_inputs,
                "fuzzy_output": fuzzy_output,
                "crisp_output": crisp_output,
                "confidence": 0.8,  # Fuzzy reasoning inherently uncertain
            }

        except Exception as e:
            logger.warning(f"Fuzzy reasoning failed: {e}")
            return {"type": "fuzzy", "error": str(e)}

    def _problem_to_facts(self, problem: Dict[str, Any]) -> List[LogicalStatement]:
        """Convierte un problema a hechos lógicos"""
        facts = []

        for key, value in problem.items():
            if isinstance(value, bool):
                fact = LogicalStatement(
                    content=f"{key} is {value}",
                    truth_value=1.0 if value else 0.0,
                    confidence=0.9,
                    evidence=[f"Direct observation: {key}={value}"],
                )
                facts.append(fact)
            elif isinstance(value, (int, float)):
                # Convertir valores numéricos a afirmaciones cualitativas
                if value > 0.7:
                    quality = "high"
                elif value > 0.3:
                    quality = "medium"
                else:
                    quality = "low"

                fact = LogicalStatement(
                    content=f"{key} is {quality}",
                    truth_value=0.8,
                    confidence=0.8,
                    evidence=[f"Numeric observation: {key}={value}"],
                )
                facts.append(fact)

        return facts

    def _integrate_reasoning_results(self, results: Dict[str, Any]) -> str:
        """Integra resultados de múltiples tipos de razonamiento"""
        conclusions = []

        # Extraer conclusiones de cada tipo de razonamiento
        if "deductive" in results and "derived_facts" in results["deductive"]:
            if results["deductive"]["derived_facts"]:
                conclusions.append(
                    f"Deductive: {', '.join(results['deductive']['derived_facts'])}"
                )

        if "inductive" in results and results["inductive"].get("patterns"):
            pattern_count = len(results["inductive"]["patterns"])
            conclusions.append(f"Inductive: Found {pattern_count} patterns in data")

        if "abductive" in results and results["abductive"].get("best_hypothesis"):
            conclusions.append(f"Abductive: {results['abductive']['best_hypothesis']}")

        if "fuzzy" in results and "crisp_output" in results["fuzzy"]:
            conclusions.append(
                f"Fuzzy: Output value {results['fuzzy']['crisp_output']:.2f}"
            )

        return " | ".join(conclusions) if conclusions else "No clear conclusions"

    def _calculate_overall_confidence(self, results: Dict[str, Any]) -> float:
        """Calcula confianza general de todos los razonamientos"""
        confidences = []

        for reasoning_type, result in results.items():
            if "confidence" in result and not result.get("error"):
                confidences.append(result["confidence"])

        if not confidences:
            return 0.0

        # Confianza ponderada (más tipos de razonamiento = mayor confianza)
        base_confidence = statistics.mean(confidences)
        variety_bonus = min(0.2, len(confidences) * 0.05)

        return min(1.0, base_confidence + variety_bonus)

    def get_reasoning_insights(self) -> Dict[str, Any]:
        """Obtiene insights del historial de razonamiento"""
        if not self.reasoning_history:
            return {"insights": "No reasoning history available"}

        insights = {
            "total_reasoning_sessions": len(self.reasoning_history),
            "average_confidence": statistics.mean(
                [r["confidence"] for r in self.reasoning_history]
            ),
            "reasoning_type_usage": {},
            "most_confident_conclusions": [],
            "pattern_trends": {},
        }

        # Analizar uso de tipos de razonamiento
        for session in self.reasoning_history:
            for reasoning_type in session["reasoning_results"]:
                if reasoning_type not in insights["reasoning_type_usage"]:
                    insights["reasoning_type_usage"][reasoning_type] = 0
                insights["reasoning_type_usage"][reasoning_type] += 1

        # Encontrar conclusiones más confiables
        high_confidence_sessions = [
            s for s in self.reasoning_history if s["confidence"] > 0.8
        ]
        insights["most_confident_conclusions"] = [
            s["integrated_conclusion"] for s in high_confidence_sessions[-5:]
        ]

        return insights

    def integrated_reasoning(
        self, query: str, context: Dict[str, Any], reasoning_types: List[str] = None
    ) -> Dict[str, Any]:
        """Razonamiento integrado que acepta query, context y tipos de razonamiento"""
        # Convertir strings a enum types
        enum_types = []
        if reasoning_types:
            for rt in reasoning_types:
                try:
                    enum_types.append(ReasoningType(rt))
                except ValueError:
                    logger.warning(f"Unknown reasoning type: {rt}")

        # Crear problema estructurado
        problem = {"query": query, "context": context, "type": "integrated_analysis"}

        # Usar el método reason_about existente
        result = self.reason_about(problem, enum_types or None)

        # Formato de retorno esperado
        return {
            "query": query,
            "integrated_response": {
                "conclusion": result.get(
                    "integrated_conclusion", "No conclusion reached"
                ),
                "confidence": result.get("confidence", 0.0),
                "reasoning_breakdown": result.get("reasoning_results", {}),
                "conscious_access": result.get("confidence", 0.0)
                > self.confidence_threshold,
            },
            "reasoning_types_used": reasoning_types
            or ["deductive", "inductive", "abductive"],
            "timestamp": result.get("timestamp", time.time()),
        }


# Función de fábrica
def create_reasoning_system() -> AdvancedReasoningSystem:
    """Crea y configura un sistema de razonamiento avanzado"""
    system = AdvancedReasoningSystem()

    # Configurar reglas deductivas básicas para scraping
    system.deductive.add_rule(
        Rule(
            antecedents=[LogicalStatement("status_code is 403", 0.9, 0.9)],
            consequent=LogicalStatement("anti_bot_detected", 1.0, 0.9),
            strength=0.9,
        )
    )

    system.deductive.add_rule(
        Rule(
            antecedents=[LogicalStatement("response_time is high", 0.8, 0.8)],
            consequent=LogicalStatement("server_overloaded", 0.8, 0.8),
            strength=0.8,
        )
    )

    # Configurar conjuntos difusos básicos
    performance_set = FuzzySet("performance")
    performance_set.add_linguistic_value(
        "low", lambda x: max(0, min(1, (0.3 - x) / 0.3))
    )
    performance_set.add_linguistic_value(
        "medium", lambda x: max(0, min((x - 0.2) / 0.3, (0.8 - x) / 0.3))
    )
    performance_set.add_linguistic_value(
        "high", lambda x: max(0, min(1, (x - 0.7) / 0.3))
    )

    system.fuzzy.add_fuzzy_set("performance", performance_set)

    return system
