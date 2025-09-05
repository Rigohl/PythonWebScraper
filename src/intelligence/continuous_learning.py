"""
Continuous Learning System
Sistema de aprendizaje continuo que integra todos los módulos de inteligencia
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import threading
import schedule

from .advanced_ml import AdvancedMLIntelligence
from .self_improvement import SelfImprovingSystem
from .cdp_stealth import StealthCDPBrowser
from .knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)

class LearningSession:
    """Representa una sesión de aprendizaje"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.start_time = time.time()
        self.end_time = None
        self.scraped_urls = []
        self.learned_patterns = []
        self.applied_improvements = []
        self.performance_metrics = {}

    def add_scraped_url(self, url: str, success: bool, response_time: float,
                       strategy_used: str, errors: int = 0):
        """Añade URL scrapeada a la sesión"""
        self.scraped_urls.append({
            'url': url,
            'success': success,
            'response_time': response_time,
            'strategy_used': strategy_used,
            'errors': errors,
            'timestamp': time.time()
        })

    def add_learned_pattern(self, pattern_type: str, pattern_data: Dict):
        """Añade patrón aprendido"""
        self.learned_patterns.append({
            'type': pattern_type,
            'data': pattern_data,
            'confidence': pattern_data.get('confidence', 0.8),
            'timestamp': time.time()
        })

    def add_improvement(self, improvement_type: str, target: str, success: bool):
        """Añade mejora aplicada"""
        self.applied_improvements.append({
            'type': improvement_type,
            'target': target,
            'success': success,
            'timestamp': time.time()
        })

    def finalize(self):
        """Finaliza la sesión y calcula métricas"""
        self.end_time = time.time()

        if self.scraped_urls:
            success_rate = sum(1 for url in self.scraped_urls if url['success']) / len(self.scraped_urls)
            avg_response_time = sum(url['response_time'] for url in self.scraped_urls) / len(self.scraped_urls)
            total_errors = sum(url['errors'] for url in self.scraped_urls)
        else:
            success_rate = 0
            avg_response_time = 0
            total_errors = 0

        self.performance_metrics = {
            'duration': self.end_time - self.start_time,
            'urls_scraped': len(self.scraped_urls),
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'total_errors': total_errors,
            'patterns_learned': len(self.learned_patterns),
            'improvements_applied': len([i for i in self.applied_improvements if i['success']]),
            'improvement_success_rate': (
                len([i for i in self.applied_improvements if i['success']]) /
                len(self.applied_improvements) if self.applied_improvements else 0
            )
        }

    def to_dict(self) -> Dict:
        """Convierte sesión a diccionario"""
        return {
            'session_id': self.session_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'scraped_urls': self.scraped_urls,
            'learned_patterns': self.learned_patterns,
            'applied_improvements': self.applied_improvements,
            'performance_metrics': self.performance_metrics
        }

class ContinuousLearningEngine:
    """Motor de aprendizaje continuo para el sistema autónomo"""

    def __init__(self, data_dir: str = "data/continuous_learning"):
        self.orchestrator = ContinuousLearningOrchestrator(data_dir)
        self.is_running = False
        self.auto_learning_enabled = True

    def start(self):
        """Inicia el motor de aprendizaje continuo"""
        self.is_running = True
        self.orchestrator.start_background_learning()
        return self.orchestrator.start_learning_session()

    def stop(self):
        """Detiene el motor de aprendizaje continuo"""
        self.is_running = False
        self.orchestrator.stop_background_learning()
        return self.orchestrator.end_learning_session()

    def learn_from_operation(self, url: str, html: str, response_time: float,
                           status_code: int, success: bool, strategy_used: str,
                           errors: int = 0):
        """Aprende de una operación de scraping"""
        if not self.auto_learning_enabled:
            return None

        return self.orchestrator.learn_from_scraping(
            url, html, response_time, status_code, success, strategy_used, errors
        )

    def get_status(self) -> Dict[str, Any]:
        """Obtiene estado del motor de aprendizaje"""
        summary = self.orchestrator.get_learning_summary()
        summary.update({
            'engine_running': self.is_running,
            'auto_learning_enabled': self.auto_learning_enabled
        })
        return summary

    def enable_auto_learning(self):
        """Habilita aprendizaje automático"""
        self.auto_learning_enabled = True

    def disable_auto_learning(self):
        """Deshabilita aprendizaje automático"""
        self.auto_learning_enabled = False

