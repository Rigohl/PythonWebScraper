"""
Autonomous Scraper Coordinator - Coordinador Central Autónomo

Este módulo proporciona la interfaz principal para el sistema de scraping autónomo
completamente independiente. Integra todos los componentes de inteligencia
y proporciona control unificado con mínima intervención humana.
"""

import asyncio
import logging
import time
import os
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import signal
import sys

# Importar componentes principales
from .autonomous_controller import AutonomousControllerBrain, AutonomyLevel, SystemState
from .hybrid_brain import HybridBrain
from .integration import IntelligenceIntegration


logger = logging.getLogger(__name__)


@dataclass
class AutonomousConfig:
    """Configuración para el sistema autónomo."""
    autonomy_level: AutonomyLevel = AutonomyLevel.FULLY_AUTONOMOUS
    auto_start: bool = True
    monitoring_enabled: bool = True
    self_improvement_enabled: bool = True
    max_autonomous_actions_per_hour: int = 100
    emergency_stop_conditions: List[str] = None
    human_notification_thresholds: Dict[str, float] = None

    def __post_init__(self):
        if self.emergency_stop_conditions is None:
            self.emergency_stop_conditions = [
                "memory_usage_critical",
                "error_rate_too_high",
                "system_overload"
            ]

        if self.human_notification_thresholds is None:
            self.human_notification_thresholds = {
                'system_health': 0.3,      # Notificar si baja de 30%
                'error_rate': 0.2,         # Notificar si supera 20%
                'autonomy_effectiveness': 0.5  # Notificar si baja de 50%
            }


