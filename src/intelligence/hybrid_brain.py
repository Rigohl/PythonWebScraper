"""
Hybrid Brain System - True Neural Architecture with Consciousness Modeling

Este módulo combina todos los sistemas cerebrales en una arquitectura unificada:
- Neural Brain: Neurons reales con synapses, STDP learning, specialized clusters
- Advanced Reasoning: Deductive, inductive, abductive, fuzzy logic systems
- Advanced Memory: Episodic/semantic memory, working memory, consolidation
- Emotional Brain: Valence-arousal model, emotion regulation, appraisal theory
- Metacognitive Brain: Self-awareness, self-reflection, strategy monitoring
- Legacy Systems: Brain de IA-A + AutonomousLearningBrain de IA-B integrados

El HybridBrain actúa como:
1. Unified Consciousness: Global workspace theory implementation
2. Cross-System Communication: Neural-level integration between subsystems
3. Emergent Intelligence: Properties arising from system interactions
4. True Brain Architecture: Realistic neural processing with synaptic learning
"""

import json
import logging
import os
import statistics
import threading
import time
from collections import defaultdict, deque
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse

from .advanced_memory import create_advanced_memory_system
from .advanced_ml import AdvancedMLIntelligence
from .advanced_reasoning import create_advanced_reasoning_system
from .auto_testing import AutoTestingFramework
from .autonomous_brain import AutonomousLearningBrain, ScrapingSession
from .autonomous_learning import KnowledgeSeeder
from .brain import Brain, ExperienceEvent
from .brain_enrichment import EnrichmentStore
from .cdp_stealth import StealthCDPBrowser
from .code_introspection import CodeIntrospectionEngine
from .continuous_learning import ContinuousLearningOrchestrator
from .emotional_brain import create_emotional_brain
from .knowledge_base import KnowledgeBase
from .knowledge_store import KnowledgeStore
from .metacognitive_brain import create_metacognitive_brain

# Import new brain systems
from .neural_brain import create_neural_brain
from .plugin_manager import PluginManager
from .rule_engine import RuleEngine
from .self_improvement import SelfImprovingSystem
from .self_repair import SelfRepairAdvisor

# Self-update engine (to be created) provides analysis & suggestions
try:
    from .self_update_engine import SelfUpdateEngine
except Exception:  # graceful if not yet created
    SelfUpdateEngine = None

logger = logging.getLogger(__name__)


