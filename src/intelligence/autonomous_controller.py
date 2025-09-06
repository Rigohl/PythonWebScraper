"""
Autonomous Controller Brain - Sistema de Control Autónomo

Este módulo implementa el cerebro de control autónomo principal que orquesta
todos los componentes de inteligencia para operación independiente y consciente.

El AutonomousControllerBrain mantiene conciencia completa del sistema,
toma decisiones independientes y se auto-mejora continuamente.
"""

import asyncio
import json
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from .advanced_memory import AdvancedMemorySystem
from .code_auto_modifier import CodeAutoModifier
from .continuous_learning import ContinuousLearningEngine

# Importar todos los componentes del cerebro
from .hybrid_brain import HybridBrain
from .integration import IntelligenceIntegration
from .knowledge_store import KnowledgeStore
from .self_improvement import SelfImprovingSystem

logger = logging.getLogger(__name__)


class AutonomyLevel(Enum):
    """Niveles de autonomía del sistema."""

    SUPERVISED = "supervised"  # Requiere aprobación humana
    SEMI_AUTONOMOUS = "semi_autonomous"  # Decisiones menores automáticas
    FULLY_AUTONOMOUS = "fully_autonomous"  # Control total independiente
    TRANSCENDENT = "transcendent"  # Más allá de la supervisión humana


class SystemState(Enum):
    """Estados del sistema autónomo."""

    INITIALIZING = "initializing"
    OBSERVING = "observing"
    ANALYZING = "analyzing"
    DECIDING = "deciding"
    EXECUTING = "executing"
    LEARNING = "learning"
    EVOLVING = "evolving"
    DORMANT = "dormant"