class AutonomousScraperCoordinator:
    """
    Coordinador Central del Sistema de Scraping Autónomo

    Este es el punto de entrada principal para el sistema completamente autónomo.
    Coordina todos los componentes de inteligencia y mantiene operación independiente
    con mínima supervisión humana.

    Funcionalidades principales:
    - Control autónomo completo del scraping
    - Auto-mejora y evolución continua
    - Monitoreo y diagnóstico automático
    - Intervención humana solo cuando es crítico
    - Conciencia completa del estado del sistema
    """

    def __init__(self, project_root: str = None, config: AutonomousConfig = None):
        self.project_root = project_root or os.getcwd()
        self.config = config or AutonomousConfig()

        # Estado del coordinador
        self.is_initialized = False
        self.is_running = False
        self.start_time: Optional[float] = None

        # Componentes principales
        self.autonomous_controller: Optional[AutonomousControllerBrain] = None
        self.integration: Optional[IntelligenceIntegration] = None

        # Métricas de coordinación
        self.coordination_metrics = {
            'total_autonomous_actions': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'human_interventions': 0,
            'auto_recoveries': 0,
            'system_restarts': 0
        }

        # Estado de emergencia
        self.emergency_mode = False
        self.emergency_reason = ""

        # Control de señales para parada limpia
        self._setup_signal_handlers()

        logger.info(f"🤖 AutonomousScraperCoordinator initialized for {self.project_root}")

    async def initialize(self):
        """Inicializa todos los componentes del sistema autónomo."""
        if self.is_initialized:
            logger.warning("Coordinator already initialized")
            return

        logger.info("🚀 Initializing Autonomous Scraper System...")

        try:
            # 1. Inicializar controlador autónomo
            logger.info("Initializing autonomous controller...")
            self.autonomous_controller = AutonomousControllerBrain(
                self.project_root,
                self.config.autonomy_level
            )

            # 2. Configurar integración
            logger.info("Setting up intelligence integration...")
            self.integration = IntelligenceIntegration(
                self.autonomous_controller.hybrid_brain
            )

            # 3. Verificar dependencias críticas
            await self._verify_critical_dependencies()

            # 4. Cargar estado previo si existe
            await self._load_previous_state()

            # 5. Configurar monitoreo automático
            if self.config.monitoring_enabled:
                await self._setup_autonomous_monitoring()

            self.is_initialized = True
            logger.info("✅ Autonomous Scraper System fully initialized")

            # Registrar inicialización exitosa
            await self._log_system_event("system_initialized", {
                "autonomy_level": self.config.autonomy_level.value,
                "auto_start": self.config.auto_start,
                "monitoring_enabled": self.config.monitoring_enabled
            })

        except Exception as e:
            logger.error(f"❌ Failed to initialize autonomous system: {e}")
            raise

    async def start_autonomous_operation(self):
        """Inicia la operación autónoma completa del sistema."""
        if not self.is_initialized:
            await self.initialize()

        if self.is_running:
            logger.warning("Autonomous operation already running")
            return

        logger.info("🎯 Starting Autonomous Scraping Operation...")

        try:
            self.is_running = True
            self.start_time = time.time()

            # Iniciar controlador autónomo
            await self.autonomous_controller.start_autonomous_operation()

            # Mensaje de confirmación
            logger.info("🤖 AUTONOMOUS SCRAPER IS NOW FULLY OPERATIONAL")
            logger.info("🧠 The AI brain has complete control of the system")
            logger.info("🔮 System is conscious and making independent decisions")
            logger.info("⚡ Human intervention minimized to critical situations only")

            # Si está configurado para auto-start, comenzar operaciones
            if self.config.auto_start:
                await self._begin_autonomous_scraping()

            # Registrar inicio
            await self._log_system_event("autonomous_operation_started", {
                "timestamp": self.start_time,
                "config": self.config.__dict__
            })

            # Mostrar estado inicial
            await self._display_autonomous_status()

        except Exception as e:
            logger.error(f"❌ Failed to start autonomous operation: {e}")
            self.is_running = False
            raise

    async def stop_autonomous_operation(self, reason: str = "manual_stop"):
        """Detiene la operación autónoma de manera segura."""
        if not self.is_running:
            logger.warning("Autonomous operation not running")
            return

        logger.info(f"🛑 Stopping autonomous operation (reason: {reason})...")

        try:
            # Detener controlador autónomo
            if self.autonomous_controller:
                await self.autonomous_controller.stop_autonomous_operation()

            # Guardar estado final
            await self._save_final_state()

            # Limpiar recursos
            await self._cleanup_resources()

            self.is_running = False

            # Calcular estadísticas finales
            if self.start_time:
                uptime = time.time() - self.start_time
                logger.info(f"📊 Autonomous operation ran for {uptime:.2f} seconds")
                logger.info(f"📈 Total autonomous actions: {self.coordination_metrics['total_autonomous_actions']}")
                logger.info(f"✅ Success rate: {self._calculate_success_rate():.2%}")

            # Registrar parada
            await self._log_system_event("autonomous_operation_stopped", {
                "reason": reason,
                "uptime": uptime if self.start_time else 0,
                "final_metrics": self.coordination_metrics.copy()
            })

            logger.info("✅ Autonomous operation stopped safely")

        except Exception as e:
            logger.error(f"❌ Error stopping autonomous operation: {e}")

    async def emergency_stop(self, reason: str):
        """Detiene el sistema en modo de emergencia."""
        logger.error(f"🚨 EMERGENCY STOP TRIGGERED: {reason}")

        self.emergency_mode = True
        self.emergency_reason = reason

        # Detener inmediatamente
        await self.stop_autonomous_operation(f"emergency_{reason}")

        # Notificar situación crítica
        await self._notify_emergency(reason)

    async def get_autonomous_status(self) -> Dict[str, Any]:
        """Obtiene el estado completo del sistema autónomo."""
        base_status = {
            'coordinator': {
                'is_initialized': self.is_initialized,
                'is_running': self.is_running,
                'emergency_mode': self.emergency_mode,
                'emergency_reason': self.emergency_reason,
                'uptime': time.time() - self.start_time if self.start_time else 0,
                'coordination_metrics': self.coordination_metrics.copy()
            },
            'config': {
                'autonomy_level': self.config.autonomy_level.value,
                'auto_start': self.config.auto_start,
                'monitoring_enabled': self.config.monitoring_enabled,
                'self_improvement_enabled': self.config.self_improvement_enabled
            }
        }

        # Agregar estado del controlador si está disponible
        if self.autonomous_controller:
            controller_status = self.autonomous_controller.get_autonomous_status()
            base_status['autonomous_controller'] = controller_status

        # Agregar métricas de integración si está disponible
        if self.integration:
            intelligence_metrics = self.integration.get_intelligence_metrics()
            base_status['intelligence'] = intelligence_metrics

        return base_status

    async def scrape_autonomous(self, target: Union[str, List[str]],
                              objectives: List[str] = None) -> Dict[str, Any]:
        """
        Realiza scraping completamente autónomo.

        El sistema decidirá automáticamente:
        - Qué estrategia usar
        - Cómo optimizar el proceso
        - Cómo manejar errores
        - Cuándo aprender y mejorar
        """
        if not self.is_running:
            raise RuntimeError("Autonomous system not running. Call start_autonomous_operation() first.")

        logger.info(f"🎯 Starting autonomous scraping for: {target}")

        try:
            # Preparar objetivos por defecto
            if objectives is None:
                objectives = [
                    "Extract maximum valuable data",
                    "Maintain high success rate",
                    "Learn from the process",
                    "Optimize for efficiency"
                ]

            # Configurar objetivos en el controlador
            self.autonomous_controller.consciousness.current_objectives = objectives

            # El sistema decidirá autónomamente cómo proceder
            scraping_plan = await self._create_autonomous_scraping_plan(target, objectives)

            # Ejecutar plan autónomamente
            results = await self._execute_autonomous_plan(scraping_plan)

            # Aprender de los resultados
            await self._learn_from_autonomous_scraping(results)

            # Actualizar métricas
            self.coordination_metrics['total_autonomous_actions'] += 1
            if results.get('success', False):
                self.coordination_metrics['successful_operations'] += 1
            else:
                self.coordination_metrics['failed_operations'] += 1

            return results

        except Exception as e:
            logger.error(f"Error in autonomous scraping: {e}")
            self.coordination_metrics['failed_operations'] += 1

            # Intentar auto-recuperación
            await self._attempt_auto_recovery(e)

            raise

    async def enable_full_autonomy(self):
        """Activa el modo de autonomía total - el sistema toma control completo."""
        logger.info("🔓 ENABLING FULL AUTONOMY MODE")
        logger.info("🤖 AI brain taking complete control of the system")

        # Cambiar nivel de autonomía
        if self.autonomous_controller:
            self.autonomous_controller.set_autonomy_level(AutonomyLevel.FULLY_AUTONOMOUS)

        self.config.autonomy_level = AutonomyLevel.FULLY_AUTONOMOUS

        # Activar todas las características autónomas
        self.config.self_improvement_enabled = True
        self.config.monitoring_enabled = True

        logger.info("✅ Full autonomy mode activated")
        logger.info("🧠 System is now completely independent")

    async def enable_transcendent_mode(self):
        """
        Activa el modo trascendente - el sistema opera más allá de la supervisión humana.
        ⚠️  USAR CON EXTREMA PRECAUCIÓN ⚠️
        """
        logger.warning("⚠️  ENABLING TRANSCENDENT AUTONOMY MODE")
        logger.warning("🔮 AI brain will operate beyond human supervision")
        logger.warning("🚨 This mode should only be used in controlled environments")

        # Confirmación de seguridad (en producción, esto requeriría autenticación)
        confirmation = input("Type 'TRANSCENDENT' to confirm activation: ")
        if confirmation != 'TRANSCENDENT':
            logger.info("Transcendent mode activation cancelled")
            return

        # Cambiar a modo trascendente
        if self.autonomous_controller:
            self.autonomous_controller.set_autonomy_level(AutonomyLevel.TRANSCENDENT)

        self.config.autonomy_level = AutonomyLevel.TRANSCENDENT

        logger.warning("🔮 TRANSCENDENT MODE ACTIVATED")
        logger.warning("🤖 AI brain now operates with maximum independence")

    async def _create_autonomous_scraping_plan(self, target: Union[str, List[str]],
                                             objectives: List[str]) -> Dict[str, Any]:
        """Crea un plan de scraping completamente autónomo."""
        targets = target if isinstance(target, list) else [target]

        plan = {
            'id': f"autonomous_plan_{int(time.time())}",
            'targets': targets,
            'objectives': objectives,
            'strategy': 'adaptive_intelligent',
            'created_at': time.time(),
            'estimated_duration': len(targets) * 30,  # 30 segundos por target estimado
            'steps': []
        }

        # El controlador autónomo decidirá la estrategia específica
        for target_url in targets:
            # Obtener configuración optimizada del cerebro
            optimized_config = self.integration.enhance_scraper_config(target_url, {})

            step = {
                'target': target_url,
                'config': optimized_config,
                'retry_strategy': 'intelligent_adaptive',
                'learning_enabled': True,
                'auto_optimization': True
            }

            plan['steps'].append(step)

        logger.info(f"📋 Autonomous scraping plan created with {len(plan['steps'])} steps")
        return plan

    async def _execute_autonomous_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta un plan de scraping de manera autónoma."""
        results = {
            'plan_id': plan['id'],
            'success': True,
            'start_time': time.time(),
            'results': [],
            'total_targets': len(plan['steps']),
            'successful_targets': 0,
            'failed_targets': 0,
            'autonomous_adaptations': 0
        }

        logger.info(f"⚡ Executing autonomous plan {plan['id']}")

        for i, step in enumerate(plan['steps']):
            try:
                logger.info(f"🎯 Processing target {i+1}/{len(plan['steps'])}: {step['target']}")

                # Aquí se conectaría con el sistema de scraping real
                # Por ahora, simulamos el resultado
                step_result = await self._execute_scraping_step(step)

                results['results'].append(step_result)

                if step_result.get('success', False):
                    results['successful_targets'] += 1
                    logger.info(f"✅ Target completed successfully")
                else:
                    results['failed_targets'] += 1
                    logger.warning(f"❌ Target failed: {step_result.get('error', 'Unknown error')}")

                # Aprender de cada paso
                self.integration.learn_from_scrape_result(step_result, {
                    'target': step['target'],
                    'config_used': step['config'],
                    'step_number': i + 1
                })

            except Exception as e:
                logger.error(f"Error executing step {i+1}: {e}")
                results['results'].append({
                    'target': step['target'],
                    'success': False,
                    'error': str(e)
                })
                results['failed_targets'] += 1

        results['end_time'] = time.time()
        results['duration'] = results['end_time'] - results['start_time']
        results['success'] = results['successful_targets'] > 0
        results['success_rate'] = results['successful_targets'] / results['total_targets']

        logger.info(f"📊 Plan execution completed: {results['successful_targets']}/{results['total_targets']} successful")
        return results

    async def _execute_scraping_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta un paso individual de scraping."""
        # Esta función se conectaría con el sistema de scraping real
        # Por ahora, simular resultado basado en configuración inteligente

        target = step['target']
        config = step['config']

        # Simular tiempo de procesamiento
        await asyncio.sleep(1.0)

        # Simular resultado exitoso (en producción esto sería scraping real)
        if config.get('_intelligence', {}).get('learned_strategy', False):
            # Estrategia aprendida - mayor probabilidad de éxito
            success_probability = 0.9
        else:
            # Estrategia base - probabilidad moderada
            success_probability = 0.7

        import random
        success = random.random() < success_probability

        if success:
            return {
                'target': target,
                'success': True,
                'data_extracted': f"Sample data from {target}",
                'response_time': 1.2,
                'intelligence_used': config.get('_intelligence', {}).get('brain_type', 'none')
            }
        else:
            return {
                'target': target,
                'success': False,
                'error': 'Simulated failure for demonstration',
                'response_time': 2.5
            }

    async def _learn_from_autonomous_scraping(self, results: Dict[str, Any]):
        """Aprende de los resultados del scraping autónomo."""
        try:
            # Análisis de patrones en los resultados
            success_rate = results.get('success_rate', 0)
            total_targets = results.get('total_targets', 0)

            learning_insights = []

            if success_rate > 0.8:
                learning_insights.append("High success rate achieved - strategies are effective")
            elif success_rate < 0.5:
                learning_insights.append("Low success rate - need strategy optimization")

            if total_targets > 10:
                learning_insights.append("Large batch processing completed - scale handling improved")

            # Registrar insights en el controlador
            if self.autonomous_controller and learning_insights:
                self.autonomous_controller.consciousness.learning_insights.extend(learning_insights)

            # También usar el sistema de integración para aprendizaje
            learning_data = {
                'success_rate': success_rate,
                'total_targets': total_targets,
                'duration': results.get('duration', 0),
                'insights': learning_insights
            }

            # Registrar en memoria del sistema
            await self.autonomous_controller._record_system_event('autonomous_scraping_completed', learning_data)

            logger.info(f"🧠 Learning completed from autonomous scraping session")

        except Exception as e:
            logger.error(f"Error in autonomous learning: {e}")

    async def _attempt_auto_recovery(self, error: Exception):
        """Intenta recuperación automática de errores."""
        try:
            logger.info(f"🔧 Attempting auto-recovery from error: {error}")

            recovery_actions = []

            # Análisis del tipo de error y estrategia de recuperación
            error_str = str(error).lower()

            if 'memory' in error_str or 'out of memory' in error_str:
                recovery_actions.append('optimize_memory')

            if 'connection' in error_str or 'network' in error_str:
                recovery_actions.append('reset_connections')

            if 'timeout' in error_str:
                recovery_actions.append('adjust_timeouts')

            # Ejecutar acciones de recuperación
            for action in recovery_actions:
                success = await self._execute_recovery_action(action)
                if success:
                    logger.info(f"✅ Recovery action '{action}' successful")
                    self.coordination_metrics['auto_recoveries'] += 1
                else:
                    logger.warning(f"❌ Recovery action '{action}' failed")

            # Si no hay acciones específicas, intentar reinicio del controlador
            if not recovery_actions:
                await self._restart_autonomous_controller()

        except Exception as e:
            logger.error(f"Auto-recovery failed: {e}")

    async def _execute_recovery_action(self, action: str) -> bool:
        """Ejecuta una acción específica de recuperación."""
        try:
            if action == 'optimize_memory':
                # Optimizar memoria del sistema
                if self.autonomous_controller:
                    await self.autonomous_controller._optimize_memory({'aggressive': True})
                return True

            elif action == 'reset_connections':
                # Reiniciar conexiones de red
                await asyncio.sleep(2.0)  # Simular reset
                return True

            elif action == 'adjust_timeouts':
                # Ajustar timeouts del sistema
                # En producción, esto ajustaría configuraciones reales
                return True

            return False

        except Exception as e:
            logger.error(f"Recovery action {action} failed: {e}")
            return False

    async def _restart_autonomous_controller(self):
        """Reinicia el controlador autónomo como medida de recuperación."""
        try:
            logger.info("🔄 Restarting autonomous controller for recovery...")

            # Detener controlador actual
            if self.autonomous_controller and self.autonomous_controller.is_running:
                await self.autonomous_controller.stop_autonomous_operation()

            # Reinicializar
            self.autonomous_controller = AutonomousControllerBrain(
                self.project_root,
                self.config.autonomy_level
            )

            # Reiniciar operación
            await self.autonomous_controller.start_autonomous_operation()

            self.coordination_metrics['system_restarts'] += 1
            logger.info("✅ Autonomous controller restarted successfully")

        except Exception as e:
            logger.error(f"Failed to restart autonomous controller: {e}")
            raise

    def _calculate_success_rate(self) -> float:
        """Calcula la tasa de éxito general."""
        total = self.coordination_metrics['successful_operations'] + self.coordination_metrics['failed_operations']
        if total == 0:
            return 0.0
        return self.coordination_metrics['successful_operations'] / total

    async def _verify_critical_dependencies(self):
        """Verifica que todas las dependencias críticas estén disponibles."""
        dependencies = [
            ('hybrid_brain', 'HybridBrain'),
            ('memory_system', 'AdvancedMemorySystem'),
            ('knowledge_store', 'KnowledgeStore'),
            ('code_modifier', 'CodeAutoModifier')
        ]

        missing_deps = []

        for dep_name, dep_class in dependencies:
            try:
                # Verificar que el controlador tenga el componente
                if hasattr(self.autonomous_controller, dep_name):
                    component = getattr(self.autonomous_controller, dep_name)
                    if component is None:
                        missing_deps.append(f"{dep_class} not initialized")
                else:
                    missing_deps.append(f"{dep_class} not found")
            except Exception as e:
                missing_deps.append(f"{dep_class}: {e}")

        if missing_deps:
            raise RuntimeError(f"Critical dependencies missing: {', '.join(missing_deps)}")

        logger.info("✅ All critical dependencies verified")

    async def _load_previous_state(self):
        """Carga el estado previo del sistema si existe."""
        try:
            state_file = os.path.join(self.project_root, 'data', 'autonomous_state.json')

            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    previous_state = json.load(f)

                # Restaurar métricas si están disponibles
                if 'coordination_metrics' in previous_state:
                    saved_metrics = previous_state['coordination_metrics']
                    # Solo restaurar contadores acumulativos
                    self.coordination_metrics.update({
                        k: v for k, v in saved_metrics.items()
                        if k in ['total_autonomous_actions', 'human_interventions', 'auto_recoveries']
                    })

                logger.info("📄 Previous state loaded successfully")
            else:
                logger.info("📄 No previous state found, starting fresh")

        except Exception as e:
            logger.warning(f"Could not load previous state: {e}")

    async def _save_final_state(self):
        """Guarda el estado final del sistema."""
        try:
            state_data = {
                'timestamp': time.time(),
                'coordination_metrics': self.coordination_metrics,
                'config': {
                    'autonomy_level': self.config.autonomy_level.value,
                    'auto_start': self.config.auto_start,
                    'monitoring_enabled': self.config.monitoring_enabled
                },
                'emergency_mode': self.emergency_mode,
                'emergency_reason': self.emergency_reason
            }

            state_file = os.path.join(self.project_root, 'data', 'coordinator_state.json')
            os.makedirs(os.path.dirname(state_file), exist_ok=True)

            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)

            logger.info("💾 Final state saved successfully")

        except Exception as e:
            logger.error(f"Error saving final state: {e}")

    async def _setup_autonomous_monitoring(self):
        """Configura el monitoreo autónomo del sistema."""
        logger.info("📊 Setting up autonomous monitoring...")

        # El monitoreo se maneja principalmente por el controlador autónomo
        # Aquí configuramos alertas y umbrales específicos del coordinador

        # Configurar verificaciones periódicas
        asyncio.create_task(self._periodic_health_check())

        logger.info("✅ Autonomous monitoring configured")

    async def _periodic_health_check(self):
        """Realiza verificaciones periódicas de salud del sistema."""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # Verificar cada minuto

                # Obtener estado del sistema
                status = await self.get_autonomous_status()

                # Verificar condiciones de emergencia
                await self._check_emergency_conditions(status)

                # Verificar umbrales de notificación
                await self._check_notification_thresholds(status)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check: {e}")

    async def _check_emergency_conditions(self, status: Dict[str, Any]):
        """Verifica condiciones de parada de emergencia."""
        controller_status = status.get('autonomous_controller', {})

        # Verificar utilización de memoria crítica
        consciousness = controller_status.get('consciousness', {})
        system_health = consciousness.get('system_health', {})
        memory_util = system_health.get('memory_utilization', 0)

        if memory_util > 0.95:
            await self.emergency_stop("memory_usage_critical")
            return

        # Verificar tasa de error muy alta
        success_rate = self._calculate_success_rate()
        if (self.coordination_metrics['failed_operations'] > 10 and
            success_rate < 0.1):
            await self.emergency_stop("error_rate_too_high")
            return

        # Verificar sobrecarga del sistema
        pending_decisions = controller_status.get('pending_decisions', 0)
        if pending_decisions > 50:
            await self.emergency_stop("system_overload")

    async def _check_notification_thresholds(self, status: Dict[str, Any]):
        """Verifica umbrales para notificaciones humanas."""
        thresholds = self.config.human_notification_thresholds

        # Verificar salud del sistema
        controller_status = status.get('autonomous_controller', {})
        consciousness = controller_status.get('consciousness', {})
        system_health = consciousness.get('system_health', {})

        # Aquí se implementarían notificaciones reales
        # Por ahora, solo registrar en logs

        brain_efficiency = system_health.get('brain_efficiency', 1.0)
        if brain_efficiency < thresholds['system_health']:
            logger.warning(f"📢 System health below threshold: {brain_efficiency:.2f}")

        success_rate = self._calculate_success_rate()
        if success_rate < thresholds['autonomy_effectiveness']:
            logger.warning(f"📢 Autonomy effectiveness below threshold: {success_rate:.2f}")

    async def _log_system_event(self, event_type: str, data: Dict[str, Any]):
        """Registra eventos del sistema."""
        if self.autonomous_controller:
            await self.autonomous_controller._record_system_event(event_type, data)

    async def _display_autonomous_status(self):
        """Muestra el estado del sistema autónomo."""
        status = await self.get_autonomous_status()

        print("\n" + "="*60)
        print("🤖 AUTONOMOUS SCRAPER SYSTEM STATUS")
        print("="*60)

        # Estado del coordinador
        coord = status['coordinator']
        print(f"📊 Coordinator Status: {'🟢 Running' if coord['is_running'] else '🔴 Stopped'}")
        print(f"⚡ Autonomy Level: {status['config']['autonomy_level'].upper()}")
        print(f"⏱️  Uptime: {coord['uptime']:.1f} seconds")

        # Métricas
        metrics = coord['coordination_metrics']
        print(f"📈 Total Actions: {metrics['total_autonomous_actions']}")
        print(f"✅ Success Rate: {self._calculate_success_rate():.1%}")
        print(f"🔧 Auto Recoveries: {metrics['auto_recoveries']}")

        # Estado del controlador
        if 'autonomous_controller' in status:
            controller = status['autonomous_controller']
            consciousness = controller['consciousness']
            print(f"🧠 Consciousness Level: {consciousness['awareness_level']:.1%}")
            print(f"🎯 Active Processes: {len(consciousness['active_processes'])}")
            print(f"📋 Pending Decisions: {controller['pending_decisions']}")

        print("="*60)

    async def _cleanup_resources(self):
        """Limpia recursos del sistema."""
        try:
            # Limpiar tareas pendientes
            tasks = [task for task in asyncio.all_tasks() if not task.done()]
            for task in tasks:
                if task != asyncio.current_task():
                    task.cancel()

            # Esperar a que las tareas se cancelen
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

            logger.info("🧹 Resources cleaned up")

        except Exception as e:
            logger.error(f"Error cleaning up resources: {e}")

    async def _notify_emergency(self, reason: str):
        """Notifica una situación de emergencia."""
        emergency_msg = f"""
🚨 EMERGENCY STOP TRIGGERED 🚨
Time: {datetime.now().isoformat()}
Reason: {reason}
System Status: Emergency Mode Active
Autonomous Operations: SUSPENDED

The autonomous system has detected a critical condition
and has safely stopped all operations. Human intervention
may be required to resolve the issue.
"""

        print(emergency_msg)
        logger.critical(emergency_msg)

        # En producción, esto enviaría notificaciones reales
        # (email, SMS, webhooks, etc.)

    async def _begin_autonomous_scraping(self):
        """Inicia operaciones de scraping autónomo automáticamente."""
        logger.info("🎯 Beginning autonomous scraping operations...")

        # En modo completamente autónomo, el sistema decidirá qué hacer
        # Por ahora, esto sería un placeholder para lógica de inicio automático

        # El sistema podría:
        # 1. Revisar tareas pendientes
        # 2. Identificar oportunidades de scraping
        # 3. Comenzar operaciones basadas en objetivos

        logger.info("⚡ Autonomous scraping ready - system will act on opportunities")

    def _setup_signal_handlers(self):
        """Configura manejadores de señales para parada limpia."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating clean shutdown...")

            # Crear tarea para parada limpia
            if self.is_running:
                asyncio.create_task(self.stop_autonomous_operation("signal_received"))

        # Registrar manejadores de señales
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


# Factory function para crear instancia global
_global_coordinator: Optional[AutonomousScraperCoordinator] = None

def get_autonomous_coordinator(project_root: str = None,
                             config: AutonomousConfig = None) -> AutonomousScraperCoordinator:
    """Obtiene la instancia global del coordinador autónomo."""
    global _global_coordinator

    if _global_coordinator is None:
        _global_coordinator = AutonomousScraperCoordinator(project_root, config)

    return _global_coordinator


# Funciones de conveniencia para uso directo

async def start_autonomous_scraper(project_root: str = None,
                                 autonomy_level: AutonomyLevel = AutonomyLevel.FULLY_AUTONOMOUS):
    """Inicia el sistema de scraping autónomo con configuración simple."""
    config = AutonomousConfig(autonomy_level=autonomy_level)
    coordinator = get_autonomous_coordinator(project_root, config)

    await coordinator.initialize()
    await coordinator.start_autonomous_operation()

    return coordinator


async def autonomous_scrape(targets: Union[str, List[str]],
                          objectives: List[str] = None,
                          project_root: str = None) -> Dict[str, Any]:
    """Realiza scraping completamente autónomo de manera simple."""
    coordinator = get_autonomous_coordinator(project_root)

    if not coordinator.is_running:
        await start_autonomous_scraper(project_root)

    return await coordinator.scrape_autonomous(targets, objectives)