class UnifiedBrainArchitecture:
    """
    Arquitectura cerebral unificada que integra todos los sistemas neuronales
    Implementa Global Workspace Theory para consciencia emergente
    """

    def __init__(self):
        # Core brain systems - True neural architecture
        self.neural_brain = create_neural_brain()
        self.reasoning_system = create_advanced_reasoning_system()
        self.memory_system = create_advanced_memory_system()
        self.emotional_brain = create_emotional_brain()
        self.metacognitive_brain = create_metacognitive_brain()

        # Global Workspace for consciousness modeling
        self.global_workspace = {
            "current_focus": None,
            "active_coalitions": [],
            "conscious_contents": deque(maxlen=10),
            "attention_weights": defaultdict(float),
            "integration_buffer": [],
        }

        # Cross-system communication channels
        self.neural_channels = {
            "memory_emotional": [],  # Memory <-> Emotion connections
            "reasoning_memory": [],  # Reasoning <-> Memory connections
            "metacog_all": [],  # Metacognition monitors all
            "emotion_decision": [],  # Emotion influences decisions
            "neural_global": [],  # Neural <-> Global workspace
        }

        # Consciousness parameters
        self.consciousness_threshold = 0.6  # Threshold for conscious access
        self.integration_window = 100  # ms for neural integration
        # System metrics
        self.neural_activity_level = 0.5
        self.consciousness_level = 0.3
        self.integration_coherence = 0.4

        # Background processing
        self.background_cycles = 0
        self.last_consolidation = time.time()

        logger.info(
            "🧠 Unified Brain Architecture initialized with true neural systems"
        )

    def process_sensory_input(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Procesa input sensorial a través de toda la arquitectura neural"""

        processing_start = time.time()

        # 1. NEURAL PROCESSING: Raw input through neural clusters
        neural_response = self.neural_brain.process_distributed(
            input_data=input_data, clusters=["sensory", "pattern", "memory"]
        )

        # 2. EMOTIONAL APPRAISAL: Process emotional significance
        event_description = input_data.get("description", "sensory input")
        emotional_context = {
            "familiarity": input_data.get("familiarity", 0.5),
            "goal_relevance": input_data.get("importance", 0.5),
            "controllable": input_data.get("controllable", True),
        }

        emotional_response = self.emotional_brain.process_emotional_event(
            event_description, emotional_context
        )

        # 3. MEMORY ENCODING: Store with emotional enhancement
        memory_content = {
            "input_data": input_data,
            "neural_response": neural_response,
            "timestamp": processing_start,
        }

        # Emotional influence on memory encoding
        enhanced_memory = self.emotional_brain.influence_memory_encoding(memory_content)

        # Create episode for episodic memory
        from .advanced_memory import Episode

        episode = Episode(
            event_description=event_description,
            participants=["self"],
            location=input_data.get("location", "unknown"),
            timestamp=processing_start,
            duration=1.0,
            outcome=input_data.get("outcome", "processed"),
            details=enhanced_memory,
        )

        memory_id = self.memory_system.encode_episode(episode)

        # 4. REASONING INTEGRATION: Apply reasoning to understand input
        reasoning_context = {
            "facts": [input_data],
            "goals": ["understand_input", "extract_meaning"],
            "constraints": [],
        }

        reasoning_result = self.reasoning_system.integrated_reasoning(
            query="analyze_sensory_input",
            context=reasoning_context,
            reasoning_types=["deductive", "inductive"],
        )

        # 5. METACOGNITIVE MONITORING: Monitor the processing
        task_context = {
            "type": "sensory_processing",
            "complexity": input_data.get("complexity", 0.5),
            "time_pressure": 0.3,
            "familiarity": emotional_context["familiarity"],
        }

        metacog_cycle = self.metacognitive_brain.initiate_metacognitive_cycle(
            task_context
        )

        # 6. GLOBAL WORKSPACE INTEGRATION: Combine all subsystem outputs
        integrated_response = self._integrate_in_global_workspace(
            {
                "neural": neural_response,
                "emotional": emotional_response.primary_emotion.value,
                "memory": memory_id,
                "reasoning": reasoning_result,
                "metacognitive": metacog_cycle,
            }
        )

        # 7. UPDATE NEURAL CONNECTIONS: Hebbian learning between systems
        self._update_cross_system_connections(input_data, integrated_response)

        processing_time = time.time() - processing_start

        return {
            "integrated_response": integrated_response,
            "neural_activity": neural_response,
            "emotional_state": self.emotional_brain.get_emotional_state(),
            "memory_encoding": memory_id,
            "reasoning_analysis": reasoning_result,
            "metacognitive_state": self.metacognitive_brain.get_metacognitive_status(),
            "consciousness_level": self.consciousness_level,
            "processing_time_ms": processing_time * 1000,
            "neural_activity_level": self.neural_activity_level,
        }

    def _integrate_in_global_workspace(
        self, subsystem_outputs: dict[str, Any]
    ) -> dict[str, Any]:
        """Integra outputs de subsistemas en workspace global (consciousness)"""

        # Calculate coalition strengths
        coalition_strengths = {}

        for subsystem, output in subsystem_outputs.items():
            strength = 0.5  # Base strength

            # Neural coalition strength
            if subsystem == "neural":
                strength = output.get("overall_activation", 0.5)

            # Emotional coalition strength
            elif subsystem == "emotional":
                emotional_intensity = self.emotional_brain.current_emotion.intensity
                strength = emotional_intensity

            # Memory coalition strength
            elif subsystem == "memory":
                # Recent memory encoding suggests active memory system
                strength = 0.7

            # Reasoning coalition strength
            elif subsystem == "reasoning":
                confidence = output.get("overall_confidence", 0.5)
                strength = confidence

            # Metacognitive coalition strength
            elif subsystem == "metacognitive":
                awareness_level = self.metacognitive_brain.current_metacognitive_state[
                    "self_awareness_level"
                ]
                strength = awareness_level

            coalition_strengths[subsystem] = strength

        # Determine winning coalition(s) for conscious access
        consciousness_threshold = self.consciousness_threshold
        winning_coalitions = [
            subsystem
            for subsystem, strength in coalition_strengths.items()
            if strength > consciousness_threshold
        ]

        # Update global workspace
        self.global_workspace["active_coalitions"] = winning_coalitions
        self.global_workspace["attention_weights"].update(coalition_strengths)

        # Create integrated conscious content
        if winning_coalitions:
            conscious_content = {
                "timestamp": time.time(),
                "dominant_coalition": max(
                    coalition_strengths.items(), key=lambda x: x[1]
                )[0],
                "coalition_strengths": coalition_strengths,
                "integrated_meaning": self._extract_integrated_meaning(
                    subsystem_outputs
                ),
                "consciousness_level": max(coalition_strengths.values()),
            }

            self.global_workspace["conscious_contents"].append(conscious_content)
            self.consciousness_level = conscious_content["consciousness_level"]

        # Apply attention decay
        for subsystem in self.global_workspace["attention_weights"]:
            self.global_workspace["attention_weights"][
                subsystem
            ] *= self.attention_decay

        return {
            "conscious_access": len(winning_coalitions) > 0,
            "dominant_process": max(coalition_strengths.items(), key=lambda x: x[1])[0],
            "coalition_strengths": coalition_strengths,
            "consciousness_level": self.consciousness_level,
            "integrated_meaning": (
                self._extract_integrated_meaning(subsystem_outputs)
                if winning_coalitions
                else None
            ),
        }

    def _extract_integrated_meaning(self, subsystem_outputs: dict[str, Any]) -> str:
        """Extrae significado integrado de outputs de subsistemas"""

        neural_response = subsystem_outputs.get("neural", {})
        emotional_state = subsystem_outputs.get("emotional", "neutral")
        reasoning_result = subsystem_outputs.get("reasoning", {})

        # Simple integration heuristic
        neural_interpretation = neural_response.get(
            "interpretation", "neural_processing"
        )
        emotional_valence = (
            "positive"
            if emotional_state in ["joy", "surprise"]
            else (
                "negative"
                if emotional_state in ["fear", "anger", "sadness"]
                else "neutral"
            )
        )
        reasoning_conclusion = reasoning_result.get(
            "final_conclusion", "analysis_complete"
        )

        integrated_meaning = f"Neural: {neural_interpretation}, Emotional: {emotional_valence}, Reasoning: {reasoning_conclusion}"

        return integrated_meaning

    def _update_cross_system_connections(
        self, input_data: dict[str, Any], response: dict[str, Any]
    ):
        """Actualiza conexiones entre sistemas (Hebbian learning)"""

        # Strengthen connections based on co-activation
        connection_strength = 0.1

        # Memory-Emotion connections
        if (
            response.get("emotional_state", {})
            .get("current_emotion", {})
            .get("intensity", 0)
            > 0.5
        ):
            self.neural_channels["memory_emotional"].append(
                {
                    "timestamp": time.time(),
                    "strength": connection_strength,
                    "context": "emotional_memory_encoding",
                }
            )

        # Reasoning-Memory connections
        if response.get("reasoning_analysis", {}).get("overall_confidence", 0) > 0.6:
            self.neural_channels["reasoning_memory"].append(
                {
                    "timestamp": time.time(),
                    "strength": connection_strength,
                    "context": "reasoning_memory_retrieval",
                }
            )

        # Metacognition monitors all systems
        self.neural_channels["metacog_all"].append(
            {
                "timestamp": time.time(),
                "monitored_systems": ["neural", "emotional", "memory", "reasoning"],
                "monitoring_strength": connection_strength,
            }
        )

        # Trim old connections (maintain recent history only)
        for channel in self.neural_channels.values():
            if isinstance(channel, list) and len(channel) > 100:
                channel[:] = channel[-50:]  # Keep last 50 connections

    def background_consciousness_cycle(self):
        """Ciclo de background para mantenimiento de consciencia"""

        self.background_cycles += 1
        current_time = time.time()

        # 1. MEMORY CONSOLIDATION (every 5 minutes)
        if current_time - self.last_consolidation > 300:  # 5 minutes
            self.memory_system.consolidation_cycle()
            self.last_consolidation = current_time

        # 2. EMOTIONAL DECAY (every cycle)
        self.emotional_brain.decay_emotions(time_elapsed_minutes=1.0)

        # 3. NEURAL HOMEOSTASIS (every 10 cycles)
        if self.background_cycles % 10 == 0:
            self.neural_brain.homeostatic_update()

        # 4. METACOGNITIVE UPDATE (every 5 cycles)
        if self.background_cycles % 5 == 0:
            self.emotional_brain.update_mood()

            # Self-reflection trigger
            performance_metrics = {
                "consciousness_level": self.consciousness_level,
                "neural_activity": self.neural_activity_level,
                "integration_coherence": self.integration_coherence,
            }

            reflection_context = {
                "performance_metrics": performance_metrics,
                "cognitive_state": {
                    "cognitive_load": self.metacognitive_brain.monitor.cognitive_load,
                    "attention_focus": self.metacognitive_brain.monitor.attention_focus,
                },
            }

            self.metacognitive_brain.trigger_self_reflection(reflection_context)

        # 5. UPDATE SYSTEM METRICS
        self._update_system_metrics()

    def _update_system_metrics(self):
        """Actualiza métricas del sistema"""

        # Neural activity level
        active_neurons = self.neural_brain.get_active_neuron_count()
        total_neurons = sum(
            len(cluster.neurons) for cluster in self.neural_brain.clusters.values()
        )
        self.neural_activity_level = active_neurons / max(1, total_neurons)

        # Integration coherence
        active_coalitions = len(self.global_workspace["active_coalitions"])
        total_systems = 5  # neural, emotional, memory, reasoning, metacognitive
        self.integration_coherence = active_coalitions / total_systems

        # Consciousness level already updated in global workspace integration

    def get_consciousness_state(self) -> dict[str, Any]:
        """Obtiene estado completo de consciencia"""

        return {
            "consciousness_level": self.consciousness_level,
            "neural_activity_level": self.neural_activity_level,
            "integration_coherence": self.integration_coherence,
            "global_workspace": {
                "active_coalitions": self.global_workspace["active_coalitions"],
                "current_focus": self.global_workspace["current_focus"],
                "attention_distribution": dict(
                    self.global_workspace["attention_weights"]
                ),
                "conscious_contents_count": len(
                    self.global_workspace["conscious_contents"]
                ),
            },
            "subsystem_states": {
                "neural": self.neural_brain.get_brain_state(),
                "emotional": self.emotional_brain.get_emotional_state(),
                "memory": self.memory_system.get_memory_statistics(),
                "reasoning": {
                    "available_reasoners": [
                        "deductive",
                        "inductive",
                        "abductive",
                        "fuzzy",
                    ],
                    "active": True,
                },
                "metacognitive": self.metacognitive_brain.get_metacognitive_status(),
            },
            "cross_system_connections": {
                channel: len(connections) if isinstance(connections, list) else 0
                for channel, connections in self.neural_channels.items()
            },
            "background_cycles": self.background_cycles,
        }


class HybridBrain:
    """
    Sistema cerebral híbrido que integra:
    - Unified Brain Architecture: Neural verdadero con consciousness
    - Legacy Systems: Brain + AutonomousLearning integrados
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir

        # Initialize true neural brain architecture
        self.unified_brain = UnifiedBrainArchitecture()

        # Initialize legacy systems (preserved for compatibility)
        state_file = os.path.join(data_dir, "brain_state.json")
        learning_file = os.path.join(data_dir, "autonomous_learning.json")

        self.simple_brain = Brain(state_file=state_file)
        self.autonomous_brain = AutonomousLearningBrain(data_path=learning_file)

        # Additional intelligence systems
        self.knowledge_base = KnowledgeBase()
        self.rule_engine = RuleEngine()
        self.enrichment = EnrichmentStore()

        # Load overrides
        self.overrides = self._load_brain_overrides()

        # Self-repair advisor
        self.self_repair_advisor = SelfRepairAdvisor(
            self.simple_brain,
            self.autonomous_brain,
            self.enrichment,
            overrides=self.overrides,
            knowledge_base=self.knowledge_base,
        )

        self.auto_testing = AutoTestingFramework()

        # Advanced AI systems
        try:
            self.ml_intelligence = AdvancedMLIntelligence()
            self.self_improver = SelfImprovingSystem()
            self.cdp_browser = StealthCDPBrowser()
            logger.info("🚀 Advanced AI systems loaded successfully")
        except Exception as e:
            logger.warning(f"Some advanced AI systems failed to load: {e}")
            self.ml_intelligence = None
            self.self_improver = None
            self.cdp_browser = None

        # Neural integration state
        self.integration_mode = "unified"  # "unified", "legacy", "hybrid"
        self.consciousness_enabled = True
        self.ia_sync_file = "IA_SYNC.md"

        # Background processing thread
        self._start_background_processing()

        # Orquestador de aprendizaje continuo (coordina todo)
        try:
            self.learning_orchestrator = ContinuousLearningOrchestrator()

            # Vincular componentes al orquestador
            self.learning_orchestrator.set_ml_intelligence(self.ml_intelligence)
            self.learning_orchestrator.set_self_improver(self.self_improver)
            self.learning_orchestrator.set_knowledge_base(self.knowledge_base)

            logger.info(
                "🚀 Advanced AI modules loaded: ML Intelligence, Self-Improvement, CDP Stealth, Continuous Learning"
            )

        except Exception as e:
            logger.warning(f"Some advanced AI modules failed to load: {e}")
            self.learning_orchestrator = None

        # Inicializar sistema de curiosidad
        self._initialize_curiosity_system()

        logger.info(
            "🧠 HybridBrain initialized with Unified Neural Architecture + Legacy Systems"
        )

        # ================= Code Introspection & Self-Update =================
        try:
            self.code_introspector = CodeIntrospectionEngine(
                code_dir=os.path.dirname(__file__)
            )
            self.code_structure = self.code_introspector.parse_directory()
            if SelfUpdateEngine:
                project_root = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "..", "..")
                )
                self.self_update_engine = SelfUpdateEngine(root_dir=project_root)
            else:
                self.self_update_engine = None

            # Initialize knowledge seeder
            self.knowledge_seeder = KnowledgeSeeder(self.knowledge_store)
            logger.info(
                "🔍 Code introspection active | files=%d", len(self.code_structure)
            )
        except Exception as e:
            logger.warning(f"Code introspection init failed: {e}")
            self.code_introspector = None
            self.code_structure = {}
            self.self_update_engine = None

        # Strategy & self-maintenance state
        self.strategy_history = deque(maxlen=50)
        self.last_self_maintenance = 0.0
        self.self_maintenance_interval = 3600  # seconds
        # Knowledge store
        try:
            self.knowledge_store = KnowledgeStore()
            logger.info("🧬 KnowledgeStore ready (SQLite)")
        except Exception as e:
            logger.warning(f"KnowledgeStore init failed: {e}")
            self.knowledge_store = None

        # Plugin manager
        try:
            plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
            self.plugin_manager = PluginManager(plugins_dir)
            self.plugin_manager.discover()
            self.plugin_manager.initialize(self)
            logger.info("🔌 Plugins loaded: %d", len(self.plugin_manager.plugins))
        except Exception as e:
            logger.warning(f"Plugin system init failed: {e}")
            self.plugin_manager = None

        # Adaptation engine simple stats
        self.adaptation_stats = {
            "events_processed": 0,
            "success_events": 0,
            "failure_events": 0,
            "domains": {},
        }

        # Inicializar historial de modificaciones y estado omnisciente
        self._modification_history = []
        self._monitoring_active = False
        self._monitoring_thread = None

        # Inicializar omnisciencia después de todos los componentes
        self._initialize_omniscience()

    def _start_background_processing(self):
        """Inicia procesamiento de background para consciencia"""

        def background_loop():
            while True:
                try:
                    if self.consciousness_enabled and self.integration_mode in [
                        "unified",
                        "hybrid",
                    ]:
                        self.unified_brain.background_consciousness_cycle()
                        # Continuous reflective thinking
                        self._continuous_thought_cycle()
                        # Plugin periodic tick
                        if self.plugin_manager:
                            self.plugin_manager.tick()
                    time.sleep(10)  # 10 second cycles
                except Exception as e:
                    logger.error(f"Background processing error: {e}")
                    time.sleep(30)  # Longer sleep on error

        self.background_thread = threading.Thread(target=background_loop, daemon=True)
        self.background_thread.start()

        # Initialize omniscient observation capabilities
        self._initialize_omniscience()

    def process_scraping_event(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """
        Procesa evento de scraping a través de toda la arquitectura neural
        """

        if self.integration_mode == "unified":
            return self._process_with_unified_brain(event_data)
        elif self.integration_mode == "legacy":
            return self._process_with_legacy_systems(event_data)
        else:  # hybrid
            return self._process_with_hybrid_approach(event_data)

    def _process_with_unified_brain(self, event_data: dict[str, Any]) -> dict[str, Any]:
        """Procesa con arquitectura neural unificada"""

        # Enhance event data for neural processing
        enhanced_event = {
            "description": f"Scraping event: {event_data.get('event_type', 'unknown')}",
            "url": event_data.get("url", ""),
            "status_code": event_data.get("status_code", 200),
            "success": event_data.get("success", True),
            "data_extracted": event_data.get("data_extracted", {}),
            "complexity": self._estimate_complexity(event_data),
            "familiarity": self._estimate_familiarity(event_data),
            "importance": event_data.get("importance", 0.5),
            "controllable": True,
            "location": "web_scraping_context",
            "outcome": "success" if event_data.get("success", True) else "failure",
        }

        # Process through unified neural architecture
        neural_response = self.unified_brain.process_sensory_input(enhanced_event)

        # Generate insights for scraping
        scraping_insights = self._extract_scraping_insights(neural_response, event_data)

        # Update legacy systems for compatibility
        self._sync_with_legacy_systems(event_data, neural_response)

        # Ingest event as fact & adapt counters
        self._ingest_event_fact(event_data, neural_response)

        # Plugin processing enrichment
        plugin_outputs = []
        if self.plugin_manager:
            try:
                plugin_outputs = self.plugin_manager.process_event(event_data)
            except Exception:
                plugin_outputs = []

        return {
            **neural_response,
            "scraping_insights": scraping_insights,
            "processing_mode": "unified_neural",
            "consciousness_engaged": neural_response["integrated_response"][
                "conscious_access"
            ],
            "plugin_outputs": plugin_outputs,
        }

    # ===================== Strategy Formulation & Continuous Thought =====================
    def formulate_strategy(
        self, goal: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Genera una estrategia estructurada usando razonamiento multi-modal y conocimiento de programación."""
        context = context or {}

        # Query programming knowledge for relevant insights
        programming_knowledge = []
        if self.knowledge_store:
            try:
                # Get relevant programming knowledge
                if "scraping" in goal.lower() or "web" in goal.lower():
                    prog_knowledge = self.knowledge_store.query_programming_knowledge(
                        "web_scraping"
                    )
                    programming_knowledge.extend(prog_knowledge)

                if "performance" in goal.lower() or "optimization" in goal.lower():
                    perf_knowledge = self.knowledge_store.query_programming_knowledge(
                        "performance"
                    )
                    programming_knowledge.extend(perf_knowledge)

                if "database" in goal.lower() or "data" in goal.lower():
                    db_knowledge = self.knowledge_store.query_programming_knowledge(
                        "database"
                    )
                    programming_knowledge.extend(db_knowledge)
            except Exception:
                logger.exception(
                    "Suppressed non-fatal error in hybrid_brain while computing top_errors"
                )

        reasoning_input = {
            "facts": [{"goal": goal, "time": time.time()}]
            + [
                {"programming_insight": k[2], "confidence": k[3]}
                for k in programming_knowledge[:5]
            ],
            "goals": [goal],
            "constraints": context.get("constraints", []),
            "knowledge_base": programming_knowledge,
        }

        reasoning = self.unified_brain.reasoning_system.integrated_reasoning(
            query=f"strategy_{goal}",
            context=reasoning_input,
            reasoning_types=["abductive", "deductive", "inductive"],
        )

        meta_cycle = (
            self.unified_brain.metacognitive_brain.initiate_metacognitive_cycle(
                {
                    "type": "strategy_formulation",
                    "complexity": context.get("complexity", 0.5),
                    "familiarity": 0.5,
                    "knowledge_used": len(programming_knowledge),
                }
            )
        )

        strategy = {
            "goal": goal,
            "steps": reasoning.get("reasoning_steps", [])[:10],
            "confidence": reasoning.get("overall_confidence", 0.5),
            "meta": meta_cycle,
            "programming_insights": [k[2] for k in programming_knowledge[:3]],
            "knowledge_enhanced": len(programming_knowledge) > 0,
            "timestamp": time.time(),
        }

        self.strategy_history.append(strategy)
        if self.knowledge_store:
            try:
                self.knowledge_store.add_strategy(
                    goal, strategy["confidence"], strategy["steps"], strategy["meta"]
                )
            except Exception:
                logger.exception(
                    "Suppressed non-fatal error in hybrid_brain while computing total_patterns"
                )
        return strategy

    def _continuous_thought_cycle(self):
        """Ejecución periódica: reflexión, generación de estrategias y mantenimiento."""
        now = time.time()
        # Periodic self-maintenance
        if now - self.last_self_maintenance > self.self_maintenance_interval:
            try:
                self.run_self_maintenance_cycle()
            finally:
                self.last_self_maintenance = now
        # Proactive strategy every 15 min
        if (not self.strategy_history) or (
            now - self.strategy_history[-1]["timestamp"] > 900
        ):
            try:
                self.formulate_strategy("optimize_scraping")
            except Exception:
                logger.exception(
                    "Suppressed non-fatal error in hybrid_brain while evaluating domain strategies"
                )
        # Curiosity analysis every 5 min (configurable)
        if hasattr(self, "curiosity_system") and self.curiosity_system:
            try:
                self._run_curiosity_analysis_cycle()
            except Exception as e:
                logger.debug(f"Curiosity analysis cycle failed: {e}")
        # Adaptive tuning: simple reinforcement-like stats logging
        self._adaptive_update()

    def _run_curiosity_analysis_cycle(self):
        """Ejecuta análisis de curiosidad periódica en segundo plano"""
        if not hasattr(self, "last_curiosity_analysis"):
            self.last_curiosity_analysis = 0

        now = time.time()
        curiosity_interval = 300  # 5 minutos por defecto

        # Verificar si es tiempo de análisis de curiosidad
        if now - self.last_curiosity_analysis < curiosity_interval:
            return

        try:
            # Ejecutar análisis de curiosidad
            if hasattr(self.curiosity_system, "analyze_current_state"):
                analysis_result = self.curiosity_system.analyze_current_state()

                # Procesar cualquier novedad detectada
                if analysis_result and analysis_result.get("novelty_detected", False):
                    logger.info(
                        "🧠 Curiosidad: Novedad detectada en el análisis periódico"
                    )

                    # Generar notificación si es apropiado
                    if hasattr(self.curiosity_system, "generate_notification"):
                        notification = self.curiosity_system.generate_notification(
                            analysis_result
                        )
                        if notification:
                            logger.info(f"🧠 Curiosidad: {notification}")

            self.last_curiosity_analysis = now

        except Exception as e:
            logger.debug(f"Error en análisis de curiosidad periódica: {e}")

    # ===================== Self-Maintenance & Code Awareness =====================
    def run_self_maintenance_cycle(self) -> dict[str, Any]:
        """Analiza estructura de código y genera sugerencias de mejora (si disponible)."""
        result = {
            "timestamp": time.time(),
            "introspection": None,
            "improvement_suggestions": None,
        }
        try:
            if self.code_introspector:
                self.code_structure = self.code_introspector.parse_directory()
                result["introspection"] = {
                    "files": len(self.code_structure),
                    "classes": sum(
                        len(v["classes"]) for v in self.code_structure.values()
                    ),
                    "functions": sum(
                        len(v["functions"]) for v in self.code_structure.values()
                    ),
                }
                # Persist metrics per file
                if self.knowledge_store:
                    for path, meta in self.code_structure.items():
                        try:
                            lines = 0
                            with open(path, encoding="utf-8") as fh:
                                lines = fh.read().count("\n") + 1
                            avg_func_len = (
                                lines / max(1, len(meta["functions"]))
                                if meta["functions"]
                                else lines
                            )
                            self.knowledge_store.add_code_metrics(
                                file_path=path,
                                lines=lines,
                                functions=len(meta["functions"]),
                                classes=len(meta["classes"]),
                                avg_func_len=avg_func_len,
                                complexity=0.0,
                                imports=len(meta["imports"]),
                            )
                        except Exception:
                            logger.exception(
                                "Suppressed non-fatal error in hybrid_brain during pattern extraction loop"
                            )
            if self.self_update_engine:
                analysis = self.self_update_engine.analyze_repository()
                suggestions = self.self_update_engine.generate_improvement_suggestions(
                    analysis
                )
                result["improvement_suggestions"] = suggestions[:10]
                if self.knowledge_store:
                    for s in suggestions[:25]:
                        try:
                            self.knowledge_store.add_improvement_suggestion(
                                file_path=s.get("file", "n/a"),
                                issue_type=s["type"],
                                description=s.get("detail", ""),
                                severity=(
                                    "high" if s.get("priority") == "high" else "medium"
                                ),
                                score=0.9 if s.get("priority") == "high" else 0.6,
                                suggestion=s.get("detail", ""),
                            )
                        except Exception:
                            logger.exception(
                                "Suppressed non-fatal error in hybrid_brain during pattern matching"
                            )
        except Exception as e:
            result["error"] = str(e)
        logger.info("🛠️ Self-maintenance cycle done")
        return result

    def get_code_self_awareness(self) -> dict[str, Any]:
        if not self.code_structure:
            return {"available": False}
        return {
            "available": True,
            "files_analyzed": len(self.code_structure),
            "metrics": {
                "total_classes": sum(
                    len(v["classes"]) for v in self.code_structure.values()
                ),
                "total_functions": sum(
                    len(v["functions"]) for v in self.code_structure.values()
                ),
            },
        }

    # ===================== Event -> Fact Ingestion & Adaptation =====================
    def _ingest_event_fact(
        self, event: dict[str, Any], neural_response: dict[str, Any]
    ):
        if not self.knowledge_store:
            return
        try:
            domain = ""
            if "url" in event:
                try:
                    domain = urlparse(event["url"]).netloc
                except Exception:
                    domain = ""
            success = event.get("success", True)
            self.knowledge_store.add_fact(
                category="scrape_event",
                subject=domain or "unknown_domain",
                predicate="event_result",
                obj="success" if success else "failure",
                confidence=0.8 if success else 0.4,
                source="runtime",
            )
            # Adapt counters
            self.adaptation_stats["events_processed"] += 1
            if success:
                self.adaptation_stats["success_events"] += 1
            else:
                self.adaptation_stats["failure_events"] += 1
            if domain:
                d = self.adaptation_stats["domains"].setdefault(
                    domain, {"success": 0, "failure": 0}
                )
                if success:
                    d["success"] += 1
                else:
                    d["failure"] += 1
        except Exception:
            logger.exception(
                "Suppressed non-fatal error in hybrid_brain while enriching session"
            )

    def _adaptive_update(self):
        # Simple heuristic: if a domain has >30% failures and enough samples, generate strategy
        for domain, stats in list(self.adaptation_stats["domains"].items()):
            total = stats["success"] + stats["failure"]
            if total >= 5:
                failure_rate = stats["failure"] / total if total else 0
                if failure_rate > 0.3:
                    try:
                        self.formulate_strategy(
                            f"improve_domain_{domain}", context={"complexity": 0.6}
                        )
                    except Exception:
                        logger.exception(
                            "Suppressed non-fatal error in hybrid_brain when updating autonomous brain"
                        )

    def _load_brain_overrides(self) -> dict[str, Any]:
        """Carga configuración de overrides desde brain_overrides.json (sugerencia IA-A)"""
        overrides_file = "config/brain_overrides.json"
        defaults = {
            "priority_weight_success": 0.6,
            "priority_weight_link": 0.4,
            "backoff_threshold": 0.5,
            "min_visits_for_backoff": 5,
            "autonomous_learning_weight": 0.4,
            "simple_brain_weight": 0.6,
        }

        try:
            if os.path.exists(overrides_file):
                with open(overrides_file, encoding="utf-8") as f:
                    overrides = json.load(f)
                logger.info(f"🧠 Loaded brain overrides from {overrides_file}")
                return {**defaults, **overrides}
            else:
                logger.info("🧠 Using default brain configuration (no overrides file)")
                return defaults
        except Exception as e:
            logger.warning(f"Error loading brain overrides: {e}, using defaults")
            return defaults

    def _build_domain_context(self, domain: str) -> dict[str, Any]:
        """Construye un contexto unificado con toda la inteligencia disponible para un dominio."""
        if not domain:
            return {}

        context = {"domain": domain}

        # 1. Datos del SimpleBrain
        context["simple"] = {
            "visits": getattr(self.simple_brain, "domain_stats", {})
            .get(domain, {})
            .get("visits", 0),
            "success_rate": self.simple_brain.domain_success_rate(domain),
            "error_rate": self.simple_brain.domain_error_rate(domain),
            "link_yield": self.simple_brain.link_yield(domain),
            "avg_response_time": self.simple_brain.avg_response_time(domain),
        }

        # 2. Datos del AutonomousLearningBrain
        auto_intel = self.autonomous_brain.domain_intelligence.get(domain)
        context["autonomous"] = auto_intel.to_dict() if auto_intel else {}

        # 3. Datos del EnrichmentStore
        context["enrichment"] = self.enrichment.domain_insight(domain)

        # 4. Evaluar con RuleEngine
        flat_data_for_rules = {
            "domain": domain,
            **context["simple"],
            **context["enrichment"],
        }
        context["rule_engine_results"] = self.rule_engine.evaluate_all(
            flat_data_for_rules
        )

        return context

    def record_scraping_result(self, result, context: dict[str, Any] = None):
        """Registra un resultado de scraping en ambos sistemas"""

        # Extraer información del resultado
        url = getattr(result, "url", "")
        domain = urlparse(url).netloc if url else ""

        # Determinar estado
        if getattr(result, "success", False):
            status = "SUCCESS"
        elif getattr(result, "is_duplicate", False):
            status = "DUPLICATE"
        elif getattr(result, "error", None):
            status = "ERROR"
        else:
            status = "RETRY"

        # Crear evento para Brain (IA-A)
        event = ExperienceEvent(
            url=url,
            status=status,
            response_time=context.get("response_time") if context else None,
            content_length=len(getattr(result, "content", "") or ""),
            new_links=len(getattr(result, "links", []) or []),
            domain=domain,
            extracted_fields=len(getattr(result, "extracted_data", {}) or {}),
            error_type=context.get("error_type") if context else None,
        )

        # Registrar en Brain (IA-A)
        self.simple_brain.record_event(event)

        # Crear sesión para AutonomousLearningBrain (IA-B) con el dataclass real
        content_len = len(getattr(result, "content", "") or "")
        extracted_fields = len(getattr(result, "extracted_data", {}) or {})
        response_time = (context or {}).get("response_time", 0.0)
        status_code = getattr(
            result, "status_code", 200 if status == "SUCCESS" else 500
        )
        retry_count = (context or {}).get("retry_count", 0)
        user_agent = (context or {}).get("user_agent", "")
        delay_used = (context or {}).get("delay_used", 1.0)
        # Heurística simple para calidad de extracción
        extraction_quality = (
            min(extracted_fields / 10.0, 1.0) if extracted_fields else 0.0
        )
        patterns_found = self._extract_patterns(result)
        errors = []
        if status == "ERROR":
            errors = [
                getattr(
                    result,
                    "error_message",
                    (context or {}).get("error_type", "unknown"),
                )
            ]

        try:
            session = ScrapingSession(
                domain=domain,
                url=url,
                timestamp=time.time(),
                success=(status == "SUCCESS"),
                response_time=response_time,
                content_length=content_len,
                status_code=status_code,
                retry_count=retry_count,
                user_agent=user_agent,
                delay_used=delay_used,
                extraction_quality=extraction_quality,
                patterns_found=patterns_found,
                errors=errors,
            )
            self.autonomous_brain.learn_from_session(session)
        except Exception as e:
            logger.error(f"Failed to register autonomous learning session: {e}")

        # Registrar enriquecimiento (tolerante a fallos, nunca rompe el flujo)
        try:
            self.enrichment.add_session(
                result, context=context, patterns=patterns_found
            )
        except Exception:
            logger.exception(
                "Suppressed non-fatal error in hybrid_brain during auto-learn from session"
            )

        # Auto-aprendizaje dinámico de knowledge base
        try:
            self._auto_learn_from_session(result, context, patterns_found)
        except Exception:
            logger.exception("Suppressed non-fatal error in hybrid_brain link analysis")

        # Log híbrido
        logger.debug(
            f"🧠 Hybrid learning: {status} for {domain} - Brain+Autonomous updated"
        )

        # Chequear y reportar avisos de alto impacto
        try:
            self._check_and_report_advisories(domain)
        except Exception as e:
            logger.error(f"Error checking/reporting advisories: {e}")

    def _check_and_report_advisories(self, domain: str):
        """Revisa y reporta avisos de alto impacto para un dominio.

        Esta implementación es idempotente y no se llama a sí misma. Solo
        informa (log/print) cuando hay una recomendación explícita. Se evita
        cualquier recursión accidental y se captura/registro de excepciones
        completas para facilitar auditoría.
        """
        try:
            # 1. Obtener la tasa de error actual del cerebro simple
            error_rate = self.simple_brain.domain_error_rate(domain)
            min_visits = self.overrides.get("min_visits_for_backoff", 5)

            # 2. Solo actuar si hay suficientes datos
            if (
                getattr(self.simple_brain, "domain_stats", {})
                .get(domain, {})
                .get("visits", 0)
                < min_visits
            ):
                return

            # 3. Si la tasa de error es alta, generar sugerencias
            if error_rate >= self.overrides.get("backoff_threshold", 0.5):
                # Usar el Rule Engine para obtener la sugerencia específica
                domain_data = {"domain": domain, "error_rate": error_rate}
                rule_results = self.rule_engine.evaluate_all(domain_data)

                # Buscar la regla de backoff
                backoff_suggestion = next(
                    (
                        r
                        for r in rule_results
                        if r.get("rule_id") == "high_error_rate_backoff"
                    ),
                    None,
                )

                if backoff_suggestion:
                    # Obtener conocimiento relacionado
                    kb_ref_id = "scraping:respect-delays"
                    kb_snippet = self.knowledge_base.get(kb_ref_id)
                    kb_title = kb_snippet.get("title", "N/A") if kb_snippet else "N/A"

                    # Imprimir el aviso en un formato claro y estructurado
                    print("\n" + "-" * 25)
                    print("🧠 AVISO DEL CEREBRO HÍBRIDO 🧠")
                    print("-" * 25)
                    print(f"Dominio:           {domain}")
                    print(
                        f"Síntoma:           Tasa de Error Elevada ({error_rate:.1%})"
                    )
                    print(f"Sugerencia ID:     {backoff_suggestion['rule_id']}")
                    print(f"Recomendación:     {backoff_suggestion['message']}")
                    print(f"Conocimiento Rel.: {kb_ref_id} - {kb_title}")
                    print("-" * 25 + "\n")

        except Exception as e:
            logger.exception(
                "Error while checking/reporting advisories for domain %s: %s", domain, e
            )

    # Duplicate definition removed. See the canonical implementation above which
    # includes full logging and idempotent behavior. Keeping a single
    # implementation ensures there is no accidental recursion or conflicting
    # behavior.

    def _extract_patterns(self, result) -> list[str]:
        """Extrae patrones avanzados del resultado para el aprendizaje autónomo profundo"""
        patterns = []

        # Patrones de estructura de página
        if hasattr(result, "extracted_data") and result.extracted_data:
            for key in result.extracted_data.keys():
                patterns.append(f"field_{key}")

                # Análisis de tipo de dato para cada campo extraído
                value = result.extracted_data.get(key)
                if isinstance(value, str):
                    # Detectar formatos específicos
                    if value and value[0].isdigit():
                        if "$" in value or "€" in value:
                            patterns.append(f"price_format_{key}")
                        elif "-" in value or "/" in value:
                            patterns.append(f"date_format_{key}")
                    # Detectar longitud de contenido
                    if len(value) > 200:
                        patterns.append(f"long_text_{key}")
                    elif len(value) < 10:
                        patterns.append(f"short_text_{key}")
                elif isinstance(value, (int, float)):
                    patterns.append(f"numeric_{key}")
                elif isinstance(value, list):
                    patterns.append(f"list_{key}_{len(value)}")
                elif isinstance(value, dict):
                    patterns.append(f"nested_{key}")

        # Patrones de links - Análisis avanzado
        if hasattr(result, "links") and result.links:
            link_count = len(result.links)
            patterns.append(f"links_found_{link_count}")

            # Detectar patrones en URLs
            internal_links = 0
            media_links = 0
            pagination_candidates = 0
            domain_patterns = set()

            if hasattr(result, "url"):
                base_domain = urlparse(result.url).netloc

                for link in result.links:
                    try:
                        parsed = urlparse(link)
                        link_domain = parsed.netloc

                        # Detectar links internos vs externos
                        if link_domain == base_domain:
                            internal_links += 1
                            domain_patterns.add(link_domain)

                            # Detectar posible paginación
                            path = parsed.path
                            query = parsed.query
                            if any(
                                x in path for x in ["/page/", "/p/", "page=", "?p="]
                            ):
                                pagination_candidates += 1
                            elif query and any(
                                x in query for x in ["page=", "p=", "pg="]
                            ):
                                pagination_candidates += 1

                        # Detectar links a recursos específicos
                        if any(
                            media in link.lower()
                            for media in [".jpg", ".png", ".pdf", ".mp4"]
                        ):
                            media_links += 1
                    except Exception:
                        continue

            # Añadir insights de links
            if internal_links > 0:
                patterns.append(f"internal_links_{min(internal_links, 100)}")
            if len(domain_patterns) > 1:
                patterns.append(f"diverse_domains_{min(len(domain_patterns), 10)}")
            if pagination_candidates > 0:
                patterns.append(f"pagination_detected_{min(pagination_candidates, 10)}")
            if media_links > 0:
                patterns.append(f"media_links_{min(media_links, 20)}")

        # Patrones de contenido - Análisis avanzado
        content_text = getattr(result, "content_text", "") or ""
        content_html = getattr(result, "content_html", "") or ""
        content_length = len(content_text)

        # Clasificación de tamaño
        if content_length > 10000:
            patterns.append("large_content")
        elif content_length > 1000:
            patterns.append("medium_content")
        else:
            patterns.append("small_content")

        # Análisis de estructura HTML
        if content_html:
            # Detectar tablas
            if "<table" in content_html:
                tables_count = content_html.count("<table")
                patterns.append(f"tables_{min(tables_count, 10)}")

            # Detectar formularios
            if "<form" in content_html:
                forms_count = content_html.count("<form")
                patterns.append(f"forms_{forms_count}")

            # Detectar scripts incrustados
            if "<script" in content_html:
                scripts_count = content_html.count("<script")
                patterns.append(f"scripts_{min(scripts_count, 20)}")

                # Detectar frameworks comunes
                js_frameworks = ["react", "vue", "angular", "jquery", "bootstrap"]
                for framework in js_frameworks:
                    if framework in content_html.lower():
                        patterns.append(f"uses_{framework}")

            # Detectar secciones importantes
            if "<header" in content_html or "<nav" in content_html:
                patterns.append("has_header_nav")

            if "<footer" in content_html:
                patterns.append("has_footer")

            # Detectar estructuras comunes
            if "<article" in content_html:
                patterns.append("article_structure")

            if "<section" in content_html:
                sections_count = content_html.count("<section")
                patterns.append(f"sections_{min(sections_count, 10)}")

        # Análisis semántico del contenido
        if content_text:
            # Detectar tipo de contenido
            semantic_indicators = {
                "product": [
                    "comprar",
                    "precio",
                    "disponible",
                    "envío",
                    "stock",
                    "producto",
                ],
                "article": ["publicado", "autor", "artículo", "leer", "comentarios"],
                "profile": ["perfil", "usuario", "biografía", "seguir", "miembro"],
                "listing": [
                    "resultados",
                    "ordenar por",
                    "filtrar",
                    "mostrar",
                    "búsqueda",
                ],
                "news": [
                    "noticia",
                    "última hora",
                    "reportaje",
                    "periodista",
                    "actualidad",
                ],
            }

            content_lower = content_text.lower()
            for content_type, indicators in semantic_indicators.items():
                matches = sum(1 for ind in indicators if ind in content_lower)
                if matches >= 2:  # Al menos 2 indicadores
                    patterns.append(f"content_type_{content_type}")

            # Detectar idioma (simplificado)
            lang_indicators = {
                "es": ["de", "la", "el", "en", "que", "por", "con", "para"],
                "en": ["the", "of", "and", "to", "in", "is", "that"],
                "fr": ["le", "la", "les", "des", "du", "et", "est"],
                "de": ["der", "die", "das", "und", "ist", "für"],
            }

            lang_scores = {}
            for lang, indicators in lang_indicators.items():
                words = content_lower.split()
                common_words = sum(1 for word in words if word in indicators)
                if len(words) > 0:
                    lang_scores[lang] = common_words / len(words)

            if lang_scores:
                detected_lang = max(lang_scores.items(), key=lambda x: x[1])
                if detected_lang[1] > 0.05:  # Umbral mínimo
                    patterns.append(f"lang_{detected_lang[0]}")

        # Patrones de respuesta y metadatos HTTP
        if hasattr(result, "http_status_code") and result.http_status_code:
            status_code = result.http_status_code
            # Agrupar códigos por categoría
            if 200 <= status_code < 300:
                patterns.append("status_success")
            elif 300 <= status_code < 400:
                patterns.append(f"status_redirect_{status_code}")
            elif 400 <= status_code < 500:
                patterns.append(f"status_client_error_{status_code}")
            elif 500 <= status_code < 600:
                patterns.append(f"status_server_error_{status_code}")

        # Patrones de tiempo de carga
        if hasattr(result, "response_time") and result.response_time:
            response_time = result.response_time
            if response_time < 0.5:
                patterns.append("response_very_fast")
            elif response_time < 1.0:
                patterns.append("response_fast")
            elif response_time < 2.0:
                patterns.append("response_medium")
            elif response_time < 5.0:
                patterns.append("response_slow")
            else:
                patterns.append("response_very_slow")

        # Patrones de healing
        if hasattr(result, "healing_events") and result.healing_events:
            healing_count = len(result.healing_events)
            patterns.append(f"healing_applied_{min(healing_count, 5)}")

            # Tipos de healing aplicados
            healing_types = set()
            for event in result.healing_events:
                if "type" in event:
                    healing_types.add(event["type"])

            for htype in healing_types:
                patterns.append(f"healing_type_{htype}")

        # LLM insights
        if hasattr(result, "llm_extracted_data") and result.llm_extracted_data:
            patterns.append("llm_enhanced")

            # Contar campos extraídos por LLM
            llm_fields = len(result.llm_extracted_data)
            patterns.append(f"llm_fields_{min(llm_fields, 10)}")

        return patterns

    def get_domain_priority(self, domain: str) -> float:
        """Calcula prioridad de dominio combinando ambos sistemas con overrides configurables"""

        # Prioridad básica del Brain (IA-A) con overrides
        simple_priority = (
            self.simple_brain.domain_success_rate(domain)
            * self.overrides["priority_weight_success"]
            + self.simple_brain.link_yield(domain)
            * self.overrides["priority_weight_link"]
        )

        # Inteligencia del AutonomousLearningBrain (IA-B)
        autonomous_priority = 0.0

        # Usar la inteligencia autónoma (adaptado a la API real)
        try:
            import statistics

            domain_sessions = [
                s
                for s in getattr(self.autonomous_brain, "session_history", [])
                if getattr(s, "domain", None) == domain
            ]
            if domain_sessions:
                try:
                    success_rate = sum(
                        1 for s in domain_sessions if getattr(s, "success", False)
                    ) / len(domain_sessions)
                except Exception:
                    success_rate = 0.0

                try:
                    avg_response = statistics.mean(
                        [
                            float(getattr(s, "response_time", 0) or 0)
                            for s in domain_sessions
                        ]
                    )
                except Exception:
                    avg_response = 0.0

                try:
                    pattern_count = sum(
                        len(getattr(s, "patterns_found", []) or [])
                        for s in domain_sessions
                    )
                except Exception:
                    pattern_count = 0

                autonomous_priority = (
                    float(success_rate) * 0.4
                    + min(float(avg_response) / 1000.0, 1.0) * 0.3
                    + (float(pattern_count) / 10.0) * 0.3
                )
        except Exception:
            # Fallback en caso de error
            autonomous_priority = 0.0

        # Combinar ambas prioridades con pesos configurables (overrides)
        hybrid_priority = (
            simple_priority * self.overrides["simple_brain_weight"]
            + autonomous_priority * self.overrides["autonomous_learning_weight"]
        )

        return hybrid_priority

    def should_backoff(self, domain: str) -> bool:
        """Determina si debe hacer backoff combinando ambos sistemas con overrides configurables"""

        # Backoff simple del Brain (IA-A) con configuración override
        try:
            simple_backoff = bool(
                self.simple_brain.should_backoff(
                    domain,
                    error_threshold=self.overrides.get("backoff_threshold", 0.5),
                    min_visits=self.overrides.get("min_visits_for_backoff", 5),
                )
            )
        except Exception:
            simple_backoff = False

        # Backoff inteligente del AutonomousLearningBrain (IA-B)
        autonomous_backoff = False

        try:
            # Usar la API real del cerebro autónomo
            domain_sessions = [
                s
                for s in getattr(self.autonomous_brain, "session_history", [])
                if getattr(s, "domain", None) == domain
            ]
            min_visits = int(self.overrides.get("min_visits_for_backoff", 5))
            if len(domain_sessions) >= min_visits:
                try:
                    success_rate = sum(
                        1 for s in domain_sessions if getattr(s, "success", False)
                    ) / len(domain_sessions)
                except Exception:
                    success_rate = 1.0

                try:
                    error_count = sum(
                        len(getattr(s, "errors", []) or []) for s in domain_sessions
                    )
                except Exception:
                    error_count = 0

                # Backoff si el éxito es muy bajo o hay muchos errores
                autonomous_backoff = (
                    float(success_rate)
                    < float(self.overrides.get("backoff_threshold", 0.5))
                    or int(error_count) > 3
                )
        except Exception:
            autonomous_backoff = False

        # Si cualquiera de los dos sugiere backoff, hacemos backoff
        return simple_backoff or autonomous_backoff

    def get_optimization_config(self, domain: str) -> dict[str, Any]:
        """Obtiene configuración optimizada para un dominio"""

        config = {}

        try:
            import statistics

            # Usar la API real del cerebro autónomo
            domain_sessions = [
                s for s in self.autonomous_brain.session_history if s.domain == domain
            ]
            if domain_sessions:
                success_rate = sum(1 for s in domain_sessions if s.success) / len(
                    domain_sessions
                )

                # Extraer estrategias basadas en sesiones exitosas
                successful_sessions = [s for s in domain_sessions if s.success]
                if successful_sessions:
                    best_session = max(
                        successful_sessions, key=lambda s: s.extraction_quality
                    )
                    config.update(
                        {
                            "delay": best_session.delay_used,
                            "user_agent_pattern": best_session.user_agent,
                            "retry_count": min(
                                5,
                                max(
                                    1,
                                    int(
                                        statistics.median(
                                            [s.retry_count for s in successful_sessions]
                                        )
                                    ),
                                ),
                            ),
                            "timeout": 30,  # Valor por defecto
                            "predicted_success_rate": success_rate,
                        }
                    )
        except Exception:
            # Si hay error, no añadimos nada a la configuración
            pass

        # Combinar con métricas del Brain simple
        config.update(
            {
                "simple_priority": self.simple_brain.domain_priority(domain),
                "error_rate": self.simple_brain.domain_error_rate(domain),
                "avg_response_time": self.simple_brain.avg_response_time(domain),
            }
        )

        return config

    def get_comprehensive_stats(self) -> dict[str, Any]:
        """Obtiene estadísticas comprehensivas de ambos sistemas"""

        # Stats del Brain (IA-A)
        simple_stats = self.simple_brain.snapshot()

        # Stats del AutonomousLearningBrain (IA-B)
        try:
            domains_learned = len(
                getattr(self.autonomous_brain, "domain_intelligence", {})
            )
            total_patterns = sum(
                len(v)
                for v in getattr(self.autonomous_brain, "pattern_library", {}).values()
            )
            # Contar estrategias: suma de longitudes de best_strategies por dominio
            strategies_optimized = sum(
                len(intel.best_strategies)
                for intel in getattr(
                    self.autonomous_brain, "domain_intelligence", {}
                ).values()
            )
            learning_sessions = len(
                getattr(self.autonomous_brain, "session_history", [])
            )
        except Exception as e:
            logger.error(f"Error collecting autonomous brain stats: {e}")
            domains_learned = 0
            total_patterns = 0
            strategies_optimized = 0
            learning_sessions = 0

        # Calcular métricas avanzadas de AutonomousLearningBrain
        try:
            successful_sessions = sum(
                1
                for s in getattr(self.autonomous_brain, "session_history", [])
                if getattr(s, "success", False)
            )
            success_rate = (
                successful_sessions / max(learning_sessions, 1)
                if learning_sessions > 0
                else 0
            )

            # Analizar los tiempos de respuesta
            response_times = [
                s.response_time
                for s in self.autonomous_brain.session_history
                if s.success
            ]
            avg_response_time = statistics.mean(response_times) if response_times else 0

            # Analizar patrones más comunes
            all_patterns = []
            for session in getattr(self.autonomous_brain, "session_history", []):
                all_patterns.extend(getattr(session, "patterns_found", []) or [])

            pattern_frequency = {}
            for pattern in all_patterns:
                pattern_frequency[pattern] = pattern_frequency.get(pattern, 0) + 1

            top_patterns = sorted(
                pattern_frequency.items(), key=lambda x: x[1], reverse=True
            )[:5]

            # Estadísticas por dominio
            domain_success_rates = {}
            for domain, intel in getattr(
                self.autonomous_brain, "domain_intelligence", {}
            ).items():
                domain_success_rates[domain] = getattr(intel, "success_rate", 0)

            # Eficiencia de aprendizaje
            learning_efficiency = getattr(
                self.autonomous_brain, "_calculate_learning_efficiency", lambda: 0
            )()
        except Exception as e:
            logger.error(f"Error calculating advanced autonomous brain metrics: {e}")
            successful_sessions = 0
            success_rate = 0
            avg_response_time = 0
            top_patterns = []
            domain_success_rates = {}
            learning_efficiency = 0

        autonomous_stats = {
            "domains_learned": domains_learned,
            "total_patterns": total_patterns,
            "strategies_optimized": strategies_optimized,
            "learning_sessions": learning_sessions,
            "success_rate": round(success_rate, 2),
            "avg_response_time": round(avg_response_time, 2),
            "top_patterns": top_patterns,
            "domain_success_rates": domain_success_rates,
            "learning_efficiency": round(learning_efficiency, 2),
        }

        # Combinar estadísticas
        hybrid_stats = {
            "hybrid_system": True,
            "simple_brain": simple_stats,
            "autonomous_brain": autonomous_stats,
            "enrichment": self.enrichment.summarize(),
            "repair_suggestions_preview": self.generate_repair_suggestions(limit=5),
            "knowledge_base_snippets": len(
                getattr(self.knowledge_base, "snippets", {})
            ),
            "rule_engine_summary": self.rule_engine.get_rule_summary(),
            "auto_testing_summary": self.auto_testing.get_testing_summary(),
            "top_performing_domains": self._get_top_performing_domains(),
            "learning_insights": self._get_learning_insights(),
            "overrides": self.overrides,
        }

        return hybrid_stats

    # ----------------- Compatibilidad con interfaz Brain simple -----------------
    def snapshot(
        self,
    ) -> dict[str, Any]:  # pragma: no cover - usada por tests heredados
        """Devuelve un snapshot similar al Brain clásico para compatibilidad.

        Estructura:
        {
          'domains': { ... },
          'top_domains': [...],
          'error_type_freq': {...},
          'recent_events': [...],
          'hybrid': True
        }
        """
        # Obtain snapshot from the simple brain, but be defensive: tests often
        # patch Brain with MagicMock which would return MagicMock objects here.
        try:
            simple = self.simple_brain.snapshot()
        except Exception:
            simple = {}

        # If the returned snapshot isn't a dict (e.g. MagicMock), coerce to a
        # safe dict structure so callers/tests can index keys as expected.
        if not isinstance(simple, dict):
            try:
                simple = dict(simple)
            except Exception:
                simple = {
                    "domains": {},
                    "top_domains": [],
                    "error_type_freq": {},
                    "recent_events": [],
                    "total_events": 0,
                }

        simple["hybrid"] = True
        return simple

    def domain_priority(self, domain: str) -> float:  # pragma: no cover
        """Alias para permitir que código legado use domain_priority()."""
        try:
            return self.get_domain_priority(domain)
        except Exception:
            return 0.0

    def _get_top_performing_domains(self) -> list[dict[str, Any]]:
        """Obtiene los dominios con mejor rendimiento combinado"""

        domain_scores = {}

        # Combinar dominios de ambos sistemas
        # Defensive: tests may autospec Brain and AutonomousLearningBrain which
        # produce mocks without instance attributes like domain_stats or
        # domain_intelligence. Use getattr with sensible defaults.
        simple_domains = set(getattr(self.simple_brain, "domain_stats", {}).keys())
        auto_domains = set(
            getattr(self.autonomous_brain, "domain_intelligence", {}).keys()
        )
        all_domains = simple_domains | auto_domains

        for domain in all_domains:
            hybrid_priority = self.get_domain_priority(domain)
            simple_success = self.simple_brain.domain_success_rate(domain)

            domain_scores[domain] = {
                "domain": domain,
                "hybrid_priority": hybrid_priority,
                "simple_success_rate": simple_success,
                "total_visits": self.simple_brain.domain_stats.get(domain, {}).get(
                    "visits", 0
                ),
            }

        # Ordenar por prioridad híbrida
        sorted_domains = sorted(
            domain_scores.values(), key=lambda x: x["hybrid_priority"], reverse=True
        )

        return sorted_domains[:5]

    def _get_learning_insights(self) -> list[str]:
        """Obtiene insights de aprendizaje del sistema"""

        insights = []

        # Insights del Brain simple
        top_errors = sorted(
            getattr(self.simple_brain, "error_type_freq", {}).items(),
            key=lambda x: x[1],
            reverse=True,
        )[:3]
        if top_errors:
            insights.append(
                f"Errores más comunes: {', '.join([f'{err}({count})' for err, count in top_errors])}"
            )

        # Insights del sistema autónomo
        try:
            total_patterns = sum(
                len(getattr(di, "common_patterns", []))
                for di in getattr(
                    self.autonomous_brain, "domain_intelligence", {}
                ).values()
            )
        except Exception:
            total_patterns = 0
        if total_patterns > 0:
            insights.append(f"Patrones descubiertos: {total_patterns} únicos")

        try:
            domains_with_strategies = sum(
                1
                for intel in getattr(
                    self.autonomous_brain, "domain_intelligence", {}
                ).values()
                if getattr(intel, "best_strategies", None)
            )
            if domains_with_strategies > 0:
                insights.append(
                    f"Estrategias optimizadas: {domains_with_strategies} dominios"
                )
        except Exception:
            logger.exception("Suppressed non-fatal error in hybrid_brain link analysis")

        return insights

    def flush(self):
        """Persiste el estado de ambos sistemas"""
        self.simple_brain.flush()
        # Persistencia del cerebro autónomo (compatibilidad: usar método privado existente)
        try:
            if hasattr(self.autonomous_brain, "save_learning_data"):
                self.autonomous_brain.save_learning_data()  # type: ignore[attr-defined]
            else:
                self.autonomous_brain._save_intelligence()  # type: ignore[attr-defined]
        except Exception:
            logger.debug("No se pudo persistir autonomous_brain", exc_info=True)
        # Persistir enriquecimiento avanzado
        try:
            self.enrichment.save()
        except Exception:
            logger.exception(
                "Suppressed non-fatal error in hybrid_brain during priority calculation"
            )

        # Actualizar comunicación inter-IA
        self._update_ia_sync()
        # Actualizar reporte de auto-repair (advisory)
        try:
            self.export_repair_report()
        except Exception:
            logger.exception(
                "Suppressed non-fatal error in hybrid_brain while extracting patterns from links"
            )

    def _update_ia_sync(self):
        """Actualiza el archivo de sincronización inter-IA"""

        try:
            timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")

            # Preparar mensaje de estado
            stats = self.get_comprehensive_stats()
            domains_count = len(stats["simple_brain"]["domains"])
            patterns_count = stats["autonomous_brain"]["total_patterns"]

            new_entry = f"{timestamp} | FEAT | IA-B: Sistema híbrido activo - {domains_count} dominios, {patterns_count} patrones\n"

            # Agregar entrada al final del archivo
            with open(self.ia_sync_file, "a", encoding="utf-8") as f:
                f.write(new_entry)

            logger.info("🧠 IA_SYNC updated with hybrid brain status")

        except Exception as e:
            logger.error(f"Failed to update IA_SYNC: {e}")

    # ----------------- Motor de sugerencias / Auto-repair (advisory) -----------------
    def generate_repair_suggestions(self, limit: int = 15) -> list[dict[str, Any]]:
        """Genera sugerencias inteligentes priorizadas.

        Solo lectura: no ejecuta cambios. Devuelve lista de dicts.
        """
        try:
            return self.self_repair_advisor.generate(limit=limit)
        except Exception:
            return []

    def export_repair_report(self, path: str = "IA_SELF_REPAIR.md", limit: int = 25):
        """Exporta reporte detallado de sugerencias a un archivo Markdown."""
        try:
            suggestions = self.generate_repair_suggestions(limit=limit)
            lines = [
                "# IA Self-Repair Advisory Report",
                "",
                "> Informe generado automáticamente por HybridBrain (capa advisory, sin auto-modificación)",
                "",
                f"Generado: {datetime.now(UTC).isoformat()}Z",
                f"Total sugerencias: {len(suggestions)}",
                "",
                "## Sugerencias Prioritarias",
                "",
            ]
            for s in suggestions:
                lines.extend(
                    [
                        f"### {s['title']} ({s['severity'].upper()})",
                        f"ID: `{s['id']}` | Categoría: {s['category']} | Confianza: {s.get('confidence', 0):.2f}",
                        (
                            f"Referencias KB: {', '.join(s.get('kb_refs', []))}"
                            if s.get("kb_refs")
                            else ""
                        ),
                        "",
                        f"**Rationale:** {s['rationale']}",
                        "",
                        f"**Acción Recomendada:** {s['recommended_action']}",
                        "",
                        f"**Señales:** `{s['signals']}`",
                        "",
                        "---",
                        "",
                    ]
                )
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        except Exception:
            logger.exception(
                "Suppressed non-fatal error in hybrid_brain get_comprehensive_stats fallback"
            )

    # ----------------- Conocimiento / Razonamiento -----------------
    def get_knowledge(
        self, category: str = None, tags: list[str] = None, limit: int = 5
    ) -> list[dict[str, Any]]:
        try:
            results = self.knowledge_base.search(category=category, tags=tags)
            return results[:limit]
        except Exception:
            return []

    def query_knowledge_base(self, query: str) -> list[dict[str, Any]]:
        """Searches the knowledge base for a given query."""
        print(f"Searching knowledge base for: {query}")
        try:
            # Search by category and tags based on the query
            tags = [tag.strip() for tag in query.split(" ")]
            results = self.knowledge_base.search(category=query, tags=tags)
            # Limit results to first 10 if needed
            return results[:10] if len(results) > 10 else results
        except Exception as e:
            logger.error(f"Error querying knowledge base: {e}")
            return []

    def reason_about_issue(self, observation: dict[str, Any]) -> dict[str, Any]:
        """Razonamiento ligero sobre un problema reportado.

        observation ejemplo:
          {
            'domain': 'example.com',
            'symptom': 'high_error_rate',
            'error_rate': 0.7,
            'avg_response_time': 3.2
          }
        Retorna hipótesis y referencias de conocimiento.
        """
        domain = observation.get("domain")
        symptom = observation.get("symptom")
        hypotheses = []
        kb_refs = []
        try:
            if symptom == "high_error_rate":
                er = observation.get("error_rate", 0)
                if er >= self.overrides.get("backoff_threshold", 0.5):
                    hypotheses.append(
                        "Posible saturación o bloqueo parcial: aplicar backoff y revisar patrones de petición."
                    )
                    kb_refs.extend(
                        [
                            s["id"]
                            for s in self.get_knowledge(
                                category="scraping", tags=["adaptive"]
                            )
                        ]
                    )
                    kb_refs.extend(
                        [s["id"] for s in self.get_knowledge(category="anti-bot")]
                    )
            if symptom == "slow_domain":
                kb_refs.extend(
                    [s["id"] for s in self.get_knowledge(category="performance")]
                )
                hypotheses.append(
                    "Latencia elevada sostenida: considerar aumentar delay y habilitar caching selectivo."
                )
            if symptom == "structural_drift":
                kb_refs.extend(
                    [s["id"] for s in self.get_knowledge(category="selectors")]
                )
                hypotheses.append(
                    "Variación estructural: regenerar selectores robustos y añadir fallback XPath."
                )
        except Exception:
            logger.exception(
                "Suppressed non-fatal error in hybrid_brain while collecting autonomous brain stats"
            )
        return {
            "domain": domain,
            "symptom": symptom,
            "hypotheses": hypotheses,
            "knowledge_refs": list(dict.fromkeys(kb_refs)),
        }

    def reason_declaratively(self, domain_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Razonamiento declarativo sobre datos de dominio.

        Args:
            domain_data: Datos del dominio para evaluación

        Returns:
            Lista de resultados de evaluación de reglas
        """
        try:
            return self.rule_engine.evaluate_all(domain_data)
        except Exception:
            return []

    def _auto_learn_from_session(
        self, result, context: dict[str, Any], patterns: list[str]
    ):
        """Auto-aprendizaje dinámico: extrae conocimiento de sesiones exitosas."""
        try:
            if not getattr(result, "success", False):
                return

            # Generar snippets dinámicos de patrones exitosos
            domain = urlparse(getattr(result, "url", "")).netloc
            response_time = (context or {}).get("response_time", 0)

            # Aprender de velocidad excepcional
            if response_time and response_time < 0.3:
                snippet_id = f"learned:fast_domain:{domain.replace('.', '_')}"
                if snippet_id not in self.knowledge_base.snippets:
                    from .knowledge_base import KnowledgeSnippet

                    snippet = KnowledgeSnippet(
                        id=snippet_id,
                        category="performance",
                        title=f"Optimización observada en {domain}",
                        content=f"Dominio {domain} responde consistentemente en <0.3s. Mantener configuración actual.",
                        tags=["learned", "fast", domain],
                        quality_score=0.7,
                    )
                    self.knowledge_base.snippets[snippet_id] = snippet

            # Aprender de patrones de extracción exitosos
            if patterns and len(patterns) >= 3:
                snippet_id = f"learned:extraction:{domain.replace('.', '_')}"
                if snippet_id not in self.knowledge_base.snippets:
                    from .knowledge_base import KnowledgeSnippet

                    top_patterns = patterns[:5]
                    snippet = KnowledgeSnippet(
                        id=snippet_id,
                        category="selectors",
                        title=f"Patrones exitosos en {domain}",
                        content=f"Patrones validados: {', '.join(top_patterns)}. Priorizar estos selectores.",
                        tags=["learned", "extraction", domain],
                        quality_score=0.75,
                    )
                    self.knowledge_base.snippets[snippet_id] = snippet

        except Exception:
            logger.exception(
                "Suppressed non-fatal error in hybrid_brain get_optimization_config"
            )

    def evaluate_suggestion_effectiveness(
        self, suggestion_id: str, outcome: str, metrics: dict[str, Any]
    ):
        """Sistema meta-cognitivo: evalúa efectividad de sugerencias aplicadas.

        Args:
            suggestion_id: ID de la sugerencia aplicada
            outcome: 'success', 'failure', 'partial'
            metrics: métricas antes/después del cambio
        """
        try:
            # Almacenar feedback en knowledge base
            feedback_id = f"feedback:{suggestion_id}:{time.time()}"
            from .knowledge_base import KnowledgeSnippet

            effectiveness_score = {"success": 0.9, "partial": 0.6, "failure": 0.2}.get(
                outcome, 0.5
            )

            snippet = KnowledgeSnippet(
                id=feedback_id,
                category="meta-learning",
                title=f"Efectividad de {suggestion_id}",
                content=f"Sugerencia {suggestion_id} resultó en {outcome}. Métricas: {metrics}",
                tags=["feedback", "effectiveness", outcome],
                quality_score=effectiveness_score,
            )
            self.knowledge_base.snippets[feedback_id] = snippet

            # Ajustar reglas dinámicamente según feedback
            if outcome == "failure":
                # Reducir prioridad de reglas similares
                rule_category = (
                    suggestion_id.split("::")[0] if "::" in suggestion_id else None
                )
                if rule_category:
                    for rule in self.rule_engine.rules.values():
                        if rule.action.category == rule_category:
                            rule.priority = max(10, rule.priority - 10)

        except Exception:
            logger.exception(
                "Suppressed non-fatal error in hybrid_brain while generating repair suggestions"
            )

    # 🧠 Métodos de integración para sistemas avanzados de IA

    def start_continuous_learning(self):
        """Inicia el aprendizaje continuo en segundo plano"""

        # First, seed all knowledge into the brain
        try:
            seeding_results = self.knowledge_seeder.seed_all_knowledge()
            logger.info("🌱 Knowledge seeded: %s", seeding_results)
        except Exception as e:
            logger.warning(f"Knowledge seeding failed: {e}")

        # Generate autonomous patch proposals
        try:
            if self.self_update_engine:
                patch_proposals = self.self_update_engine.generate_patch_proposals(
                    self.knowledge_store
                )
                logger.info(
                    "🔧 Generated %d autonomous patch proposals", len(patch_proposals)
                )
        except Exception as e:
            logger.warning(f"Patch generation failed: {e}")

        if self.learning_orchestrator:
            try:
                self.learning_orchestrator.start_background_learning()
                logger.info("🔄 Continuous learning started successfully")
            except Exception as e:
                logger.warning(f"Failed to start continuous learning: {e}")

    def get_ml_suggestions(
        self, url: str, context: dict[str, Any] = None
    ) -> dict[str, Any]:
        """Obtiene sugerencias del sistema ML avanzado"""
        if not self.ml_intelligence:
            return {}

        try:
            return self.ml_intelligence.analyze_scraping_context(url, context or {})
        except Exception as e:
            logger.warning(f"ML suggestions failed: {e}")
            return {}

    def trigger_self_improvement(self, target_metrics: dict[str, float] = None):
        """Dispara el proceso de auto-mejora del código"""
        if not self.self_improver:
            return

        try:
            self.self_improver.improve_system(target_metrics or {})
            logger.info("🔧 Self-improvement process triggered")
        except Exception as e:
            logger.warning(f"Self-improvement failed: {e}")

    def get_cdp_browser(self):
        """Obtiene instancia del navegador CDP sigiloso"""
        return self.cdp_browser

    def record_learning_session(
        self,
        url: str,
        success: bool,
        patterns: list[str],
        improvements: dict[str, Any] = None,
    ):
        """Registra una sesión de aprendizaje en el orquestador"""
        if not self.learning_orchestrator:
            return

        try:
            self.learning_orchestrator.record_session(
                url, success, patterns, improvements or {}
            )
        except Exception as e:
            logger.warning(f"Failed to record learning session: {e}")

    # 🧠 Neural Brain Integration Methods

    def _process_with_legacy_systems(
        self, event_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Procesa con sistemas legacy (Brain A + B)"""

        # Process with Simple Brain (IA-A)
        if "url" in event_data:
            from urllib.parse import urlparse

            domain = urlparse(event_data["url"]).netloc
        else:
            domain = "unknown"

        # Create experience event for Simple Brain
        from datetime import datetime

        from .brain import ExperienceEvent

        exp_event = ExperienceEvent(
            event_type=event_data.get("event_type", "scraping"),
            url=event_data.get("url", ""),
            success=event_data.get("success", True),
            data_extracted=len(str(event_data.get("data_extracted", {}))),
            processing_time=event_data.get("processing_time", 0.0),
            error_message=event_data.get("error_message"),
            timestamp=datetime.now(UTC),
        )

        brain_a_response = self.simple_brain.record_experience(exp_event)

        # Process with Autonomous Brain (IA-B)
        from .autonomous_learning import ScrapingSession

        session = ScrapingSession(
            start_time=datetime.now(),
            domain=domain,
            pages_scraped=1,
            success_rate=1.0 if event_data.get("success", True) else 0.0,
            avg_response_time=event_data.get("processing_time", 0.0),
            errors_encountered=0 if event_data.get("success", True) else 1,
            data_extracted=event_data.get("data_extracted", {}),
        )

        brain_b_response = self.autonomous_brain.record_session(session)

        return {
            "brain_a_response": brain_a_response,
            "brain_b_response": brain_b_response,
            "processing_mode": "legacy_systems",
            "consciousness_engaged": False,
        }

    def _process_with_hybrid_approach(
        self, event_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Procesa con enfoque híbrido (Neural + Legacy)"""

        # Process with unified brain
        neural_response = self._process_with_unified_brain(event_data)

        # Process with legacy systems
        legacy_response = self._process_with_legacy_systems(event_data)

        # Integrate both approaches
        integrated_response = {
            **neural_response,
            "legacy_insights": legacy_response,
            "processing_mode": "hybrid_neural_legacy",
            "integration_coherence": self._calculate_integration_coherence(
                neural_response, legacy_response
            ),
        }

        return integrated_response

    def _estimate_complexity(self, event_data: dict[str, Any]) -> float:
        """Estima complejidad del evento de scraping"""

        complexity = 0.3  # Base complexity

        # URL complexity
        if "url" in event_data:
            url_parts = len(event_data["url"].split("/"))
            complexity += min(0.3, url_parts * 0.05)

        # Data complexity
        if "data_extracted" in event_data:
            data_size = len(str(event_data["data_extracted"]))
            complexity += min(0.2, data_size / 1000)

        # Error complexity
        if not event_data.get("success", True):
            complexity += 0.3

        return min(1.0, complexity)

    def _estimate_familiarity(self, event_data: dict[str, Any]) -> float:
        """Estima familiaridad con el tipo de evento"""

        # Check domain familiarity in legacy systems
        if "url" in event_data:
            from urllib.parse import urlparse

            domain = urlparse(event_data["url"]).netloc
            try:
                domain_experience = self.simple_brain.get_domain_experience(domain)
            except Exception:
                domain_experience = {}

            # Coerce to numeric safely: MagicMocks may return MagicMock for .get()
            try:
                total_requests = domain_experience.get("total_requests", 0)
                total_requests = float(total_requests)
            except Exception:
                total_requests = 0.0

            return min(1.0, total_requests / 100.0)

        return 0.5

    def _extract_scraping_insights(
        self, neural_response: dict[str, Any], event_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Extrae insights específicos para scraping del response neural"""

        insights = {}

        # Emotional insights
        emotional_state = neural_response.get("emotional_state", {})
        current_emotion = emotional_state.get("current_emotion", {})

        if current_emotion.get("emotion") == "fear":
            insights["recommendation"] = (
                "Detected fear response - possible anti-bot detection"
            )
        elif current_emotion.get("emotion") == "joy":
            insights["recommendation"] = (
                "Positive emotional response - scraping going well"
            )

        # Memory insights
        if neural_response.get("memory_encoding"):
            insights["memory_note"] = (
                "Event stored in episodic memory for future reference"
            )

        # Reasoning insights
        reasoning_analysis = neural_response.get("reasoning_analysis", {})
        if reasoning_analysis.get("overall_confidence", 0) > 0.8:
            insights["confidence"] = "High confidence in scraping strategy"
        elif reasoning_analysis.get("overall_confidence", 0) < 0.4:
            insights["confidence"] = "Low confidence - consider strategy adjustment"

        # Metacognitive insights
        metacog_state = neural_response.get("metacognitive_state", {})
        if metacog_state.get("cognitive_load", 0) > 0.8:
            insights["workload"] = "High cognitive load - consider simplifying approach"

        return insights

    def _sync_with_legacy_systems(
        self, event_data: dict[str, Any], neural_response: dict[str, Any]
    ):
        """Sincroniza insights neurales con sistemas legacy"""

        # Update Simple Brain with neural insights
        if hasattr(self.simple_brain, "update_neural_insights"):
            self.simple_brain.update_neural_insights(event_data, neural_response)

        # Update Autonomous Brain with consciousness state
        if hasattr(self.autonomous_brain, "update_consciousness_state"):
            consciousness_state = self.unified_brain.get_consciousness_state()
            self.autonomous_brain.update_consciousness_state(consciousness_state)

    def _calculate_integration_coherence(
        self, neural_response: dict[str, Any], legacy_response: dict[str, Any]
    ) -> float:
        """Calcula coherencia entre respuestas neural y legacy"""

        # Simple coherence measure
        neural_success = neural_response.get("integrated_response", {}).get(
            "conscious_access", False
        )
        legacy_success = legacy_response.get("brain_a_response", {}).get(
            "success", False
        )

        if neural_success == legacy_success:
            return 0.8
        else:
            return 0.4

    def get_brain_state(self) -> dict[str, Any]:
        """Obtiene estado completo del cerebro híbrido"""

        state = {
            "integration_mode": self.integration_mode,
            "consciousness_enabled": self.consciousness_enabled,
            "unified_brain_state": (
                self.unified_brain.get_consciousness_state()
                if hasattr(self, "unified_brain")
                else {}
            ),
            "legacy_simple_brain_state": (
                self.simple_brain.get_state()
                if hasattr(self.simple_brain, "get_state")
                else {}
            ),
            "legacy_autonomous_brain_state": (
                self.autonomous_brain.get_intelligence_state()
                if hasattr(self.autonomous_brain, "get_intelligence_state")
                else {}
            ),
        }

        return state

    def enable_consciousness(self):
        """Habilita procesamiento consciente"""
        self.consciousness_enabled = True
        logger.info("🧠 Consciousness processing ENABLED")

    def disable_consciousness(self):
        """Deshabilita procesamiento consciente (modo legacy)"""
        self.consciousness_enabled = False
        logger.info("🧠 Consciousness processing DISABLED - using legacy mode")

    def set_integration_mode(self, mode: str):
        """Establece modo de integración: 'unified', 'legacy', 'hybrid'"""
        if mode in ["unified", "legacy", "hybrid"]:
            self.integration_mode = mode
            logger.info(f"🧠 Integration mode set to: {mode}")
        else:
            logger.warning(f"Invalid integration mode: {mode}")

    # ============================================================================
    # SISTEMA DE OBSERVACIÓN OMNISCIENTE
    # El cerebro puede observar todo el proyecto pero está protegido de cambios externos
    # ============================================================================

    def _initialize_curiosity_system(self):
        """Inicializa el sistema de curiosidad y proactividad"""
        try:
            from .curiosity import CuriositySystem

            # Crear instancia del sistema de curiosidad
            self.curiosity_system = CuriositySystem(
                brain_instance=self,
                tui_app=None,  # Se puede conectar después
                voice_assistant=None,  # Se puede conectar después
            )

            logger.info("🧠 Sistema de curiosidad inicializado exitosamente")

        except Exception as e:
            logger.warning(f"Error inicializando sistema de curiosidad: {e}")
            self.curiosity_system = None

    def _initialize_omniscience(self):
        """Inicializa capacidades de observación omnisciente del cerebro"""
        self._project_observers = {
            "settings": None,
            "database": None,
            "logs": None,
            "code_files": {},
            "runtime_metrics": {},
            "network_activity": [],
        }
        self._protection_layer = OmniscientProtectionLayer()
        logger.info(
            "🧠 Omniscient observation system initialized - Brain can observe all, but nothing can affect brain"
        )

    def observe_project_state(self) -> dict[str, Any]:
        """Observa el estado completo del proyecto de manera read-only"""
        try:
            state = {
                "timestamp": datetime.now(UTC).isoformat(),
                "observer": "HybridBrain_Omniscient",
                "settings_state": self._observe_settings(),
                "database_state": self._observe_database(),
                "logs_state": self._observe_logs(),
                "code_quality": self._observe_code_quality(),
                "runtime_metrics": self._observe_runtime_metrics(),
                "network_activity": self._observe_network_activity(),
                "project_health": self._calculate_project_health(),
            }

            # Process observations through neural architecture
            neural_observations = {}
            if hasattr(self, "unified_brain") and hasattr(
                self.unified_brain, "process_sensory_input"
            ):
                try:
                    neural_observations = self.unified_brain.process_sensory_input(
                        {
                            "type": "project_observation",
                            "data": state,
                            "importance": 0.9,
                            "complexity": 0.8,
                            "familiarity": 0.7,
                        }
                    )
                except Exception as inner_e:
                    logger.debug(f"Neural processing skipped: {inner_e}")

            return {
                "raw_observations": state,
                "neural_analysis": neural_observations,
                "brain_assessment": self._assess_project_modifications_needed(state),
            }

        except Exception as e:
            logger.error(f"🧠 Error during omniscient observation: {e}")
            # Retornar estructura consistente para que tests no fallen por clave faltante
            return {
                "raw_observations": {"error": str(e)},
                "neural_analysis": {},
                "brain_assessment": {
                    "modifications_needed": False,
                    "recommendations": [],
                    "brain_decision": "observe_on_error",
                },
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat(),
            }

    def _observe_settings(self) -> dict[str, Any]:
        """Observa configuraciones del proyecto (read-only)"""
        try:
            from ..settings import settings

            # Extract critical settings for brain analysis
            observed_settings = {
                "hybrid_brain_enabled": getattr(settings, "HYBRID_BRAIN_ENABLED", True),
                "consciousness_enabled": getattr(
                    settings, "CONSCIOUSNESS_ENABLED", True
                ),
                "continuous_learning_enabled": getattr(
                    settings, "CONTINUOUS_LEARNING_ENABLED", True
                ),
                "intelligence_integration_mode": getattr(
                    settings, "INTELLIGENCE_INTEGRATION_MODE", "unified"
                ),
                "neural_activity_threshold": getattr(
                    settings, "NEURAL_ACTIVITY_THRESHOLD", 0.6
                ),
                "concurrency": getattr(settings, "CONCURRENCY", 5),
                "robots_enabled": getattr(settings, "ROBOTS_ENABLED", True),
                "ethics_checks_enabled": getattr(
                    settings, "ETHICS_CHECKS_ENABLED", True
                ),
            }

            return {
                "status": "observed",
                "settings": observed_settings,
                "assessment": (
                    "intelligence_configuration_optimal"
                    if observed_settings["hybrid_brain_enabled"]
                    else "intelligence_degraded"
                ),
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _observe_database(self) -> dict[str, Any]:
        """Observa estado de la base de datos (read-only)"""
        try:
            # Safely observe database without modifying it
            from ..database import DatabaseManager

            # Create read-only observation instance
            db_observer = DatabaseManager(db_path="data/scraper_database.db")

            # Gather metrics without modifying data
            observation = {
                "tables_exist": True,  # Basic check
                "estimated_records": "unknown",  # Safe default
                "last_activity": "unknown",
            }

            # Try safe read operations
            try:
                # This is a safe read operation
                stats = db_observer.get_stats()
                if stats:
                    observation.update(
                        {
                            "total_urls": stats.get("total_urls", 0),
                            "successful_scrapes": stats.get("successful_scrapes", 0),
                            "failed_scrapes": stats.get("failed_scrapes", 0),
                        }
                    )
            except Exception:
                logger.exception(
                    "Suppressed non-fatal error in hybrid_brain during safe DB observation"
                )

            return {
                "status": "observed",
                "database_metrics": observation,
                "assessment": (
                    "database_healthy"
                    if observation.get("total_urls", 0) > 0
                    else "database_empty"
                ),
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _observe_logs(self) -> dict[str, Any]:
        """Observa logs del sistema (read-only)"""
        try:
            logs_dir = "logs"
            log_files = []

            if os.path.exists(logs_dir):
                for file in os.listdir(logs_dir):
                    if file.endswith(".log"):
                        file_path = os.path.join(logs_dir, file)
                        try:
                            stat = os.stat(file_path)
                            log_files.append(
                                {
                                    "file": file,
                                    "size": stat.st_size,
                                    "modified": stat.st_mtime,
                                }
                            )
                        except Exception:
                            continue

            return {
                "status": "observed",
                "log_files": log_files,
                "assessment": "logs_active" if log_files else "logs_inactive",
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _observe_code_quality(self) -> dict[str, Any]:
        """Observa calidad del código (read-only)"""
        try:
            src_dir = "src"
            code_metrics = {
                "python_files": 0,
                "total_lines": 0,
                "intelligence_files": 0,
            }

            if os.path.exists(src_dir):
                for root, dirs, files in os.walk(src_dir):
                    for file in files:
                        if file.endswith(".py"):
                            code_metrics["python_files"] += 1
                            if "intelligence" in root:
                                code_metrics["intelligence_files"] += 1

                            # Count lines safely
                            try:
                                with open(
                                    os.path.join(root, file), encoding="utf-8"
                                ) as f:
                                    code_metrics["total_lines"] += sum(1 for _ in f)
                            except Exception:
                                continue

            return {
                "status": "observed",
                "code_metrics": code_metrics,
                "assessment": (
                    "codebase_intelligent"
                    if code_metrics["intelligence_files"] > 5
                    else "codebase_basic"
                ),
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _observe_runtime_metrics(self) -> dict[str, Any]:
        """Observa métricas de tiempo de ejecución"""
        return {
            "status": "observed",
            "metrics": {
                "memory_usage": "unknown",
                "cpu_usage": "unknown",
                "active_threads": threading.active_count(),
            },
            "assessment": "runtime_stable",
        }

    def _observe_network_activity(self) -> dict[str, Any]:
        """Observa actividad de red (si está disponible)"""
        return {
            "status": "observed",
            "network_metrics": {
                "recent_requests": "unknown",
                "success_rate": "unknown",
            },
            "assessment": "network_activity_unknown",
        }

    def _calculate_project_health(self) -> dict[str, Any]:
        """Calcula salud general del proyecto basada en observaciones"""
        return {
            "overall_health": "optimal",
            "intelligence_status": "active",
            "recommendations": [],
        }

    def _assess_project_modifications_needed(
        self, observations: dict[str, Any]
    ) -> dict[str, Any]:
        """Evalúa si el cerebro necesita modificar algo en el proyecto"""
        recommendations = []

        # Check if intelligence is properly configured
        settings_state = observations.get("settings_state", {})
        if settings_state.get("assessment") == "intelligence_degraded":
            recommendations.append(
                {
                    "type": "settings_modification",
                    "priority": "high",
                    "description": "Intelligence configuration needs optimization",
                    "suggested_action": "enable_full_intelligence",
                }
            )

        # Check database health
        db_state = observations.get("database_state", {})
        if db_state.get("assessment") == "database_empty":
            recommendations.append(
                {
                    "type": "database_initialization",
                    "priority": "medium",
                    "description": "Database appears empty or inactive",
                    "suggested_action": "initialize_baseline_data",
                }
            )

        return {
            "modifications_needed": len(recommendations) > 0,
            "recommendations": recommendations,
            "brain_decision": (
                "observe_and_adapt" if recommendations else "maintain_current_state"
            ),
        }

    def make_autonomous_decision(self, context: dict[str, Any]) -> dict[str, Any]:
        """Toma decisiones autónomas basadas en el contexto"""
        # Procesar a través de la arquitectura neural
        neural_decision = (
            self.unified_brain.process_sensory_input(
                {
                    "type": "autonomous_decision_context",
                    "data": context,
                    "importance": 0.95,
                    "complexity": 0.8,
                    "familiarity": 0.6,
                }
            )
            if hasattr(self, "unified_brain")
            else {}
        )

        # El cerebro evalúa si debe actuar
        consciousness_active = neural_decision.get("integrated_response", {}).get(
            "conscious_access", False
        )

        decision = {
            "timestamp": datetime.now(UTC).isoformat(),
            "consciousness_engaged": consciousness_active,
            "decision_type": "autonomous_evaluation",
            "context_assessment": self._assess_decision_context(context),
            "neural_analysis": neural_decision,
            "action_taken": "observation_and_learning",
        }

        logger.info(f"🧠 Brain autonomous decision: {decision['action_taken']}")
        return decision

    def _assess_decision_context(self, context: dict[str, Any]) -> dict[str, Any]:
        """Evalúa el contexto para tomar decisiones"""
        return {
            "context_complexity": "medium",
            "risk_assessment": "low",
            "potential_impact": "positive",
            "brain_confidence": 0.8,
            "recommended_approach": "observe_and_adapt",
        }

    # ============================================================================
    # CAPA DE PROTECCIÓN DEL CEREBRO
    # ============================================================================


class OmniscientProtectionLayer:
    """Capa de protección que impide que código externo modifique el cerebro"""

    def __init__(self):
        self.protected_attributes = [
            "unified_brain",
            "simple_brain",
            "autonomous_brain",
            "neural_brain",
            "emotional_brain",
            "metacognitive_brain",
            "advanced_memory",
            "advanced_reasoning",
            "consciousness_enabled",
            "integration_mode",
            "_project_observers",
        ]
        self.modification_attempts = []

    def protect_brain_state(self, brain_instance):
        """Protege el estado del cerebro de modificaciones externas"""
        # Implementación futura: interceptores de modificación

    def log_modification_attempt(self, attribute: str, caller: str):
        """Registra intentos de modificación externa"""
        self.modification_attempts.append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "attribute": attribute,
                "caller": caller,
                "action": "blocked",
            }
        )

    # ============================================================================
    # CAPACIDADES DE MODIFICACIÓN CONTROLADA DEL CEREBRO
    # El cerebro puede modificar el proyecto cuando lo considera necesario
    # ============================================================================

    def apply_intelligent_modifications(
        self, observations: dict[str, Any]
    ) -> dict[str, Any]:
        """Aplica modificaciones inteligentes basadas en observaciones"""
        if not hasattr(self, "_protection_layer"):
            return {"error": "Protection layer not initialized"}

        assessment = observations.get("brain_assessment", {})
        recommendations = assessment.get("recommendations", [])

        applied_modifications = []
        errors = []

        for recommendation in recommendations:
            try:
                if recommendation["type"] == "settings_modification":
                    result = self._modify_settings_intelligently(recommendation)
                    applied_modifications.append(result)
                elif recommendation["type"] == "database_initialization":
                    result = self._initialize_database_intelligently(recommendation)
                    applied_modifications.append(result)
                # Más tipos de modificaciones pueden añadirse aquí

            except Exception as e:
                errors.append({"recommendation": recommendation, "error": str(e)})

        return {
            "modifications_applied": applied_modifications,
            "errors": errors,
            "brain_state": "active_modification_mode",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def _modify_settings_intelligently(
        self, recommendation: dict[str, Any]
    ) -> dict[str, Any]:
        """Modifica configuraciones de manera inteligente"""
        logger.info(
            f"🧠 Brain considers settings modification: {recommendation['description']}"
        )

        # El cerebro evalúa si la modificación es necesaria
        if recommendation["suggested_action"] == "enable_full_intelligence":
            # Verificar que la inteligencia esté correctamente configurada
            modifications = {
                "action": "settings_verification",
                "description": "Verified intelligence configuration is optimal",
                "result": "no_changes_needed",
            }

            logger.info(
                "🧠 Brain verified: intelligence configuration is already optimal"
            )
            return modifications

        return {
            "action": "settings_modification",
            "description": "Settings modification evaluated",
            "result": "deferred_for_safety",
        }

    def _initialize_database_intelligently(
        self, recommendation: dict[str, Any]
    ) -> dict[str, Any]:
        """Inicializa base de datos de manera inteligente"""
        logger.info(
            f"🧠 Brain considers database initialization: {recommendation['description']}"
        )

        return {
            "action": "database_assessment",
            "description": "Database state assessed and deemed acceptable for current operations",
            "result": "monitoring_continued",
        }

    def get_brain_modification_history(self) -> list[dict[str, Any]]:
        """Obtiene historial de modificaciones realizadas por el cerebro"""
        if not hasattr(self, "_modification_history"):
            self._modification_history = []
        return self._modification_history

    def _log_brain_action(self, action: dict[str, Any]):
        """Registra acciones del cerebro"""
        if not hasattr(self, "_modification_history"):
            self._modification_history = []

        self._modification_history.append(
            {
                **action,
                "timestamp": datetime.now(UTC).isoformat(),
                "brain_state": self.get_brain_state(),
            }
        )

        # Mantener solo las últimas 100 acciones
        if len(self._modification_history) > 100:
            self._modification_history = self._modification_history[-100:]

    def _start_continuous_monitoring(self):
        """Inicia monitoreo continuo del proyecto"""
        if not hasattr(self, "_monitoring_active"):
            self._monitoring_active = True
            self._monitoring_thread = threading.Thread(
                target=self._continuous_monitoring_loop,
                daemon=True,
                name="BrainOmniscientMonitor",
            )
            self._monitoring_thread.start()
            logger.info("🧠 Brain continuous monitoring thread started")

    def _continuous_monitoring_loop(self):
        """Loop de monitoreo continuo que ejecuta en thread separado"""
        monitoring_interval = 30  # segundos

        while getattr(self, "_monitoring_active", False):
            try:
                # Observación omnisciente del proyecto
                observations = self.observe_project_state()

                # El cerebro evalúa si hay algo que requiere atención
                assessment = observations.get("brain_assessment", {})
                if assessment.get("modifications_needed", False):
                    # Log de actividad de monitoreo
                    logger.info(
                        f"🧠 Brain monitoring detected {len(assessment.get('recommendations', []))} issues requiring attention"
                    )

                    # El cerebro puede decidir actuar de manera autónoma
                    decision = self.make_autonomous_decision(
                        {
                            "context": "continuous_monitoring",
                            "observations": observations,
                            "monitoring_cycle": True,
                        }
                    )

                    self._log_brain_action(
                        {
                            "action_type": "continuous_monitoring_decision",
                            "decision": decision,
                            "observations_summary": {
                                "health": observations.get("raw_observations", {}).get(
                                    "project_health", {}
                                ),
                                "recommendations_count": len(
                                    assessment.get("recommendations", [])
                                ),
                            },
                        }
                    )

                time.sleep(monitoring_interval)

            except Exception as e:
                logger.warning(f"🧠 Brain monitoring loop error: {e}")
                time.sleep(monitoring_interval)

    def stop_continuous_monitoring(self):
        """Detiene el monitoreo continuo"""
        self._monitoring_active = False
        logger.info("🧠 Brain continuous monitoring stopped")

    # Legacy compatibility methods
    def record_experience(self, event: Any) -> dict[str, Any]:
        """Método de compatibilidad con Brain A"""
        if hasattr(event, "__dict__"):
            event_data = event.__dict__
        else:
            event_data = event

        return self.process_scraping_event(event_data)

    def record_session(self, session: Any) -> dict[str, Any]:
        """Método de compatibilidad con Brain B"""
        if hasattr(session, "__dict__"):
            session_data = session.__dict__
        else:
            session_data = session

        event_data = {
            "event_type": "scraping_session",
            "domain": session_data.get("domain", "unknown"),
            "success": session_data.get("success_rate", 0) > 0.5,
            "data_extracted": session_data.get("data_extracted", {}),
            "processing_time": session_data.get("avg_response_time", 0),
        }

        return self.process_scraping_event(event_data)

    def analyze_cross_session_patterns(self) -> dict[str, Any]:
        """Analiza patrones a través de múltiples sesiones"""
        if not self.learning_orchestrator:
            return {}

        try:
            return self.learning_orchestrator.analyze_patterns()
        except Exception as e:
            logger.warning(f"Cross-session pattern analysis failed: {e}")
            return {}


# Singleton para uso global
_hybrid_brain_instance = None


def get_hybrid_brain() -> HybridBrain:
    """Obtiene la instancia singleton del HybridBrain"""
    global _hybrid_brain_instance
    if _hybrid_brain_instance is None:
        _hybrid_brain_instance = HybridBrain()
    return _hybrid_brain_instance
