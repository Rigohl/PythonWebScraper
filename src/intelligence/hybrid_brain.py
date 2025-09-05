"""
Hybrid Brain System - Fusión de AutonomousLearningBrain (IA-B) + Brain (IA-A)

Este módulo combina lo mejor de ambos sistemas:
- Brain de IA-A: Eventos ligeros, heurísticas de dominio, persistencia JSON simple
- AutonomousLearningBrain de IA-B: Aprendizaje de patrones, estrategias adaptativas, inteligencia predictiva

El HybridBrain actúa como:
1. Proxy inteligente que envía eventos a ambos sistemas
2. Orchestrador de decisiones que combina insights de ambos
3. Coordinador de comunicación inter-IA via IA_SYNC.md
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
import statistics

from .brain import Brain, ExperienceEvent
from .autonomous_brain import AutonomousLearningBrain, ScrapingSession, DomainIntelligence
import time

logger = logging.getLogger(__name__)

class HybridBrain:
    """🧠 Sistema híbrido que combina Brain (IA-A) + AutonomousLearningBrain (IA-B)"""

    def __init__(self, state_file: str = "data/brain_state.json", learning_file: str = "data/autonomous_learning.json"):
        # IA-A Brain: Eventos ligeros y heurísticas de dominio
        self.simple_brain = Brain(state_file=state_file)

        # IA-B AutonomousLearningBrain: Aprendizaje profundo y patrones
        # Ajuste: AutonomousLearningBrain usa parámetro data_path
        self.autonomous_brain = AutonomousLearningBrain(data_path=learning_file)

        # Comunicación inter-IA
        self.ia_sync_file = "IA_SYNC.md"

        # Cargar configuración de overrides según sugerencia de IA-A
        self.overrides = self._load_brain_overrides()

        logger.info("🧠 Hybrid Brain initialized - combining IA-A + IA-B intelligence systems")
        logger.info(f"🧠 Brain overrides loaded: {len(self.overrides)} settings")

    def _load_brain_overrides(self) -> Dict[str, Any]:
        """Carga configuración de overrides desde brain_overrides.json (sugerencia IA-A)"""
        overrides_file = "config/brain_overrides.json"
        defaults = {
            "priority_weight_success": 0.6,
            "priority_weight_link": 0.4,
            "backoff_threshold": 0.5,
            "min_visits_for_backoff": 5,
            "autonomous_learning_weight": 0.4,
            "simple_brain_weight": 0.6
        }

        try:
            if os.path.exists(overrides_file):
                with open(overrides_file, 'r', encoding='utf-8') as f:
                    overrides = json.load(f)
                logger.info(f"🧠 Loaded brain overrides from {overrides_file}")
                return {**defaults, **overrides}
            else:
                logger.info("🧠 Using default brain configuration (no overrides file)")
                return defaults
        except Exception as e:
            logger.warning(f"Error loading brain overrides: {e}, using defaults")
            return defaults

    def record_scraping_result(self, result, context: Dict[str, Any] = None):
        """Registra un resultado de scraping en ambos sistemas"""

        # Extraer información del resultado
        url = getattr(result, 'url', '')
        domain = urlparse(url).netloc if url else ''

        # Determinar estado
        if getattr(result, 'success', False):
            status = "SUCCESS"
        elif getattr(result, 'is_duplicate', False):
            status = "DUPLICATE"
        elif getattr(result, 'error', None):
            status = "ERROR"
        else:
            status = "RETRY"

        # Crear evento para Brain (IA-A)
        event = ExperienceEvent(
            url=url,
            status=status,
            response_time=context.get('response_time') if context else None,
            content_length=len(getattr(result, 'content', '') or ''),
            new_links=len(getattr(result, 'links', []) or []),
            domain=domain,
            extracted_fields=len(getattr(result, 'extracted_data', {}) or {}),
            error_type=context.get('error_type') if context else None
        )

        # Registrar en Brain (IA-A)
        self.simple_brain.record_event(event)

        # Crear sesión para AutonomousLearningBrain (IA-B) con el dataclass real
        content_len = len(getattr(result, 'content', '') or '')
        extracted_fields = len(getattr(result, 'extracted_data', {}) or {})
        response_time = (context or {}).get('response_time', 0.0)
        status_code = getattr(result, 'status_code', 200 if status == 'SUCCESS' else 500)
        retry_count = (context or {}).get('retry_count', 0)
        user_agent = (context or {}).get('user_agent', '')
        delay_used = (context or {}).get('delay_used', 1.0)
        # Heurística simple para calidad de extracción
        extraction_quality = min(extracted_fields / 10.0, 1.0) if extracted_fields else 0.0
        patterns_found = self._extract_patterns(result)
        errors = []
        if status == 'ERROR':
            errors = [getattr(result, 'error_message', (context or {}).get('error_type', 'unknown'))]

        try:
            session = ScrapingSession(
                domain=domain,
                url=url,
                timestamp=time.time(),
                success=(status == 'SUCCESS'),
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

        # Log híbrido
        logger.debug(f"🧠 Hybrid learning: {status} for {domain} - Brain+Autonomous updated")

    def _extract_patterns(self, result) -> List[str]:
        """Extrae patrones avanzados del resultado para el aprendizaje autónomo profundo"""
        patterns = []

        # Patrones de estructura de página
        if hasattr(result, 'extracted_data') and result.extracted_data:
            for key in result.extracted_data.keys():
                patterns.append(f"field_{key}")

                # Análisis de tipo de dato para cada campo extraído
                value = result.extracted_data.get(key)
                if isinstance(value, str):
                    # Detectar formatos específicos
                    if value and value[0].isdigit():
                        if '$' in value or '€' in value:
                            patterns.append(f"price_format_{key}")
                        elif '-' in value or '/' in value:
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
        if hasattr(result, 'links') and result.links:
            link_count = len(result.links)
            patterns.append(f"links_found_{link_count}")

            # Detectar patrones en URLs
            internal_links = 0
            media_links = 0
            pagination_candidates = 0
            domain_patterns = set()

            if hasattr(result, 'url'):
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
                            if any(x in path for x in ['/page/', '/p/', 'page=', '?p=']):
                                pagination_candidates += 1
                            elif query and any(x in query for x in ['page=', 'p=', 'pg=']):
                                pagination_candidates += 1

                        # Detectar links a recursos específicos
                        if any(media in link.lower() for media in ['.jpg', '.png', '.pdf', '.mp4']):
                            media_links += 1
                    except:
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
        content_text = getattr(result, 'content_text', '') or ''
        content_html = getattr(result, 'content_html', '') or ''
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
            if '<table' in content_html:
                tables_count = content_html.count('<table')
                patterns.append(f"tables_{min(tables_count, 10)}")

            # Detectar formularios
            if '<form' in content_html:
                forms_count = content_html.count('<form')
                patterns.append(f"forms_{forms_count}")

            # Detectar scripts incrustados
            if '<script' in content_html:
                scripts_count = content_html.count('<script')
                patterns.append(f"scripts_{min(scripts_count, 20)}")

                # Detectar frameworks comunes
                js_frameworks = ['react', 'vue', 'angular', 'jquery', 'bootstrap']
                for framework in js_frameworks:
                    if framework in content_html.lower():
                        patterns.append(f"uses_{framework}")

            # Detectar secciones importantes
            if '<header' in content_html or '<nav' in content_html:
                patterns.append("has_header_nav")

            if '<footer' in content_html:
                patterns.append("has_footer")

            # Detectar estructuras comunes
            if '<article' in content_html:
                patterns.append("article_structure")

            if '<section' in content_html:
                sections_count = content_html.count('<section')
                patterns.append(f"sections_{min(sections_count, 10)}")

        # Análisis semántico del contenido
        if content_text:
            # Detectar tipo de contenido
            semantic_indicators = {
                "product": ["comprar", "precio", "disponible", "envío", "stock", "producto"],
                "article": ["publicado", "autor", "artículo", "leer", "comentarios"],
                "profile": ["perfil", "usuario", "biografía", "seguir", "miembro"],
                "listing": ["resultados", "ordenar por", "filtrar", "mostrar", "búsqueda"],
                "news": ["noticia", "última hora", "reportaje", "periodista", "actualidad"]
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
                "de": ["der", "die", "das", "und", "ist", "für"]
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
        if hasattr(result, 'http_status_code') and result.http_status_code:
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
        if hasattr(result, 'response_time') and result.response_time:
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
        if hasattr(result, 'healing_events') and result.healing_events:
            healing_count = len(result.healing_events)
            patterns.append(f"healing_applied_{min(healing_count, 5)}")

            # Tipos de healing aplicados
            healing_types = set()
            for event in result.healing_events:
                if 'type' in event:
                    healing_types.add(event['type'])

            for htype in healing_types:
                patterns.append(f"healing_type_{htype}")

        # LLM insights
        if hasattr(result, 'llm_extracted_data') and result.llm_extracted_data:
            patterns.append("llm_enhanced")

            # Contar campos extraídos por LLM
            llm_fields = len(result.llm_extracted_data)
            patterns.append(f"llm_fields_{min(llm_fields, 10)}")

        return patterns

    def get_domain_priority(self, domain: str) -> float:
        """Calcula prioridad de dominio combinando ambos sistemas con overrides configurables"""

        # Prioridad básica del Brain (IA-A) con overrides
        simple_priority = (
            self.simple_brain.domain_success_rate(domain) * self.overrides["priority_weight_success"] +
            self.simple_brain.link_yield(domain) * self.overrides["priority_weight_link"]
        )

        # Inteligencia del AutonomousLearningBrain (IA-B)
        autonomous_priority = 0.0

        # Usar la inteligencia autónoma (adaptado a la API real)
        try:
            import statistics
            domain_sessions = [s for s in self.autonomous_brain.session_history if s.domain == domain]
            if domain_sessions:
                success_rate = sum(1 for s in domain_sessions if s.success) / len(domain_sessions)
                avg_response = statistics.mean([s.response_time for s in domain_sessions]) if domain_sessions else 0
                pattern_count = sum(len(s.patterns_found) for s in domain_sessions)

                autonomous_priority = (
                    success_rate * 0.4 +
                    min(avg_response / 1000, 1.0) * 0.3 +  # Convertir ms a ratio
                    (pattern_count / 10) * 0.3  # Normalizar patrones
                )
        except Exception:
            # Fallback en caso de error
            autonomous_priority = 0.0

        # Combinar ambas prioridades con pesos configurables (overrides)
        hybrid_priority = (
            simple_priority * self.overrides["simple_brain_weight"] +
            autonomous_priority * self.overrides["autonomous_learning_weight"]
        )

        return hybrid_priority

    def should_backoff(self, domain: str) -> bool:
        """Determina si debe hacer backoff combinando ambos sistemas con overrides configurables"""

        # Backoff simple del Brain (IA-A) con configuración override
        simple_backoff = self.simple_brain.should_backoff(
            domain,
            error_threshold=self.overrides["backoff_threshold"],
            min_visits=self.overrides["min_visits_for_backoff"]
        )

        # Backoff inteligente del AutonomousLearningBrain (IA-B)
        autonomous_backoff = False

        try:
            # Usar la API real del cerebro autónomo
            domain_sessions = [s for s in self.autonomous_brain.session_history if s.domain == domain]
            if len(domain_sessions) >= self.overrides["min_visits_for_backoff"]:
                success_rate = sum(1 for s in domain_sessions if s.success) / len(domain_sessions)
                error_count = sum(len(s.errors) for s in domain_sessions)

                # Backoff si el éxito es muy bajo o hay muchos errores
                autonomous_backoff = (
                    success_rate < self.overrides["backoff_threshold"] or
                    error_count > 3
                )
        except Exception:
            autonomous_backoff = False

        # Si cualquiera de los dos sugiere backoff, hacemos backoff
        return simple_backoff or autonomous_backoff

    def get_optimization_config(self, domain: str) -> Dict[str, Any]:
        """Obtiene configuración optimizada para un dominio"""

        config = {}

        try:
            import statistics
            # Usar la API real del cerebro autónomo
            domain_sessions = [s for s in self.autonomous_brain.session_history if s.domain == domain]
            if domain_sessions:
                success_rate = sum(1 for s in domain_sessions if s.success) / len(domain_sessions)

                # Extraer estrategias basadas en sesiones exitosas
                successful_sessions = [s for s in domain_sessions if s.success]
                if successful_sessions:
                    best_session = max(successful_sessions, key=lambda s: s.extraction_quality)
                    config.update({
                        'delay': best_session.delay_used,
                        'user_agent_pattern': best_session.user_agent,
                        'retry_count': min(5, max(1, int(statistics.median([s.retry_count for s in successful_sessions])))),
                        'timeout': 30,  # Valor por defecto
                        'predicted_success_rate': success_rate
                    })
        except Exception:
            # Si hay error, no añadimos nada a la configuración
            pass

        # Combinar con métricas del Brain simple
        config.update({
            'simple_priority': self.simple_brain.domain_priority(domain),
            'error_rate': self.simple_brain.domain_error_rate(domain),
            'avg_response_time': self.simple_brain.avg_response_time(domain)
        })

        return config

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas comprehensivas de ambos sistemas"""

        # Stats del Brain (IA-A)
        simple_stats = self.simple_brain.snapshot()

        # Stats del AutonomousLearningBrain (IA-B)
        try:
            domains_learned = len(self.autonomous_brain.domain_intelligence)
            total_patterns = sum(len(v) for v in self.autonomous_brain.pattern_library.values())
            # Contar estrategias: suma de longitudes de best_strategies por dominio
            strategies_optimized = sum(len(intel.best_strategies) for intel in self.autonomous_brain.domain_intelligence.values())
            learning_sessions = len(self.autonomous_brain.session_history)
        except Exception as e:
            logger.error(f"Error collecting autonomous brain stats: {e}")
            domains_learned = 0
            total_patterns = 0
            strategies_optimized = 0
            learning_sessions = 0

        # Calcular métricas avanzadas de AutonomousLearningBrain
        try:
            successful_sessions = sum(1 for s in self.autonomous_brain.session_history if s.success)
            success_rate = successful_sessions / max(learning_sessions, 1) if learning_sessions > 0 else 0

            # Analizar los tiempos de respuesta
            response_times = [s.response_time for s in self.autonomous_brain.session_history if s.success]
            avg_response_time = statistics.mean(response_times) if response_times else 0

            # Analizar patrones más comunes
            all_patterns = []
            for session in self.autonomous_brain.session_history:
                all_patterns.extend(session.patterns_found)

            pattern_frequency = {}
            for pattern in all_patterns:
                pattern_frequency[pattern] = pattern_frequency.get(pattern, 0) + 1

            top_patterns = sorted(pattern_frequency.items(), key=lambda x: x[1], reverse=True)[:5]

            # Estadísticas por dominio
            domain_success_rates = {}
            for domain, intel in self.autonomous_brain.domain_intelligence.items():
                domain_success_rates[domain] = intel.success_rate

            # Eficiencia de aprendizaje
            learning_efficiency = self.autonomous_brain._calculate_learning_efficiency()
        except Exception as e:
            logger.error(f"Error calculating advanced autonomous brain metrics: {e}")
            successful_sessions = 0
            success_rate = 0
            avg_response_time = 0
            top_patterns = []
            domain_success_rates = {}
            learning_efficiency = 0

        autonomous_stats = {
            'domains_learned': domains_learned,
            'total_patterns': total_patterns,
            'strategies_optimized': strategies_optimized,
            'learning_sessions': learning_sessions,
            'success_rate': round(success_rate, 2),
            'avg_response_time': round(avg_response_time, 2),
            'top_patterns': top_patterns,
            'domain_success_rates': domain_success_rates,
            'learning_efficiency': round(learning_efficiency, 2)
        }

        # Combinar estadísticas
        hybrid_stats = {
            'hybrid_system': True,
            'simple_brain': simple_stats,
            'autonomous_brain': autonomous_stats,
            'top_performing_domains': self._get_top_performing_domains(),
            'learning_insights': self._get_learning_insights(),
            'overrides': self.overrides,
        }

        return hybrid_stats

    # ----------------- Compatibilidad con interfaz Brain simple -----------------
    def snapshot(self) -> Dict[str, Any]:  # pragma: no cover - usada por tests heredados
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
        simple = self.simple_brain.snapshot()
        simple['hybrid'] = True
        return simple

    def domain_priority(self, domain: str) -> float:  # pragma: no cover
        """Alias para permitir que código legado use domain_priority()."""
        try:
            return self.get_domain_priority(domain)
        except Exception:
            return 0.0

    def _get_top_performing_domains(self) -> List[Dict[str, Any]]:
        """Obtiene los dominios con mejor rendimiento combinado"""

        domain_scores = {}

        # Combinar dominios de ambos sistemas
        all_domains = set(self.simple_brain.domain_stats.keys()) | set(self.autonomous_brain.domain_intelligence.keys())

        for domain in all_domains:
            hybrid_priority = self.get_domain_priority(domain)
            simple_success = self.simple_brain.domain_success_rate(domain)

            domain_scores[domain] = {
                'domain': domain,
                'hybrid_priority': hybrid_priority,
                'simple_success_rate': simple_success,
                'total_visits': self.simple_brain.domain_stats.get(domain, {}).get('visits', 0)
            }

        # Ordenar por prioridad híbrida
        sorted_domains = sorted(domain_scores.values(), key=lambda x: x['hybrid_priority'], reverse=True)

        return sorted_domains[:5]

    def _get_learning_insights(self) -> List[str]:
        """Obtiene insights de aprendizaje del sistema"""

        insights = []

        # Insights del Brain simple
        top_errors = sorted(self.simple_brain.error_type_freq.items(), key=lambda x: x[1], reverse=True)[:3]
        if top_errors:
            insights.append(f"Errores más comunes: {', '.join([f'{err}({count})' for err, count in top_errors])}")

        # Insights del sistema autónomo
        total_patterns = sum(len(di.discovered_patterns) for di in self.autonomous_brain.domain_intelligence.values())
        if total_patterns > 0:
            insights.append(f"Patrones descubiertos: {total_patterns} únicos")

        try:
            domains_with_strategies = sum(1 for intel in self.autonomous_brain.domain_intelligence.values() if intel.best_strategies)
            if domains_with_strategies > 0:
                insights.append(f"Estrategias optimizadas: {domains_with_strategies} dominios")
        except Exception:
            pass

        return insights

    def flush(self):
        """Persiste el estado de ambos sistemas"""
        self.simple_brain.flush()
        self.autonomous_brain.save_learning_data()

        # Actualizar comunicación inter-IA
        self._update_ia_sync()

    def _update_ia_sync(self):
        """Actualiza el archivo de sincronización inter-IA"""

        try:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

            # Preparar mensaje de estado
            stats = self.get_comprehensive_stats()
            domains_count = len(stats['simple_brain']['domains'])
            patterns_count = stats['autonomous_brain']['total_patterns']

            new_entry = f"{timestamp} | FEAT | IA-B: Sistema híbrido activo - {domains_count} dominios, {patterns_count} patrones\n"

            # Agregar entrada al final del archivo
            with open(self.ia_sync_file, 'a', encoding='utf-8') as f:
                f.write(new_entry)

            logger.info("🧠 IA_SYNC updated with hybrid brain status")

        except Exception as e:
            logger.error(f"Failed to update IA_SYNC: {e}")

# Singleton para uso global
_hybrid_brain_instance = None

def get_hybrid_brain() -> HybridBrain:
    """Obtiene la instancia singleton del HybridBrain"""
    global _hybrid_brain_instance
    if _hybrid_brain_instance is None:
        _hybrid_brain_instance = HybridBrain()
    return _hybrid_brain_instance