class ContinuousLearningOrchestrator:
    """Orquestador principal del sistema de aprendizaje continuo"""

    def __init__(self, data_dir: str = "data/continuous_learning"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Componentes de IA
        self.ml_intelligence = AdvancedMLIntelligence()
        self.self_improver = SelfImprovingSystem()
        self.knowledge_base = KnowledgeBase()

        # Estado del sistema
        self.current_session: Optional[LearningSession] = None
        self.learning_history = []
        self.background_learning_active = False

        # Configuración
        self.config = {
            'auto_improvement_interval': 3600,  # 1 hora
            'pattern_analysis_interval': 1800,   # 30 minutos
            'knowledge_update_interval': 7200,   # 2 horas
            'max_session_duration': 14400,       # 4 horas
            'min_data_for_learning': 10,         # Mínimo de datos para aprender
            'learning_rate_decay': 0.95,         # Decay del learning rate
        }

        self._load_learning_history()

    def start_learning_session(self, session_id: Optional[str] = None) -> str:
        """Inicia nueva sesión de aprendizaje"""
        if self.current_session:
            self.end_learning_session()

        session_id = session_id or f"session_{int(time.time())}"
        self.current_session = LearningSession(session_id)

        logger.info(f"Started learning session: {session_id}")
        return session_id

    def end_learning_session(self) -> Optional[Dict]:
        """Finaliza sesión actual de aprendizaje"""
        if not self.current_session:
            return None

        self.current_session.finalize()
        session_data = self.current_session.to_dict()

        # Guardar en historial
        self.learning_history.append(session_data)
        self._save_learning_history()

        # Procesar aprendizajes de la sesión
        self._process_session_learnings(self.current_session)

        logger.info(f"Ended learning session: {self.current_session.session_id}")
        logger.info(f"Session metrics: {self.current_session.performance_metrics}")

        self.current_session = None
        return session_data

    def learn_from_scraping(self, url: str, html: str, response_time: float,
                          status_code: int, success: bool, strategy_used: str,
                          errors: int = 0):
        """Aprende de una operación de scraping"""

        # 1. Análisis ML del sitio
        ml_recommendation = self.ml_intelligence.analyze_and_recommend(
            url, html, response_time, status_code
        )

        # 2. Aprender del resultado
        self.ml_intelligence.learn_from_outcome(
            url, ml_recommendation, success, response_time, errors
        )

        # 3. Detectar patrones nuevos
        patterns = self._detect_new_patterns(url, ml_recommendation, success)

        # 4. Actualizar knowledge base si es necesario
        if patterns:
            self._update_knowledge_base(patterns)

        # 5. Registrar en sesión actual
        if self.current_session:
            self.current_session.add_scraped_url(
                url, success, response_time, strategy_used, errors
            )

            for pattern in patterns:
                self.current_session.add_learned_pattern(
                    pattern['type'], pattern['data']
                )

        return {
            'ml_recommendation': ml_recommendation,
            'patterns_detected': patterns,
            'learning_applied': True
        }

    def _detect_new_patterns(self, url: str, ml_recommendation: Dict,
                           success: bool) -> List[Dict]:
        """Detecta nuevos patrones en los datos"""
        patterns = []

        features = ml_recommendation['features']

        # Patrón de éxito para sitios con Cloudflare
        if features.get('has_cloudflare', 0) > 0.7 and success:
            patterns.append({
                'type': 'cloudflare_success_pattern',
                'data': {
                    'strategy': ml_recommendation['rl_recommended_action'],
                    'response_time': features['response_time'],
                    'confidence': 0.8
                },
                'url': url
            })

        # Patrón de sitio complejo que responde bien
        if features.get('dom_depth', 0) > 15 and features.get('script_count', 0) > 10 and success:
            patterns.append({
                'type': 'complex_site_success',
                'data': {
                    'dom_depth': features['dom_depth'],
                    'script_count': features['script_count'],
                    'strategy': ml_recommendation['rl_recommended_action'],
                    'confidence': 0.85
                },
                'url': url
            })

        # Patrón de anomalía que tuvo éxito
        if ml_recommendation.get('anomaly_detected') and success:
            patterns.append({
                'type': 'anomaly_success',
                'data': {
                    'anomaly_confidence': ml_recommendation['anomaly_confidence'],
                    'successful_strategy': ml_recommendation['rl_recommended_action'],
                    'confidence': 0.9
                },
                'url': url
            })

        return patterns

    def _update_knowledge_base(self, patterns: List[Dict]):
        """Actualiza knowledge base con nuevos patrones"""
        for pattern in patterns:
            if pattern['type'] == 'cloudflare_success_pattern':
                snippet_id = f"learned:cloudflare-bypass-{int(time.time())}"
                self.knowledge_base.add_snippet(
                    snippet_id,
                    "learned-patterns",
                    "Cloudflare Bypass Success Pattern",
                    f"Strategy '{pattern['data']['strategy']}' successful for Cloudflare sites "
                    f"with response time {pattern['data']['response_time']:.2f}s",
                    ["cloudflare", "bypass", "learned", "success"],
                    pattern['data']['confidence']
                )

            elif pattern['type'] == 'complex_site_success':
                snippet_id = f"learned:complex-site-{int(time.time())}"
                self.knowledge_base.add_snippet(
                    snippet_id,
                    "learned-patterns",
                    "Complex Site Handling Pattern",
                    f"Sites with DOM depth {pattern['data']['dom_depth']} and "
                    f"{pattern['data']['script_count']} scripts respond well to "
                    f"strategy '{pattern['data']['strategy']}'",
                    ["complex-sites", "dom-depth", "learned", "success"],
                    pattern['data']['confidence']
                )

    def _process_session_learnings(self, session: LearningSession):
        """Procesa aprendizajes al final de la sesión"""

        # 1. Analizar tendencias de la sesión
        if len(session.scraped_urls) >= self.config['min_data_for_learning']:
            self._analyze_session_trends(session)

        # 2. Actualizar modelos ML
        self.ml_intelligence.save_models()

        # 3. Ejecutar auto-mejora si es necesario
        if len(session.applied_improvements) < 2:  # Pocas mejoras aplicadas
            self._trigger_auto_improvement()

    def _analyze_session_trends(self, session: LearningSession):
        """Analiza tendencias en la sesión"""
        urls = session.scraped_urls

        # Estrategias más exitosas
        strategy_success = {}
        for url_data in urls:
            strategy = url_data['strategy_used']
            if strategy not in strategy_success:
                strategy_success[strategy] = {'success': 0, 'total': 0}

            strategy_success[strategy]['total'] += 1
            if url_data['success']:
                strategy_success[strategy]['success'] += 1

        # Encontrar mejor estrategia
        best_strategy = None
        best_rate = 0

        for strategy, stats in strategy_success.items():
            if stats['total'] >= 3:  # Mínimo de muestras
                rate = stats['success'] / stats['total']
                if rate > best_rate:
                    best_rate = rate
                    best_strategy = strategy

        if best_strategy and best_rate > 0.8:
            # Actualizar knowledge base con tendencia
            snippet_id = f"session-trend-{session.session_id}"
            self.knowledge_base.add_snippet(
                snippet_id,
                "session-trends",
                f"High Success Strategy: {best_strategy}",
                f"Strategy '{best_strategy}' achieved {best_rate:.2%} success rate "
                f"in session {session.session_id} with {strategy_success[best_strategy]['total']} samples",
                ["session-trends", "high-success", best_strategy],
                best_rate
            )

            logger.info(f"Detected high-success strategy trend: {best_strategy} ({best_rate:.2%})")

    def _trigger_auto_improvement(self):
        """Dispara proceso de auto-mejora"""
        try:
            improvement_result = self.self_improver.auto_improve_step()

            if self.current_session and improvement_result.get('improvements_applied', 0) > 0:
                for improvement in improvement_result.get('details', []):
                    self.current_session.add_improvement(
                        improvement['type'],
                        improvement['file'],
                        improvement['success']
                    )

            logger.info(f"Auto-improvement completed: {improvement_result.get('status')}")

        except Exception as e:
            logger.error(f"Auto-improvement failed: {e}")

    def start_background_learning(self):
        """Inicia aprendizaje en segundo plano"""
        if self.background_learning_active:
            return

        self.background_learning_active = True

        # Programar tareas periódicas
        schedule.every(self.config['auto_improvement_interval']).seconds.do(
            self._background_auto_improvement
        )

        schedule.every(self.config['pattern_analysis_interval']).seconds.do(
            self._background_pattern_analysis
        )

        schedule.every(self.config['knowledge_update_interval']).seconds.do(
            self._background_knowledge_update
        )

        # Iniciar thread de background
        self.background_thread = threading.Thread(target=self._background_loop)
        self.background_thread.daemon = True
        self.background_thread.start()

        logger.info("Background learning started")

    def stop_background_learning(self):
        """Detiene aprendizaje en segundo plano"""
        self.background_learning_active = False
        schedule.clear()
        logger.info("Background learning stopped")

    def _background_loop(self):
        """Loop principal de background learning"""
        while self.background_learning_active:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Background learning error: {e}")

    def _background_auto_improvement(self):
        """Auto-mejora en background"""
        try:
            if not self.current_session:  # Solo si no hay sesión activa
                improvement_result = self.self_improver.auto_improve_step()
                logger.info(f"Background auto-improvement: {improvement_result.get('status')}")
        except Exception as e:
            logger.error(f"Background auto-improvement error: {e}")

    def _background_pattern_analysis(self):
        """Análisis de patrones en background"""
        try:
            # Analizar patrones en el historial
            recent_sessions = self.learning_history[-10:]  # Últimas 10 sesiones

            if len(recent_sessions) >= 3:
                self._analyze_cross_session_patterns(recent_sessions)

        except Exception as e:
            logger.error(f"Background pattern analysis error: {e}")

    def _background_knowledge_update(self):
        """Actualización de knowledge base en background"""
        try:
            # Persistir knowledge base
            self.knowledge_base.persist()

            # Limpiar snippets viejos de baja calidad
            self._cleanup_knowledge_base()

        except Exception as e:
            logger.error(f"Background knowledge update error: {e}")

    def _analyze_cross_session_patterns(self, sessions: List[Dict]):
        """Analiza patrones entre múltiples sesiones"""
        # Encontrar estrategias consistentemente exitosas
        strategy_performance = {}

        for session in sessions:
            for url_data in session.get('scraped_urls', []):
                strategy = url_data['strategy_used']
                if strategy not in strategy_performance:
                    strategy_performance[strategy] = []

                strategy_performance[strategy].append({
                    'success': url_data['success'],
                    'response_time': url_data['response_time'],
                    'session': session['session_id']
                })

        # Identificar patrones estables
        for strategy, performance_list in strategy_performance.items():
            if len(performance_list) >= 10:  # Suficientes muestras
                success_rate = sum(1 for p in performance_list if p['success']) / len(performance_list)
                avg_response_time = sum(p['response_time'] for p in performance_list) / len(performance_list)

                if success_rate > 0.85 and avg_response_time < 3.0:
                    # Patrón estable y efectivo
                    snippet_id = f"stable-pattern-{strategy}-{int(time.time())}"
                    self.knowledge_base.add_snippet(
                        snippet_id,
                        "stable-patterns",
                        f"Stable High-Performance Strategy: {strategy}",
                        f"Strategy '{strategy}' shows consistent high performance: "
                        f"{success_rate:.2%} success rate, {avg_response_time:.2f}s avg response time "
                        f"across {len(performance_list)} samples",
                        ["stable-patterns", "high-performance", strategy],
                        success_rate
                    )

                    logger.info(f"Detected stable high-performance pattern: {strategy}")

    def _cleanup_knowledge_base(self):
        """Limpia knowledge base de snippets obsoletos"""
        # Remover snippets de baja calidad viejos
        current_time = time.time()
        old_threshold = current_time - (30 * 24 * 3600)  # 30 días

        snippets_to_remove = []

        for snippet_id, snippet in self.knowledge_base.snippets.items():
            if (snippet.added_ts < old_threshold and
                snippet.quality_score < 0.6 and
                snippet.category in ['learned-patterns', 'session-trends']):
                snippets_to_remove.append(snippet_id)

        for snippet_id in snippets_to_remove:
            del self.knowledge_base.snippets[snippet_id]

        if snippets_to_remove:
            logger.info(f"Cleaned up {len(snippets_to_remove)} old low-quality snippets")

    def _load_learning_history(self):
        """Carga historial de aprendizaje"""
        history_file = self.data_dir / "learning_history.json"

        try:
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.learning_history = json.load(f)
                logger.info(f"Loaded {len(self.learning_history)} learning sessions")
        except Exception as e:
            logger.warning(f"Error loading learning history: {e}")
            self.learning_history = []

    def _save_learning_history(self):
        """Guarda historial de aprendizaje"""
        history_file = self.data_dir / "learning_history.json"

        try:
            # Mantener solo las últimas 100 sesiones
            recent_history = self.learning_history[-100:]

            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(recent_history, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving learning history: {e}")

    def get_learning_summary(self) -> Dict[str, Any]:
        """Obtiene resumen del sistema de aprendizaje"""
        ml_summary = self.ml_intelligence.get_intelligence_summary()
        improvement_summary = self.self_improver.get_improvement_summary()

        # Estadísticas de sesiones
        if self.learning_history:
            total_urls = sum(len(session.get('scraped_urls', [])) for session in self.learning_history)
            total_patterns = sum(len(session.get('learned_patterns', [])) for session in self.learning_history)
            avg_success_rate = sum(
                session.get('performance_metrics', {}).get('success_rate', 0)
                for session in self.learning_history
            ) / len(self.learning_history)
        else:
            total_urls = 0
            total_patterns = 0
            avg_success_rate = 0

        return {
            'current_session_active': self.current_session is not None,
            'current_session_id': self.current_session.session_id if self.current_session else None,
            'background_learning_active': self.background_learning_active,
            'total_learning_sessions': len(self.learning_history),
            'total_urls_learned': total_urls,
            'total_patterns_discovered': total_patterns,
            'average_success_rate': avg_success_rate,
            'knowledge_base_snippets': len(self.knowledge_base.snippets),
            'ml_intelligence': ml_summary,
            'self_improvement': improvement_summary,
            'last_session': self.learning_history[-1] if self.learning_history else None
        }
