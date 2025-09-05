"""
Neural Brain System - Red neuronal real con sinapsis, neuronas y procesamiento distribuido

Este módulo implementa un cerebro neuronal verdadero con:
- Neuronas artificiales con estados dinámicos
- Sinapsis con pesos adaptativos
- Red de conexiones neuronales
- Procesamiento distribuido y paralelo
- Memoria asociativa y consolidación
- Plasticidad sináptica y aprendizaje Hebbiano
"""

import numpy as np
import json
import asyncio
import threading
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import random
import math

logger = logging.getLogger(__name__)

@dataclass
class Neuron:
    """Neurona artificial con estado dinámico y capacidad de procesamiento"""
    id: str
    neuron_type: str = "regular"  # regular, input, output, memory, logic
    activation: float = 0.0
    threshold: float = 0.5
    refractory_period: float = 0.1
    last_fired: float = 0.0
    decay_rate: float = 0.95

    # Estado interno
    membrane_potential: float = 0.0
    dendrite_inputs: List[float] = field(default_factory=list)
    axon_outputs: Dict[str, float] = field(default_factory=dict)

    # Memoria y contexto
    recent_patterns: deque = field(default_factory=lambda: deque(maxlen=100))
    learning_rate: float = 0.01

    def process_inputs(self, inputs: Dict[str, float]) -> float:
        """Procesa entradas dendríticas y calcula activación"""
        # Sumar todas las entradas ponderadas
        total_input = sum(inputs.values())
        self.dendrite_inputs.append(total_input)

        # Actualizar potencial de membrana
        self.membrane_potential += total_input
        self.membrane_potential *= self.decay_rate  # Decaimiento natural

        # Verificar período refractario
        current_time = time.time()
        if current_time - self.last_fired < self.refractory_period:
            return 0.0

        # Función de activación sigmoidea
        if self.membrane_potential > self.threshold:
            self.activation = 1 / (1 + math.exp(-self.membrane_potential))
            self.last_fired = current_time

            # Registrar patrón de activación
            self.recent_patterns.append({
                'timestamp': current_time,
                'inputs': dict(inputs),
                'activation': self.activation
            })

            return self.activation

        return 0.0

    def adapt_threshold(self, target_frequency: float = 0.1):
        """Adaptación homeostática del umbral de activación"""
        recent_firing_rate = len([p for p in self.recent_patterns
                                if time.time() - p['timestamp'] < 10]) / 10

        if recent_firing_rate > target_frequency:
            self.threshold *= 1.01  # Aumentar umbral
        elif recent_firing_rate < target_frequency:
            self.threshold *= 0.99  # Disminuir umbral

@dataclass
class Synapse:
    """Sinapsis con peso adaptativo y plasticidad"""
    pre_neuron_id: str
    post_neuron_id: str
    weight: float = 0.1
    synapse_type: str = "excitatory"  # excitatory, inhibitory
    plasticity: float = 0.01

    # Historial de activación para aprendizaje Hebbiano
    pre_activity_history: deque = field(default_factory=lambda: deque(maxlen=50))
    post_activity_history: deque = field(default_factory=lambda: deque(maxlen=50))

    # Metaplasticidad
    weight_change_history: deque = field(default_factory=lambda: deque(maxlen=100))

    def transmit(self, pre_activation: float) -> float:
        """Transmite señal a través de la sinapsis"""
        if self.synapse_type == "inhibitory":
            return -abs(self.weight * pre_activation)
        return self.weight * pre_activation

    def hebbian_learning(self, pre_activation: float, post_activation: float):
        """Aprendizaje Hebbiano: "neuronas que disparan juntas, se conectan juntas" """
        self.pre_activity_history.append(pre_activation)
        self.post_activity_history.append(post_activation)

        # Correlación temporal
        correlation = pre_activation * post_activation

        # Regla de Hebb con normalización
        weight_change = self.plasticity * correlation

        # Anti-Hebb para debilitar conexiones no correlacionadas
        if correlation < 0.1:
            weight_change *= -0.5

        self.weight += weight_change
        self.weight_change_history.append(weight_change)

        # Límites de peso sináptico
        self.weight = max(-2.0, min(2.0, self.weight))

    def spike_timing_dependent_plasticity(self, pre_time: float, post_time: float):
        """STDP: Plasticidad dependiente del tiempo de picos"""
        dt = post_time - pre_time

        if abs(dt) > 0.1:  # Ventana temporal limitada
            return

        if dt > 0:  # Post después de pre -> fortalecimiento
            weight_change = self.plasticity * math.exp(-dt / 0.02)
        else:  # Pre después de post -> debilitamiento
            weight_change = -self.plasticity * math.exp(dt / 0.02)

        self.weight += weight_change
        self.weight = max(-2.0, min(2.0, self.weight))