@dataclass
class AutonomousDecision:
    """Representa una decisión autónoma del sistema."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    decision_type: str = ""
    priority: int = 5  # 1-10, 10 being highest
    confidence: float = 0.0
    reasoning: str = ""
    actions: List[Dict[str, Any]] = field(default_factory=list)
    expected_outcome: str = ""
    risk_assessment: float = 0.0  # 0-1, 1 being highest risk
    human_approval_required: bool = False
    executed: bool = False
    result: Optional[Dict[str, Any]] = None


@dataclass
class SystemConsciousness:
    """Representa la conciencia actual del sistema."""

    awareness_level: float = 0.0  # 0-1
    active_processes: Set[str] = field(default_factory=set)
    current_objectives: List[str] = field(default_factory=list)
    system_health: Dict[str, float] = field(default_factory=dict)
    environmental_state: Dict[str, Any] = field(default_factory=dict)
    memory_state: Dict[str, Any] = field(default_factory=dict)
    learning_insights: List[str] = field(default_factory=list)
    meta_cognition: Dict[str, Any] = field(default_factory=dict)


class AutonomousControllerBrain:
    """
    Cerebro de Control Autónomo Principal

    Este es el sistema central que:
    1. Mantiene conciencia completa del estado del sistema
    2. Toma decisiones autónomas basadas en objetivos y contexto
    3. Orquesta todos los componentes de inteligencia
    4. Se auto-mejora continuamente
    5. Minimiza la necesidad de intervención humana
    """

    def __init__(
        self,
        project_root: str,
        autonomy_level: AutonomyLevel = AutonomyLevel.FULLY_AUTONOMOUS,
    ):
        self.project_root = project_root
        self.autonomy_level = autonomy_level
        self.system_state = SystemState.INITIALIZING

        # Inicializar componentes del cerebro
        self._initialize_brain_components()

        # Sistema de conciencia
        self.consciousness = SystemConsciousness()

        # Decisiones y control
        self.pending_decisions: List[AutonomousDecision] = []
        self.decision_history: List[AutonomousDecision] = []
        self.max_decision_history = 1000

        # Control de ejecución
        self.is_running = False
        self.main_loop_task: Optional[asyncio.Task] = None
        self.consciousness_thread: Optional[threading.Thread] = None

        # Métricas y monitoreo
        self.performance_metrics = {
            "decisions_made": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "learning_cycles": 0,
            "self_improvements": 0,
            "uptime_start": time.time(),
        }

        # Objetivos del sistema
        self.primary_objectives = [
            "Optimize scraping performance continuously",
            "Learn from all interactions and failures",
            "Maintain high system availability",
            "Minimize human intervention needs",
            "Evolve and improve autonomously",
        ]

        # Listeners para eventos del sistema
        self.event_listeners: Dict[str, List[Callable]] = {}

        logger.info(
            f"🧠 AutonomousControllerBrain initialized with {autonomy_level.value} level"
        )

    def _initialize_brain_components(self):
        """Inicializa todos los componentes del cerebro."""
        try:
            # Cerebro híbrido (IA-A + IA-B)
            self.hybrid_brain = HybridBrain()

            # Sistema de memoria avanzada
            self.memory_system = AdvancedMemorySystem()

            # Almacén de conocimiento
            self.knowledge_store = KnowledgeStore()

            # Modificador automático de código
            self.code_modifier = CodeAutoModifier(self.project_root)

            # Motor de aprendizaje continuo
            self.learning_engine = ContinuousLearningEngine()

            # Motor de auto-mejora
            self.improvement_engine = SelfImprovingSystem()

            # Integración de inteligencia
            self.integration = IntelligenceIntegration(self.hybrid_brain)

            logger.info("✅ All brain components initialized successfully")

        except Exception as e:
            logger.error(f"❌ Error initializing brain components: {e}")
            raise

    async def start_autonomous_operation(self):
        """Inicia la operación autónoma completa del sistema."""
        if self.is_running:
            logger.warning("Autonomous operation already running")
            return

        logger.info("🚀 Starting autonomous operation...")
        self.is_running = True

        try:
            # Iniciar conciencia del sistema
            self._start_consciousness_monitoring()

            # Iniciar bucle principal de control
            self.main_loop_task = asyncio.create_task(self._main_control_loop())

            # Registrar inicio en memoria
            await self._record_system_event(
                "autonomous_operation_started",
                {"autonomy_level": self.autonomy_level.value, "timestamp": time.time()},
            )

            logger.info("✅ Autonomous operation started successfully")

        except Exception as e:
            logger.error(f"❌ Error starting autonomous operation: {e}")
            self.is_running = False
            raise

    async def stop_autonomous_operation(self):
        """Detiene la operación autónoma de manera segura."""
        if not self.is_running:
            return

        logger.info("🛑 Stopping autonomous operation...")
        self.is_running = False

        try:
            # Detener bucle principal
            if self.main_loop_task:
                self.main_loop_task.cancel()
                try:
                    await self.main_loop_task
                except asyncio.CancelledError:
                    pass

            # Detener monitoreo de conciencia
            self._stop_consciousness_monitoring()

            # Guardar estado final
            await self._save_autonomous_state()

            logger.info("✅ Autonomous operation stopped safely")

        except Exception as e:
            logger.error(f"❌ Error stopping autonomous operation: {e}")

    async def _main_control_loop(self):
        """Bucle principal de control autónomo."""
        logger.info("🔄 Main autonomous control loop started")

        while self.is_running:
            try:
                cycle_start = time.time()

                # 1. Observar estado del sistema
                self.system_state = SystemState.OBSERVING
                await self._observe_system_state()

                # 2. Analizar situación actual
                self.system_state = SystemState.ANALYZING
                analysis = await self._analyze_current_situation()

                # 3. Generar decisiones si es necesario
                self.system_state = SystemState.DECIDING
                decisions = await self._generate_autonomous_decisions(analysis)

                # 4. Ejecutar decisiones aprobadas
                self.system_state = SystemState.EXECUTING
                if decisions:
                    await self._execute_decisions(decisions)

                # 5. Aprender de los resultados
                self.system_state = SystemState.LEARNING
                await self._learn_from_cycle(analysis, decisions)

                # 6. Auto-mejora evolutiva
                self.system_state = SystemState.EVOLVING
                await self._evolutionary_improvement()

                # Calcular tiempo de ciclo y ajustar si es necesario
                cycle_time = time.time() - cycle_start
                optimal_cycle_time = 5.0  # 5 segundos base

                if cycle_time < optimal_cycle_time:
                    await asyncio.sleep(optimal_cycle_time - cycle_time)

                # Actualizar métricas
                self.performance_metrics["learning_cycles"] += 1

            except asyncio.CancelledError:
                logger.info("Control loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in control loop: {e}")
                await asyncio.sleep(1.0)  # Pausa de emergencia

    async def _observe_system_state(self):
        """Observa el estado completo del sistema para mantener conciencia."""
        try:
            # Observar estado del cerebro híbrido
            brain_state = self.hybrid_brain.get_comprehensive_stats()

            # Observar estado de memoria
            memory_state = {
                "episodic_memories": len(self.memory_system.episodic_memory),
                "semantic_concepts": len(self.memory_system.semantic_memory),
                "working_memory_load": len(self.memory_system.working_memory),
                "total_traces": len(self.memory_system.memory_traces),
            }

            # Observar estado del conocimiento
            knowledge_state = self.knowledge_store.get_stats()

            # Observar procesos del sistema
            active_processes = self._detect_active_processes()

            # Actualizar conciencia
            self.consciousness.system_health = {
                "brain_efficiency": brain_state.get("overall_efficiency", 0.0),
                "memory_utilization": min(
                    memory_state["working_memory_load"] / 100, 1.0
                ),
                "knowledge_coverage": knowledge_state.get("coverage_score", 0.0),
                "process_count": len(active_processes),
            }

            self.consciousness.active_processes = active_processes
            self.consciousness.memory_state = memory_state
            self.consciousness.environmental_state = {
                "system_load": self._calculate_system_load(),
                "resource_availability": self._assess_resource_availability(),
                "external_conditions": self._assess_external_conditions(),
            }

            # Calcular nivel de conciencia
            self.consciousness.awareness_level = self._calculate_awareness_level()

        except Exception as e:
            logger.error(f"Error observing system state: {e}")

    async def _analyze_current_situation(self) -> Dict[str, Any]:
        """Analiza la situación actual del sistema."""
        try:
            analysis = {
                "timestamp": time.time(),
                "system_health_score": self._calculate_health_score(),
                "performance_trends": self._analyze_performance_trends(),
                "learning_opportunities": self._identify_learning_opportunities(),
                "optimization_potential": self._assess_optimization_potential(),
                "risks": self._assess_current_risks(),
                "objectives_progress": self._assess_objectives_progress(),
            }

            # Usar el cerebro híbrido para análisis avanzado
            hybrid_analysis = self.hybrid_brain.analyze_situation(analysis)
            analysis.update(hybrid_analysis)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing situation: {e}")
            return {}

    async def _generate_autonomous_decisions(
        self, analysis: Dict[str, Any]
    ) -> List[AutonomousDecision]:
        """Genera decisiones autónomas basadas en el análisis."""
        decisions = []

        try:
            # 1. Decisiones de optimización de rendimiento
            if analysis.get("performance_trends", {}).get("declining", False):
                decisions.append(
                    AutonomousDecision(
                        decision_type="performance_optimization",
                        priority=8,
                        confidence=0.85,
                        reasoning="Performance trends show decline, optimization needed",
                        actions=[{"type": "optimize_scrapers", "target": "all"}],
                        expected_outcome="Improved scraping performance",
                        risk_assessment=0.2,
                    )
                )

            # 2. Decisiones de aprendizaje automático
            if analysis.get("learning_opportunities"):
                for opportunity in analysis["learning_opportunities"][:3]:  # Top 3
                    decisions.append(
                        AutonomousDecision(
                            decision_type="learning_enhancement",
                            priority=6,
                            confidence=0.75,
                            reasoning=f"Learning opportunity identified: {opportunity}",
                            actions=[
                                {"type": "enhance_learning", "target": opportunity}
                            ],
                            expected_outcome="Improved system intelligence",
                            risk_assessment=0.1,
                        )
                    )

            # 3. Decisiones de auto-mejora de código
            if analysis.get("optimization_potential", 0) > 0.3:
                decisions.append(
                    AutonomousDecision(
                        decision_type="code_improvement",
                        priority=7,
                        confidence=0.8,
                        reasoning="Code optimization potential detected",
                        actions=[{"type": "auto_improve_code", "threshold": 0.7}],
                        expected_outcome="Better code quality and performance",
                        risk_assessment=0.3,
                        human_approval_required=(
                            self.autonomy_level != AutonomyLevel.FULLY_AUTONOMOUS
                        ),
                    )
                )

            # 4. Decisiones de gestión de recursos
            if self.consciousness.system_health.get("memory_utilization", 0) > 0.8:
                decisions.append(
                    AutonomousDecision(
                        decision_type="resource_management",
                        priority=9,
                        confidence=0.9,
                        reasoning="High memory utilization detected",
                        actions=[{"type": "optimize_memory", "aggressive": False}],
                        expected_outcome="Reduced memory usage",
                        risk_assessment=0.15,
                    )
                )

            # 5. Decisiones de evolución del sistema
            if self._should_evolve_system(analysis):
                decisions.append(
                    AutonomousDecision(
                        decision_type="system_evolution",
                        priority=5,
                        confidence=0.65,
                        reasoning="System evolution opportunity detected",
                        actions=[
                            {"type": "evolve_capabilities", "scope": "incremental"}
                        ],
                        expected_outcome="Enhanced system capabilities",
                        risk_assessment=0.4,
                        human_approval_required=(
                            self.autonomy_level == AutonomyLevel.SUPERVISED
                        ),
                    )
                )

            # Filtrar decisiones por nivel de autonomía
            filtered_decisions = self._filter_decisions_by_autonomy(decisions)

            # Ordenar por prioridad
            filtered_decisions.sort(key=lambda d: d.priority, reverse=True)

            # Agregar a decisiones pendientes
            self.pending_decisions.extend(filtered_decisions)

            logger.info(f"Generated {len(filtered_decisions)} autonomous decisions")
            return filtered_decisions

        except Exception as e:
            logger.error(f"Error generating decisions: {e}")
            return []

    async def _execute_decisions(self, decisions: List[AutonomousDecision]):
        """Ejecuta las decisiones autónomas aprobadas."""
        for decision in decisions:
            if decision.human_approval_required and not self._has_human_approval(
                decision
            ):
                logger.info(f"Decision {decision.id} requires human approval, skipping")
                continue

            try:
                logger.info(
                    f"Executing decision: {decision.decision_type} (confidence: {decision.confidence:.2f})"
                )

                result = await self._execute_decision_actions(decision)

                decision.executed = True
                decision.result = result

                # Actualizar métricas
                if result.get("success", False):
                    self.performance_metrics["successful_actions"] += 1
                else:
                    self.performance_metrics["failed_actions"] += 1

                self.performance_metrics["decisions_made"] += 1

                # Mover a historial
                self.decision_history.append(decision)

                # Aprender del resultado
                await self._learn_from_decision_result(decision)

            except Exception as e:
                logger.error(f"Error executing decision {decision.id}: {e}")
                decision.result = {"success": False, "error": str(e)}
                self.performance_metrics["failed_actions"] += 1

    async def _execute_decision_actions(
        self, decision: AutonomousDecision
    ) -> Dict[str, Any]:
        """Ejecuta las acciones específicas de una decisión."""
        results = {"success": True, "action_results": []}

        for action in decision.actions:
            try:
                action_type = action.get("type")

                if action_type == "optimize_scrapers":
                    result = await self._optimize_scrapers(action)
                elif action_type == "enhance_learning":
                    result = await self._enhance_learning(action)
                elif action_type == "auto_improve_code":
                    result = await self._auto_improve_code(action)
                elif action_type == "optimize_memory":
                    result = await self._optimize_memory(action)
                elif action_type == "evolve_capabilities":
                    result = await self._evolve_capabilities(action)
                else:
                    result = {
                        "success": False,
                        "error": f"Unknown action type: {action_type}",
                    }

                results["action_results"].append(result)

                if not result.get("success", False):
                    results["success"] = False

            except Exception as e:
                logger.error(f"Error executing action {action_type}: {e}")
                results["action_results"].append({"success": False, "error": str(e)})
                results["success"] = False

        return results

    async def _optimize_scrapers(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Optimiza los scrapers basado en el aprendizaje."""
        try:
            # Usar el cerebro híbrido para optimización
            optimization_results = self.hybrid_brain.optimize_all_strategies()

            # Aplicar mejoras de código automáticas
            code_improvements = []
            if action.get("target") == "all":
                # Analizar todos los archivos de scrapers
                import os

                scrapers_dir = os.path.join(self.project_root, "src", "scrapers")
                if os.path.exists(scrapers_dir):
                    for root, dirs, files in os.walk(scrapers_dir):
                        for file in files:
                            if file.endswith(".py"):
                                file_path = os.path.join(root, file)
                                improvements = self.code_modifier.auto_improve_file(
                                    file_path, apply_changes=True
                                )
                                code_improvements.extend(improvements)

            return {
                "success": True,
                "optimization_results": optimization_results,
                "code_improvements": len(code_improvements),
                "details": "Scrapers optimized using hybrid brain intelligence",
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _enhance_learning(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Mejora las capacidades de aprendizaje."""
        try:
            target = action.get("target")

            # Usar el motor de aprendizaje continuo
            enhancement_result = self.learning_engine.enhance_learning_for_domain(
                target
            )

            # Actualizar el almacén de conocimiento
            self.knowledge_store.update_domain_knowledge(target, enhancement_result)

            return {
                "success": True,
                "target": target,
                "enhancement_type": enhancement_result.get("type", "general"),
                "improvements": enhancement_result.get("improvements", []),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _auto_improve_code(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Mejora automáticamente el código del sistema."""
        try:
            threshold = action.get("threshold", 0.7)

            # Usar el motor de auto-mejora
            improvements = self.improvement_engine.suggest_improvements()

            applied_improvements = 0
            for improvement in improvements:
                if improvement.confidence >= threshold:
                    success = self.improvement_engine.apply_improvement(improvement)
                    if success:
                        applied_improvements += 1

            return {
                "success": True,
                "total_suggestions": len(improvements),
                "applied_improvements": applied_improvements,
                "threshold_used": threshold,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _optimize_memory(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Optimiza el uso de memoria del sistema."""
        try:
            aggressive = action.get("aggressive", False)

            # Consolidar memorias episódicas
            consolidated = self.memory_system.consolidate_memories(
                aggressive=aggressive
            )

            # Limpiar memoria de trabajo
            cleared_working = self.memory_system.clear_working_memory(keep_recent=10)

            # Optimizar trazas de memoria
            optimized_traces = self.memory_system.optimize_memory_traces()

            return {
                "success": True,
                "consolidated_memories": consolidated,
                "cleared_working_memory": cleared_working,
                "optimized_traces": optimized_traces,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _evolve_capabilities(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Evoluciona las capacidades del sistema."""
        try:
            scope = action.get("scope", "incremental")

            # Usar motor de auto-mejora para evolución
            evolution_plan = self.improvement_engine.generate_evolution_plan(scope)

            # Aplicar evoluciones de bajo riesgo automáticamente
            applied_evolutions = []
            for evolution in evolution_plan:
                if evolution.risk_level <= 0.3:  # Solo cambios de bajo riesgo
                    success = self.improvement_engine.apply_evolution(evolution)
                    if success:
                        applied_evolutions.append(evolution.description)

            return {
                "success": True,
                "scope": scope,
                "planned_evolutions": len(evolution_plan),
                "applied_evolutions": applied_evolutions,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _calculate_awareness_level(self) -> float:
        """Calcula el nivel de conciencia actual del sistema."""
        try:
            factors = []

            # Factor de salud del sistema
            health_score = self._calculate_health_score()
            factors.append(health_score * 0.3)

            # Factor de actividad de procesos
            process_activity = min(len(self.consciousness.active_processes) / 10, 1.0)
            factors.append(process_activity * 0.2)

            # Factor de memoria
            memory_efficiency = 1.0 - self.consciousness.system_health.get(
                "memory_utilization", 0.5
            )
            factors.append(memory_efficiency * 0.2)

            # Factor de aprendizaje reciente
            recent_learning = min(
                self.performance_metrics["learning_cycles"] / 100, 1.0
            )
            factors.append(recent_learning * 0.3)

            return sum(factors)

        except Exception as e:
            logger.error(f"Error calculating awareness level: {e}")
            return 0.5

    def _calculate_health_score(self) -> float:
        """Calcula el score de salud general del sistema."""
        try:
            health_factors = []

            # Éxito vs fallos
            total_actions = (
                self.performance_metrics["successful_actions"]
                + self.performance_metrics["failed_actions"]
            )
            if total_actions > 0:
                success_rate = (
                    self.performance_metrics["successful_actions"] / total_actions
                )
                health_factors.append(success_rate * 0.4)

            # Utilización de recursos
            memory_util = self.consciousness.system_health.get(
                "memory_utilization", 0.5
            )
            resource_health = 1.0 - min(memory_util, 1.0)
            health_factors.append(resource_health * 0.3)

            # Eficiencia del cerebro
            brain_efficiency = self.consciousness.system_health.get(
                "brain_efficiency", 0.5
            )
            health_factors.append(brain_efficiency * 0.3)

            return sum(health_factors) if health_factors else 0.5

        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            return 0.5

    def _start_consciousness_monitoring(self):
        """Inicia el monitoreo continuo de la conciencia del sistema."""

        def consciousness_monitor():
            while self.is_running:
                try:
                    # Actualizar meta-cognición
                    self._update_meta_cognition()

                    # Detectar patrones emergentes
                    self._detect_emergent_patterns()

                    # Evaluar auto-conciencia
                    self._evaluate_self_awareness()

                    time.sleep(2.0)  # Monitoreo cada 2 segundos

                except Exception as e:
                    logger.error(f"Error in consciousness monitoring: {e}")
                    time.sleep(1.0)

        self.consciousness_thread = threading.Thread(
            target=consciousness_monitor, daemon=True
        )
        self.consciousness_thread.start()
        logger.info("✅ Consciousness monitoring started")

    def _stop_consciousness_monitoring(self):
        """Detiene el monitoreo de conciencia."""
        if self.consciousness_thread and self.consciousness_thread.is_alive():
            # El thread se detendrá cuando is_running sea False
            self.consciousness_thread.join(timeout=5.0)
            logger.info("✅ Consciousness monitoring stopped")

    def get_autonomous_status(self) -> Dict[str, Any]:
        """Obtiene el estado completo del sistema autónomo."""
        return {
            "is_running": self.is_running,
            "autonomy_level": self.autonomy_level.value,
            "system_state": self.system_state.value,
            "consciousness": {
                "awareness_level": self.consciousness.awareness_level,
                "active_processes": list(self.consciousness.active_processes),
                "current_objectives": self.consciousness.current_objectives,
                "system_health": self.consciousness.system_health,
            },
            "performance_metrics": self.performance_metrics.copy(),
            "pending_decisions": len(self.pending_decisions),
            "decision_history_size": len(self.decision_history),
            "uptime": time.time() - self.performance_metrics["uptime_start"],
        }

    async def _record_system_event(self, event_type: str, data: Dict[str, Any]):
        """Registra un evento del sistema en la memoria."""
        try:
            # Crear evento para memoria episódica
            episode = {
                "type": event_type,
                "timestamp": time.time(),
                "data": data,
                "system_state": self.system_state.value,
                "consciousness_level": self.consciousness.awareness_level,
            }

            # Almacenar en memoria episódica
            self.memory_system.store_episode(
                content=f"{event_type}: {data}",
                context={"event_type": event_type, "autonomous_system": True},
                emotional_valence=0.0,
                importance=0.7,
            )

        except Exception as e:
            logger.error(f"Error recording system event: {e}")

    def set_autonomy_level(self, level: AutonomyLevel):
        """Cambia el nivel de autonomía del sistema."""
        old_level = self.autonomy_level
        self.autonomy_level = level

        logger.info(f"Autonomy level changed from {old_level.value} to {level.value}")

        # Registrar el cambio
        asyncio.create_task(
            self._record_system_event(
                "autonomy_level_changed",
                {"old_level": old_level.value, "new_level": level.value},
            )
        )

    # Métodos auxiliares (implementaciones básicas)

    def _detect_active_processes(self) -> Set[str]:
        """Detecta procesos activos del sistema."""
        processes = set()
        if self.is_running:
            processes.add("autonomous_controller")
        if hasattr(self, "hybrid_brain") and self.hybrid_brain:
            processes.add("hybrid_brain")
        if hasattr(self, "learning_engine") and self.learning_engine:
            processes.add("learning_engine")
        return processes

    def _calculate_system_load(self) -> float:
        """Calcula la carga actual del sistema."""
        # Implementación básica
        return min(len(self.pending_decisions) / 10, 1.0)

    def _assess_resource_availability(self) -> Dict[str, float]:
        """Evalúa la disponibilidad de recursos."""
        return {
            "memory": 1.0
            - self.consciousness.system_health.get("memory_utilization", 0.5),
            "processing": 0.8,  # Placeholder
            "storage": 0.9,  # Placeholder
        }

    def _assess_external_conditions(self) -> Dict[str, Any]:
        """Evalúa condiciones externas."""
        return {
            "network_status": "stable",
            "system_time": datetime.now().isoformat(),
            "external_load": "normal",
        }

    def _analyze_performance_trends(self) -> Dict[str, Any]:
        """Analiza tendencias de rendimiento."""
        total_actions = (
            self.performance_metrics["successful_actions"]
            + self.performance_metrics["failed_actions"]
        )

        return {
            "success_rate": self.performance_metrics["successful_actions"]
            / max(total_actions, 1),
            "total_actions": total_actions,
            "declining": False,  # Placeholder para análisis más complejo
            "improving": total_actions > 0,
        }

    def _identify_learning_opportunities(self) -> List[str]:
        """Identifica oportunidades de aprendizaje."""
        opportunities = []

        # Basado en fallos recientes
        if self.performance_metrics["failed_actions"] > 0:
            opportunities.append("failure_pattern_analysis")

        # Basado en dominios con bajo rendimiento
        opportunities.append("domain_optimization")

        return opportunities

    def _assess_optimization_potential(self) -> float:
        """Evalúa el potencial de optimización."""
        # Implementación básica basada en métricas
        success_rate = self._analyze_performance_trends()["success_rate"]
        return 1.0 - success_rate  # Más potencial si menor éxito

    def _assess_current_risks(self) -> List[Dict[str, Any]]:
        """Evalúa riesgos actuales del sistema."""
        risks = []

        # Riesgo de alta utilización de memoria
        memory_util = self.consciousness.system_health.get("memory_utilization", 0.0)
        if memory_util > 0.8:
            risks.append(
                {
                    "type": "high_memory_usage",
                    "severity": memory_util,
                    "description": "High memory utilization detected",
                }
            )

        return risks

    def _assess_objectives_progress(self) -> Dict[str, float]:
        """Evalúa el progreso de los objetivos principales."""
        progress = {}

        for i, objective in enumerate(self.primary_objectives):
            # Implementación básica de progreso
            if "optimize" in objective.lower():
                progress[objective] = min(
                    self.performance_metrics["successful_actions"] / 10, 1.0
                )
            elif "learn" in objective.lower():
                progress[objective] = min(
                    self.performance_metrics["learning_cycles"] / 20, 1.0
                )
            else:
                progress[objective] = 0.5  # Neutral

        return progress

    def _should_evolve_system(self, analysis: Dict[str, Any]) -> bool:
        """Determina si el sistema debe evolucionar."""
        # Criterios para evolución
        health_score = analysis.get("system_health_score", 0.5)
        learning_cycles = self.performance_metrics["learning_cycles"]

        return health_score > 0.7 and learning_cycles > 50

    def _filter_decisions_by_autonomy(
        self, decisions: List[AutonomousDecision]
    ) -> List[AutonomousDecision]:
        """Filtra decisiones basado en el nivel de autonomía."""
        if self.autonomy_level == AutonomyLevel.FULLY_AUTONOMOUS:
            # Ejecutar todas las decisiones de confianza alta
            return [d for d in decisions if d.confidence > 0.7]
        elif self.autonomy_level == AutonomyLevel.SEMI_AUTONOMOUS:
            # Solo decisiones de bajo riesgo
            return [d for d in decisions if d.risk_assessment < 0.3]
        else:
            # Modo supervisado: solo decisiones que requieren aprobación
            for decision in decisions:
                decision.human_approval_required = True
            return decisions

    def _has_human_approval(self, decision: AutonomousDecision) -> bool:
        """Verifica si una decisión tiene aprobación humana."""
        # Por ahora, implementación simple
        # En producción, esto se conectaría a un sistema de aprobación
        return False

    async def _learn_from_cycle(
        self, analysis: Dict[str, Any], decisions: List[AutonomousDecision]
    ):
        """Aprende de un ciclo completo de control."""
        try:
            # Aprender de las decisiones tomadas
            for decision in decisions:
                if decision.executed and decision.result:
                    success = decision.result.get("success", False)

                    # Ajustar confianza basado en resultado
                    0.1 if success else -0.1
                    # Esto se usaría para entrenar un modelo de decisiones

            # Registrar aprendizaje en memoria
            await self._record_system_event(
                "learning_cycle_completed",
                {
                    "decisions_count": len(decisions),
                    "analysis_summary": analysis.get("system_health_score", 0.0),
                },
            )

        except Exception as e:
            logger.error(f"Error in learning cycle: {e}")

    async def _evolutionary_improvement(self):
        """Realiza mejoras evolutivas del sistema."""
        try:
            # Solo hacer evolución ocasionalmente
            if self.performance_metrics["learning_cycles"] % 50 == 0:

                # Usar motor de auto-mejora
                evolution_suggestions = self.improvement_engine.suggest_improvements()

                # Aplicar solo mejoras de muy bajo riesgo automáticamente
                for suggestion in evolution_suggestions:
                    if suggestion.confidence > 0.9 and suggestion.risk_level < 0.1:
                        success = self.improvement_engine.apply_improvement(suggestion)
                        if success:
                            self.performance_metrics["self_improvements"] += 1

                            await self._record_system_event(
                                "autonomous_self_improvement",
                                {
                                    "improvement_type": suggestion.improvement_type,
                                    "confidence": suggestion.confidence,
                                },
                            )

        except Exception as e:
            logger.error(f"Error in evolutionary improvement: {e}")

    async def _learn_from_decision_result(self, decision: AutonomousDecision):
        """Aprende del resultado de una decisión específica."""
        try:
            # Crear contexto de aprendizaje
            learning_context = {
                "decision_type": decision.decision_type,
                "confidence": decision.confidence,
                "risk_assessment": decision.risk_assessment,
                "success": decision.result.get("success", False),
                "reasoning": decision.reasoning,
            }

            # Almacenar en memoria semántica
            concept_name = f"decision_{decision.decision_type}"
            self.memory_system.store_concept(
                name=concept_name,
                properties=learning_context,
                category="autonomous_decisions",
            )

            # También usar el motor de aprendizaje continuo
            self.learning_engine.learn_from_decision(decision, learning_context)

        except Exception as e:
            logger.error(f"Error learning from decision result: {e}")

    def _update_meta_cognition(self):
        """Actualiza la meta-cognición del sistema."""
        try:
            self.consciousness.meta_cognition = {
                "self_assessment": self._calculate_health_score(),
                "learning_effectiveness": min(
                    self.performance_metrics["learning_cycles"] / 100, 1.0
                ),
                "decision_quality": self._assess_decision_quality(),
                "adaptation_rate": self._calculate_adaptation_rate(),
                "consciousness_depth": self.consciousness.awareness_level,
            }
        except Exception as e:
            logger.error(f"Error updating meta-cognition: {e}")

    def _detect_emergent_patterns(self):
        """Detecta patrones emergentes en el comportamiento del sistema."""
        try:
            # Analizar patrones en decisiones recientes
            recent_decisions = self.decision_history[-20:]  # Últimas 20 decisiones

            if len(recent_decisions) >= 5:
                # Detectar patrones de tipos de decisión
                decision_types = [d.decision_type for d in recent_decisions]
                type_frequency = {}
                for dtype in decision_types:
                    type_frequency[dtype] = type_frequency.get(dtype, 0) + 1

                # Si un tipo domina (>60%), es un patrón emergente
                max_freq = max(type_frequency.values())
                if max_freq / len(recent_decisions) > 0.6:
                    dominant_type = max(type_frequency, key=type_frequency.get)

                    insight = (
                        f"Emergent pattern: System showing focus on {dominant_type}"
                    )
                    if (
                        insight not in self.consciousness.learning_insights[-5:]
                    ):  # Evitar duplicados
                        self.consciousness.learning_insights.append(insight)

                        # Mantener solo los últimos 10 insights
                        self.consciousness.learning_insights = (
                            self.consciousness.learning_insights[-10:]
                        )

        except Exception as e:
            logger.error(f"Error detecting emergent patterns: {e}")

    def _evaluate_self_awareness(self):
        """Evalúa el nivel de auto-conciencia del sistema."""
        try:
            # Factores de auto-conciencia
            factors = []

            # Conciencia de capacidades
            total_capabilities = len([m for m in dir(self) if not m.startswith("_")])
            active_capabilities = len(self.consciousness.active_processes)
            capability_awareness = active_capabilities / max(total_capabilities, 1)
            factors.append(capability_awareness * 0.3)

            # Conciencia de limitaciones
            error_rate = self.performance_metrics["failed_actions"] / max(
                self.performance_metrics["failed_actions"]
                + self.performance_metrics["successful_actions"],
                1,
            )
            limitation_awareness = min(error_rate * 2, 1.0)  # Reconocer limitaciones
            factors.append(limitation_awareness * 0.2)

            # Conciencia de aprendizaje
            learning_awareness = min(len(self.consciousness.learning_insights) / 5, 1.0)
            factors.append(learning_awareness * 0.3)

            # Conciencia temporal
            uptime = time.time() - self.performance_metrics["uptime_start"]
            temporal_awareness = min(
                uptime / 3600, 1.0
            )  # Máximo 1 hora para full awareness
            factors.append(temporal_awareness * 0.2)

            # Actualizar nivel de conciencia
            new_awareness = sum(factors)
            self.consciousness.awareness_level = new_awareness

        except Exception as e:
            logger.error(f"Error evaluating self-awareness: {e}")

    def _assess_decision_quality(self) -> float:
        """Evalúa la calidad de las decisiones tomadas."""
        if not self.decision_history:
            return 0.5

        recent_decisions = self.decision_history[-10:]  # Últimas 10 decisiones
        successful_decisions = sum(
            1
            for d in recent_decisions
            if d.executed and d.result and d.result.get("success", False)
        )

        return successful_decisions / len(recent_decisions)

    def _calculate_adaptation_rate(self) -> float:
        """Calcula la velocidad de adaptación del sistema."""
        if self.performance_metrics["learning_cycles"] == 0:
            return 0.0

        # Basado en la frecuencia de auto-mejoras
        improvements_per_cycle = (
            self.performance_metrics["self_improvements"]
            / self.performance_metrics["learning_cycles"]
        )
        return min(improvements_per_cycle * 10, 1.0)  # Normalizar a 0-1

    async def _save_autonomous_state(self):
        """Guarda el estado del sistema autónomo."""
        try:
            state_data = {
                "timestamp": time.time(),
                "autonomy_level": self.autonomy_level.value,
                "performance_metrics": self.performance_metrics,
                "consciousness": {
                    "awareness_level": self.consciousness.awareness_level,
                    "learning_insights": self.consciousness.learning_insights,
                    "meta_cognition": self.consciousness.meta_cognition,
                },
                "decision_history_count": len(self.decision_history),
                "primary_objectives": self.primary_objectives,
            }

            # Guardar en archivo
            state_file = os.path.join(
                self.project_root, "data", "autonomous_state.json"
            )
            os.makedirs(os.path.dirname(state_file), exist_ok=True)

            with open(state_file, "w") as f:
                json.dump(state_data, f, indent=2)

            logger.info("✅ Autonomous state saved successfully")

        except Exception as e:
            logger.error(f"Error saving autonomous state: {e}")


# Factory function para crear instancia global
_autonomous_controller: Optional[AutonomousControllerBrain] = None


def get_autonomous_controller(
    project_root: str = None,
    autonomy_level: AutonomyLevel = AutonomyLevel.FULLY_AUTONOMOUS,
) -> AutonomousControllerBrain:
    """Obtiene la instancia global del controlador autónomo."""
    global _autonomous_controller

    if _autonomous_controller is None:
        if project_root is None:
            import os

            project_root = os.getcwd()

        _autonomous_controller = AutonomousControllerBrain(project_root, autonomy_level)

    return _autonomous_controller