class NeuralCluster:
    """Cluster de neuronas especializadas en una función específica"""

    def __init__(self, cluster_id: str, size: int, specialty: str):
        self.cluster_id = cluster_id
        self.specialty = specialty  # memory, logic, pattern, emotion, meta
        self.neurons = {}
        self.internal_connections = []
        self.cluster_activation = 0.0
        self.consensus_threshold = 0.6

        # Crear neuronas del cluster
        for i in range(size):
            neuron_id = f"{cluster_id}_n{i}"
            neuron_type = self._get_neuron_type_for_specialty(specialty)
            self.neurons[neuron_id] = Neuron(
                id=neuron_id,
                neuron_type=neuron_type,
                threshold=random.uniform(0.3, 0.7),
                learning_rate=random.uniform(0.005, 0.02)
            )

    def _get_neuron_type_for_specialty(self, specialty: str) -> str:
        """Determina el tipo de neurona según la especialidad del cluster"""
        type_mapping = {
            'memory': 'memory',
            'logic': 'logic',
            'pattern': 'regular',
            'emotion': 'regular',
            'meta': 'logic'
        }
        return type_mapping.get(specialty, 'regular')

    def process_cluster_input(self, inputs: Dict[str, float]) -> Dict[str, float]:
        """Procesa entradas a nivel de cluster con consenso neuronal"""
        neuron_outputs = {}

        for neuron_id, neuron in self.neurons.items():
            # Distribuir entradas a neuronas del cluster
            distributed_inputs = {
                f"external_{k}": v * random.uniform(0.8, 1.2)
                for k, v in inputs.items()
            }

            activation = neuron.process_inputs(distributed_inputs)
            neuron_outputs[neuron_id] = activation

        # Calcular consenso del cluster
        active_neurons = sum(1 for v in neuron_outputs.values() if v > 0.1)
        self.cluster_activation = active_neurons / len(self.neurons)

        return neuron_outputs

    def get_cluster_consensus(self) -> bool:
        """Determina si el cluster ha alcanzado consenso"""
        return self.cluster_activation >= self.consensus_threshold

class NeuralBrain:
    """Sistema cerebral neuronal completo con procesamiento distribuido"""

    def __init__(self):
        self.neurons: Dict[str, Neuron] = {}
        self.synapses: Dict[str, Synapse] = {}
        self.clusters: Dict[str, NeuralCluster] = {}

        # Sistemas especializados
        self.memory_system = {}
        self.attention_weights = {}
        self.global_workspace = {}

        # Estado del cerebro
        self.consciousness_level = 0.0
        self.arousal_level = 0.5
        self.processing_load = 0.0

        # Inicializar arquitectura cerebral
        self._initialize_brain_architecture()

        logger.info("🧠 Neural Brain initialized with distributed processing")

    def _initialize_brain_architecture(self):
        """Inicializa la arquitectura cerebral con clusters especializados"""

        # Cluster de memoria (almacenamiento y recuperación)
        self.clusters['memory'] = NeuralCluster('memory', 20, 'memory')

        # Cluster de lógica (razonamiento y decisiones)
        self.clusters['logic'] = NeuralCluster('logic', 15, 'logic')

        # Cluster de reconocimiento de patrones
        self.clusters['pattern'] = NeuralCluster('pattern', 25, 'pattern')

        # Cluster emocional (evaluación y motivación)
        self.clusters['emotion'] = NeuralCluster('emotion', 10, 'emotion')

        # Cluster metacognitivo (auto-consciencia)
        self.clusters['meta'] = NeuralCluster('meta', 8, 'meta')

        # Crear conexiones inter-cluster
        self._create_inter_cluster_connections()

        # Inicializar workspace global
        self.global_workspace = {
            'active_concepts': {},
            'attention_focus': {},
            'working_memory': deque(maxlen=7),  # Límite cognitivo de Miller
            'consciousness_contents': {}
        }

    def _create_inter_cluster_connections(self):
        """Crea conexiones sinápticas entre clusters"""
        cluster_pairs = [
            ('memory', 'logic', 0.8),    # Memoria -> Lógica
            ('pattern', 'memory', 0.7),  # Patrones -> Memoria
            ('logic', 'emotion', 0.6),   # Lógica -> Emoción
            ('emotion', 'logic', 0.5),   # Emoción -> Lógica
            ('meta', 'logic', 0.9),      # Metacognición -> Lógica
            ('meta', 'memory', 0.8),     # Metacognición -> Memoria
            ('pattern', 'logic', 0.7),   # Patrones -> Lógica
        ]

        for source_cluster, target_cluster, base_weight in cluster_pairs:
            self._connect_clusters(source_cluster, target_cluster, base_weight)

    def _connect_clusters(self, source_id: str, target_id: str, base_weight: float):
        """Conecta dos clusters con sinapsis aleatorias"""
        source_cluster = self.clusters[source_id]
        target_cluster = self.clusters[target_id]

        # Conectar subset aleatorio de neuronas
        source_neurons = list(source_cluster.neurons.keys())
        target_neurons = list(target_cluster.neurons.keys())

        num_connections = min(len(source_neurons), len(target_neurons)) // 2

        for _ in range(num_connections):
            pre_neuron = random.choice(source_neurons)
            post_neuron = random.choice(target_neurons)

            synapse_id = f"{pre_neuron}->{post_neuron}"
            weight = base_weight * random.uniform(0.5, 1.5)

            self.synapses[synapse_id] = Synapse(
                pre_neuron_id=pre_neuron,
                post_neuron_id=post_neuron,
                weight=weight,
                plasticity=random.uniform(0.005, 0.02)
            )

    async def process_thought(self, stimulus: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa un pensamiento completo a través de toda la red neuronal"""

        # Fase 1: Activación inicial de clusters
        cluster_responses = {}
        for cluster_id, cluster in self.clusters.items():
            adapted_stimulus = self._adapt_stimulus_for_cluster(stimulus, cluster_id)
            response = cluster.process_cluster_input(adapted_stimulus)
            cluster_responses[cluster_id] = response

        # Fase 2: Propagación inter-cluster
        await self._propagate_between_clusters(cluster_responses)

        # Fase 3: Actualización del workspace global
        self._update_global_workspace(stimulus, cluster_responses)

        # Fase 4: Consolidación y aprendizaje
        self._consolidate_learning(stimulus, cluster_responses)

        # Fase 5: Generar respuesta consciente
        conscious_response = self._generate_conscious_response()

        return conscious_response

    def _adapt_stimulus_for_cluster(self, stimulus: Dict[str, Any], cluster_id: str) -> Dict[str, float]:
        """Adapta el estímulo para el tipo específico de cluster"""

        if cluster_id == 'memory':
            # Cluster de memoria se enfoca en información histórica
            return {
                'novelty': float(stimulus.get('is_new', 0)),
                'similarity': float(stimulus.get('similarity_score', 0)),
                'importance': float(stimulus.get('priority', 0.5))
            }

        elif cluster_id == 'logic':
            # Cluster lógico procesa relaciones causales
            return {
                'complexity': float(len(str(stimulus)) / 1000),
                'structure': float(stimulus.get('has_structure', 0.5)),
                'consistency': float(stimulus.get('is_consistent', 0.5))
            }

        elif cluster_id == 'pattern':
            # Cluster de patrones busca regularidades
            return {
                'repetition': float(stimulus.get('repetition_score', 0)),
                'frequency': float(stimulus.get('frequency', 0.5)),
                'regularity': float(stimulus.get('pattern_strength', 0.5))
            }

        elif cluster_id == 'emotion':
            # Cluster emocional evalúa valencia y arousal
            return {
                'valence': float(stimulus.get('success_rate', 0.5)),
                'arousal': float(stimulus.get('urgency', 0.5)),
                'motivation': float(stimulus.get('reward_potential', 0.5))
            }

        elif cluster_id == 'meta':
            # Cluster metacognitivo analiza el propio pensamiento
            return {
                'self_awareness': float(stimulus.get('requires_thinking', 0.5)),
                'confidence': float(stimulus.get('certainty', 0.5)),
                'reflection': float(stimulus.get('needs_analysis', 0.5))
            }

        # Default: distribuir uniformemente
        return {k: float(v) if isinstance(v, (int, float)) else 0.5
                for k, v in stimulus.items() if isinstance(v, (int, float, bool))}

    async def _propagate_between_clusters(self, cluster_responses: Dict[str, Dict[str, float]]):
        """Propaga activaciones entre clusters a través de sinapsis"""

        propagation_rounds = 3  # Múltiples rondas para convergencia

        for round_num in range(propagation_rounds):
            new_activations = defaultdict(float)

            for synapse_id, synapse in self.synapses.items():
                pre_neuron_id = synapse.pre_neuron_id
                post_neuron_id = synapse.post_neuron_id

                # Encontrar activación de neurona pre-sináptica
                pre_activation = 0.0
                for cluster_resp in cluster_responses.values():
                    if pre_neuron_id in cluster_resp:
                        pre_activation = cluster_resp[pre_neuron_id]
                        break

                # Transmitir a través de sinapsis
                if pre_activation > 0.1:
                    transmitted = synapse.transmit(pre_activation)
                    new_activations[post_neuron_id] += transmitted

            # Actualizar activaciones con nuevas entradas
            for cluster_id, cluster in self.clusters.items():
                for neuron_id in cluster.neurons:
                    if neuron_id in new_activations:
                        additional_input = {f"inter_cluster_r{round_num}": new_activations[neuron_id]}
                        cluster.neurons[neuron_id].process_inputs(additional_input)

            # Pequeña pausa para simular tiempo de procesamiento
            await asyncio.sleep(0.001)

    def _update_global_workspace(self, stimulus: Dict[str, Any], cluster_responses: Dict[str, Dict[str, float]]):
        """Actualiza el workspace global con información consciente"""

        # Calcular consenso de clusters
        cluster_consensus = {}
        for cluster_id, cluster in self.clusters.items():
            cluster_consensus[cluster_id] = cluster.get_cluster_consensus()

        # Actualizar nivel de consciencia basado en consenso global
        active_clusters = sum(cluster_consensus.values())
        self.consciousness_level = active_clusters / len(self.clusters)

        # Agregar al workspace global si hay suficiente activación
        if self.consciousness_level > 0.4:
            self.global_workspace['active_concepts'][time.time()] = {
                'stimulus': stimulus,
                'cluster_states': cluster_consensus,
                'consciousness_level': self.consciousness_level
            }

            # Mantener solo conceptos recientes en workspace
            cutoff_time = time.time() - 30  # 30 segundos
            self.global_workspace['active_concepts'] = {
                k: v for k, v in self.global_workspace['active_concepts'].items()
                if k > cutoff_time
            }

    def _consolidate_learning(self, stimulus: Dict[str, Any], cluster_responses: Dict[str, Dict[str, float]]):
        """Consolida el aprendizaje mediante plasticidad sináptica"""

        # Aplicar aprendizaje Hebbiano en sinapsis activas
        for synapse_id, synapse in self.synapses.items():
            pre_neuron_id = synapse.pre_neuron_id
            post_neuron_id = synapse.post_neuron_id

            # Obtener activaciones
            pre_activation = 0.0
            post_activation = 0.0

            for cluster_resp in cluster_responses.values():
                if pre_neuron_id in cluster_resp:
                    pre_activation = cluster_resp[pre_neuron_id]
                if post_neuron_id in cluster_resp:
                    post_activation = cluster_resp[post_neuron_id]

            # Aplicar aprendizaje si ambas neuronas están activas
            if pre_activation > 0.1 or post_activation > 0.1:
                synapse.hebbian_learning(pre_activation, post_activation)

        # Adaptar umbrales neuronales
        for cluster in self.clusters.values():
            for neuron in cluster.neurons.values():
                neuron.adapt_threshold()

    def _generate_conscious_response(self) -> Dict[str, Any]:
        """Genera una respuesta consciente basada en el estado del workspace global"""

        response = {
            'consciousness_level': self.consciousness_level,
            'arousal_level': self.arousal_level,
            'processing_load': self.processing_load,
            'active_clusters': {},
            'insights': [],
            'decisions': {},
            'meta_thoughts': []
        }

        # Analizar estado de cada cluster
        for cluster_id, cluster in self.clusters.items():
            response['active_clusters'][cluster_id] = {
                'activation': cluster.cluster_activation,
                'consensus': cluster.get_cluster_consensus(),
                'specialty': cluster.specialty
            }

        # Generar insights basados en patrones de activación
        if self.consciousness_level > 0.6:
            response['insights'] = self._extract_insights()

        # Tomar decisiones si hay suficiente activación lógica
        logic_activation = self.clusters['logic'].cluster_activation
        if logic_activation > 0.5:
            response['decisions'] = self._make_decisions()

        # Pensamientos metacognitivos
        meta_activation = self.clusters['meta'].cluster_activation
        if meta_activation > 0.4:
            response['meta_thoughts'] = self._generate_meta_thoughts()

        return response

    def _extract_insights(self) -> List[str]:
        """Extrae insights del patrón de activación actual"""
        insights = []

        # Analizar patrones inter-cluster
        if (self.clusters['pattern'].cluster_activation > 0.6 and
            self.clusters['memory'].cluster_activation > 0.5):
            insights.append("Pattern-memory correlation detected - learning opportunity")

        if (self.clusters['emotion'].cluster_activation > 0.7):
            insights.append("High emotional activation - important stimulus detected")

        if (self.clusters['logic'].cluster_activation > 0.8 and
            self.clusters['meta'].cluster_activation > 0.6):
            insights.append("Deep reasoning mode activated - complex problem solving")

        return insights

    def _make_decisions(self) -> Dict[str, Any]:
        """Toma decisiones basadas en la activación de clusters"""
        decisions = {}

        # Decisión de exploración vs explotación
        exploration_score = (self.clusters['pattern'].cluster_activation +
                           self.clusters['emotion'].cluster_activation) / 2

        if exploration_score > 0.6:
            decisions['exploration_strategy'] = 'explore_new_patterns'
        else:
            decisions['exploration_strategy'] = 'exploit_known_patterns'

        # Decisión de profundidad de procesamiento
        processing_depth = (self.clusters['logic'].cluster_activation +
                          self.clusters['meta'].cluster_activation) / 2

        decisions['processing_depth'] = 'deep' if processing_depth > 0.6 else 'shallow'

        return decisions

    def _generate_meta_thoughts(self) -> List[str]:
        """Genera pensamientos metacognitivos sobre el propio proceso mental"""
        meta_thoughts = []

        if self.consciousness_level > 0.8:
            meta_thoughts.append("High consciousness - clear thinking")
        elif self.consciousness_level < 0.3:
            meta_thoughts.append("Low consciousness - unclear or automatic processing")

        if self.processing_load > 0.7:
            meta_thoughts.append("High cognitive load - may need to simplify")

        # Análisis de coherencia entre clusters
        activations = [cluster.cluster_activation for cluster in self.clusters.values()]
        coherence = 1 - np.std(activations) if len(activations) > 1 else 1

        if coherence > 0.8:
            meta_thoughts.append("High neural coherence - integrated thinking")
        elif coherence < 0.5:
            meta_thoughts.append("Low neural coherence - conflicting processes")

        return meta_thoughts

    def get_brain_state(self) -> Dict[str, Any]:
        """Obtiene el estado completo del cerebro neuronal"""
        return {
            'consciousness_level': self.consciousness_level,
            'arousal_level': self.arousal_level,
            'processing_load': self.processing_load,
            'cluster_states': {
                cluster_id: {
                    'activation': cluster.cluster_activation,
                    'consensus': cluster.get_cluster_consensus(),
                    'neuron_count': len(cluster.neurons)
                }
                for cluster_id, cluster in self.clusters.items()
            },
            'synapse_count': len(self.synapses),
            'global_workspace_size': len(self.global_workspace.get('active_concepts', {})),
            'recent_insights': self._extract_insights()
        }

    def save_brain_state(self, filepath: str):
        """Guarda el estado del cerebro neuronal"""
        try:
            brain_data = {
                'consciousness_level': self.consciousness_level,
                'arousal_level': self.arousal_level,
                'processing_load': self.processing_load,
                'timestamp': datetime.now().isoformat(),
                'neuron_count': sum(len(cluster.neurons) for cluster in self.clusters.values()),
                'synapse_count': len(self.synapses),
                'cluster_activations': {
                    cluster_id: cluster.cluster_activation
                    for cluster_id, cluster in self.clusters.items()
                }
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(brain_data, f, indent=2, ensure_ascii=False)

            logger.info(f"🧠 Neural brain state saved to {filepath}")

        except Exception as e:
            logger.error(f"Failed to save neural brain state: {e}")

# Función de fábrica para crear cerebro neuronal
def create_neural_brain() -> NeuralBrain:
    """Crea y configura un nuevo cerebro neuronal"""
    return NeuralBrain()
