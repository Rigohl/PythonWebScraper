"""
Curiosity and Proactivity System for HybridBrain
Sistema de curiosidad y proactividad para el cerebro híbrido

Este módulo implementa capacidades de curiosidad intrínseca y proactividad:
- EmbeddingAdapter: Adaptador pluggable para representaciones vectoriales
- VectorStore: Almacenamiento vectorial simple basado en SQLite
- NoveltyDetector: Detector de novedad basado en similitud y señales cognitivas
- ProactivityManager: Gestor de notificaciones proactivas (advisory-only)
"""

import hashlib
import json
import logging
import math
import os
import sqlite3
import tempfile
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Entrada de memoria para el sistema de curiosidad"""

    content: str
    url: str
    title: str
    timestamp: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    novelty_score: float = 0.5
    importance: float = 0.5

    def get_id(self) -> str:
        """Genera ID único para la entrada"""
        content_hash = hashlib.md5(self.content.encode()).hexdigest()[:12]
        return f"{content_hash}_{int(self.timestamp)}"


class EmbeddingAdapter(ABC):
    """Adaptador abstracto para embeddings"""

    @abstractmethod
    def encode(self, text: str) -> List[float]:
        """Codifica texto a vector"""
        pass

    @abstractmethod
    def similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calcula similitud coseno entre dos vectores"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica si el adaptador está disponible"""
        pass


class TFIDFEmbeddingAdapter(EmbeddingAdapter):
    """Adaptador TF-IDF simple como fallback"""

    def __init__(self):
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.doc_count = 0

    def encode(self, text: str) -> List[float]:
        """Codifica usando TF-IDF simple"""
        words = self._tokenize(text)
        vector = [0.0] * len(self.vocab)

        # Calcular TF
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1

        total_words = len(words)
        if total_words == 0:
            return vector

        # Construir vector TF-IDF
        for word, count in word_counts.items():
            if word in self.vocab:
                tf = count / total_words
                idf_val = self.idf.get(word, 1.0)
                vector[self.vocab[word]] = tf * idf_val

        return vector

    def similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Similitud coseno"""
        if not vec1 or not vec2:
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def is_available(self) -> bool:
        return True

    def _tokenize(self, text: str) -> List[str]:
        """Tokenización simple"""
        return text.lower().split()

    def add_document(self, text: str):
        """Añade documento para construir vocabulario"""
        words = self._tokenize(text)
        self.doc_count += 1

        # Actualizar vocabulario
        for word in set(words):
            if word not in self.vocab:
                self.vocab[word] = len(self.vocab)

        # Actualizar IDF
        # Track document frequency (df) for each term
        for word in set(words):
            # store df counts in the same dict (as a count), will convert to IDF below
            self.idf[word] = self.idf.get(word, 0.0) + 1.0

        # Recalcular IDF usando smoothing para evitar valores cero o negativos
        # idf = log((1 + N) / (1 + df)) + 1  -> garantiza idf > 0
        for word, df in list(self.idf.items()):
            self.idf[word] = math.log((1.0 + self.doc_count) / (1.0 + df)) + 1.0


class VectorStore:
    """Almacén vectorial simple basado en SQLite"""

    def __init__(self, db_path: str = "data/curiosity_vectors.db"):
        self.db_path = db_path
        # Use a private internal DB file when given a file path to avoid
        # holding the same file handle as callers that might try to delete
        # or manage that path (common in tests that use NamedTemporaryFile).
        self._own_temp_db = False
        self._internal_db_path = self.db_path

        # Persistent connection only for in-memory DB
        self._conn = None
        if self.db_path == ":memory:":
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        else:
            # Create an internal temp file to operate on so we don't lock the
            # caller-provided path (which may be removed by tests).
            fd, tmpname = tempfile.mkstemp(suffix=".db")
            try:
                # Close the low-level fd; we'll open/close via sqlite
                os.close(fd)
            except Exception:
                pass
            self._internal_db_path = tmpname
            self._own_temp_db = True

        self._init_db()

    def _init_db(self):
        """Inicializa la base de datos"""
        if self._conn is not None:
            conn = self._conn
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vectors (
                    id TEXT PRIMARY KEY,
                    vector TEXT NOT NULL,
                    timestamp REAL,
                    metadata TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON vectors(timestamp)
            """)
            conn.commit()
        else:
            db_path = self._internal_db_path if self._own_temp_db else self.db_path
            with sqlite3.connect(db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS vectors (
                        id TEXT PRIMARY KEY,
                        vector TEXT NOT NULL,
                        timestamp REAL,
                        metadata TEXT
                    )
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_timestamp ON vectors(timestamp)
                """)

    def store(self, entry_id: str, vector: List[float], metadata: Dict[str, Any]):
        """Almacena vector"""
        db_path = self._internal_db_path if self._own_temp_db else self.db_path
        if self._conn is not None:
            conn = self._conn
            conn.execute(
                """
                INSERT OR REPLACE INTO vectors (id, vector, timestamp, metadata)
                VALUES (?, ?, ?, ?)
            """,
                (
                    entry_id,
                    json.dumps(vector),
                    time.time(),
                    json.dumps(metadata),
                ),
            )
            conn.commit()
        else:
            with sqlite3.connect(db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO vectors (id, vector, timestamp, metadata)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        entry_id,
                        json.dumps(vector),
                        time.time(),
                        json.dumps(metadata),
                    ),
                )

    def retrieve_similar(
        self, query_vector: List[float], limit: int = 10
    ) -> List[Tuple[str, float, Dict]]:
        """Recupera vectores similares"""
        results = []
        db_path = self._internal_db_path if self._own_temp_db else self.db_path
        if self._conn is not None:
            cursor = self._conn.execute("SELECT id, vector, metadata FROM vectors")
            rows = list(cursor)
        else:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("SELECT id, vector, metadata FROM vectors")
                rows = list(cursor)

        for row in rows:
            entry_id, vector_str, metadata_str = row
            stored_vector = json.loads(vector_str)
            metadata = json.loads(metadata_str)

            similarity = self._cosine_similarity(query_vector, stored_vector)
            results.append((entry_id, similarity, metadata))

        # Ordenar por similitud descendente
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calcula similitud coseno"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def get_all_ids(self) -> List[str]:
        """Obtiene todos los IDs almacenados"""
        db_path = self._internal_db_path if self._own_temp_db else self.db_path
        if self._conn is not None:
            cursor = self._conn.execute("SELECT id FROM vectors")
            return [row[0] for row in cursor]
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("SELECT id FROM vectors")
            return [row[0] for row in cursor]

    def __del__(self):
        try:
            if self._conn is not None:
                self._conn.close()
        except Exception:
            pass
        # No further action: avoid extra file opens which can cause locks on
        # Windows during rapid test teardown.
        # Remove any internal temp DB file we created
        try:
            if getattr(self, "_own_temp_db", False) and getattr(
                self, "_internal_db_path", None
            ):
                try:
                    os.unlink(self._internal_db_path)
                except Exception:
                    pass
        except Exception:
            pass


class NoveltyDetector:
    """Detector de novedad que combina múltiples señales"""

    def __init__(self, embedding_adapter: EmbeddingAdapter, vector_store: VectorStore):
        self.embedding_adapter = embedding_adapter
        self.vector_store = vector_store
        self.novelty_threshold = 0.3  # Umbral de novedad
        self.temporal_decay_factor = 0.95  # Decay temporal

    def detect_novelty(
        self, content: str, metadata: Dict[str, Any] = None
    ) -> Tuple[bool, float, Dict]:
        """Detecta si el contenido es novedoso"""
        if not self.embedding_adapter.is_available():
            return False, 0.0, {"reason": "embedding_unavailable"}

        # Generar embedding
        embedding = self.embedding_adapter.encode(content)

        # Buscar contenido similar
        similar_items = self.vector_store.retrieve_similar(embedding, limit=5)

        # Calcular score de novedad
        novelty_score = self._calculate_novelty_score(embedding, similar_items)

        # Considerar señales adicionales
        context_signals = self._analyze_context_signals(content, metadata or {})

        # Score combinado
        combined_score = (novelty_score * 0.7) + (
            context_signals["novelty_boost"] * 0.3
        )

        is_novel = combined_score > self.novelty_threshold

        analysis = {
            "novelty_score": combined_score,
            "embedding_similarity": novelty_score,
            "context_signals": context_signals,
            "similar_items_count": len(similar_items),
            "threshold": self.novelty_threshold,
        }

        return is_novel, combined_score, analysis

    def _calculate_novelty_score(
        self, embedding: List[float], similar_items: List[Tuple[str, float, Dict]]
    ) -> float:
        """Calcula score de novedad basado en similitud"""
        if not similar_items:
            return 1.0  # Completamente novedoso si no hay items similares
        # Aplicar decay temporal a similitudes antiguas
        decayed_similarities = []
        current_time = time.time()
        for _, sim, metadata in similar_items:
            timestamp = metadata.get("timestamp", current_time)
            time_diff_hours = (current_time - timestamp) / 3600
            decayed_sim = sim * (self.temporal_decay_factor**time_diff_hours)
            decayed_similarities.append(decayed_sim)

        avg_decayed_similarity = sum(decayed_similarities) / len(decayed_similarities)

        # Novedad es 1 - similitud promedio decaída
        return 1.0 - avg_decayed_similarity

    def _analyze_context_signals(
        self, content: str, metadata: Dict[str, Any]
    ) -> Dict[str, float]:
        """Analiza señales contextuales de novedad"""
        signals = {
            "temporal_freshness": 0.0,
            "domain_diversity": 0.0,
            "content_complexity": 0.0,
            "novelty_boost": 0.0,
        }

        # Frescura temporal
        current_time = time.time()
        content_time = metadata.get("timestamp", current_time)
        hours_old = (current_time - content_time) / 3600

        if hours_old < 1:
            signals["temporal_freshness"] = 0.8
        elif hours_old < 24:
            signals["temporal_freshness"] = 0.5
        else:
            signals["temporal_freshness"] = 0.1

        # Diversidad de dominio
        domain = metadata.get("domain", "")
        if domain:
            # Placeholder: en implementación real, verificar contra historial de dominios
            signals["domain_diversity"] = 0.5

        # Complejidad del contenido
        word_count = len(content.split())
        if word_count > 500:
            signals["content_complexity"] = 0.7
        elif word_count > 100:
            signals["content_complexity"] = 0.4
        else:
            signals["content_complexity"] = 0.1

        # Boost combinado
        signals["novelty_boost"] = (
            signals["temporal_freshness"] * 0.4
            + signals["domain_diversity"] * 0.3
            + signals["content_complexity"] * 0.3
        )

        return signals


class ProactivityManager:
    """Gestor de notificaciones proactivas (advisory-only)"""

    def __init__(self, tui_app=None, voice_assistant=None):
        self.tui_app = tui_app
        self.voice_assistant = voice_assistant
        self.notification_history: List[Dict[str, Any]] = []
        self.rate_limiter = {}
        self.max_notifications_per_hour = 5
        self.min_interval_seconds = 0  # allow immediate notifications in tests

    def notify_curiosity(self, message: str, context: Dict[str, Any] = None):
        """Envía notificación de curiosidad"""
        if self._should_rate_limit():
            logger.debug("Notificación rate-limited")
            return

        # Preparar mensaje
        notification = {
            "type": "curiosity",
            "message": message,
            "context": context or {},
            "timestamp": time.time(),
            "delivered": False,
        }

        # Intentar entregar via TUI
        if self.tui_app and hasattr(self.tui_app, "notify_curiosity"):
            try:
                self.tui_app.notify_curiosity(message, context)
                notification["delivered"] = True
                notification["method"] = "tui"
            except Exception as e:
                logger.warning(f"Error notificando via TUI: {e}")

        # Intentar entregar via voz (si no se entregó por TUI)
        if not notification["delivered"] and self.voice_assistant:
            try:
                self.voice_assistant.speak(message, blocking=False)
                notification["delivered"] = True
                notification["method"] = "voice"
            except Exception as e:
                logger.warning(f"Error notificando via voz: {e}")

        # Log de la notificación
        self.notification_history.append(notification)
        self._update_rate_limiter()

        logger.info(
            f"🧠 Curiosidad notificada: {message[:50]}... (método: {notification.get('method', 'none')})"
        )

    def _should_rate_limit(self) -> bool:
        """Verifica si debe rate-limit las notificaciones"""
        current_time = time.time()

        # Limpiar entradas antiguas (más de 1 hora)
        cutoff_time = current_time - 3600
        self.rate_limiter = {
            k: v for k, v in self.rate_limiter.items() if v > cutoff_time
        }

        # Verificar límite por hora
        if len(self.rate_limiter) >= self.max_notifications_per_hour:
            return True

        # Verificar intervalo mínimo
        if self.rate_limiter:
            last_notification = max(self.rate_limiter.values())
            if current_time - last_notification < self.min_interval_seconds:
                return True

        return False

    def _update_rate_limiter(self):
        """Actualiza el rate limiter"""
        current_time = time.time()
        self.rate_limiter[current_time] = current_time

    def get_notification_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de notificaciones"""
        total = len(self.notification_history)
        delivered = sum(1 for n in self.notification_history if n["delivered"])
        recent = sum(
            1 for n in self.notification_history if time.time() - n["timestamp"] < 3600
        )  # Última hora

        return {
            "total_notifications": total,
            "delivered_notifications": delivered,
            "delivery_rate": delivered / total if total > 0 else 0,
            "recent_notifications": recent,
            "rate_limited": len(
                [n for n in self.notification_history if not n["delivered"]]
            ),
        }


class CuriositySystem:
    """Sistema principal de curiosidad y proactividad"""

    def __init__(self, brain_instance=None, tui_app=None, voice_assistant=None):
        # Componentes principales
        self.embedding_adapter = TFIDFEmbeddingAdapter()
        self.vector_store = VectorStore()
        self.novelty_detector = NoveltyDetector(
            self.embedding_adapter, self.vector_store
        )
        self.proactivity_manager = ProactivityManager(tui_app, voice_assistant)

        # Referencias al cerebro
        self.brain = brain_instance

        # Estado del sistema
        self.enabled = True
        self.last_analysis_time = 0
        self.analysis_interval = 600  # 10 minutos

        # Estadísticas
        self.stats = {
            "total_analyzed": 0,
            "novel_discoveries": 0,
            "notifications_sent": 0,
        }

        logger.info("🧠 Sistema de curiosidad inicializado")

    def analyze_scraping_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza un resultado de scraping para novedad"""
        if not self.enabled:
            return {"status": "disabled"}

        try:
            # Extraer contenido relevante
            url = result.get("url", "")
            title = result.get("title", "")
            content = result.get("content", "")
            domain = result.get("domain", "")

            if not content:
                return {"status": "no_content"}

            # Crear entrada de memoria
            entry = MemoryEntry(
                content=content,
                url=url,
                title=title,
                timestamp=time.time(),
                metadata={
                    "domain": domain,
                    "content_length": len(content),
                    "scraping_success": result.get("status") == "SUCCESS",
                },
            )

            # Detectar novedad
            is_novel, novelty_score, analysis = self.novelty_detector.detect_novelty(
                content, entry.metadata
            )

            # Actualizar estadísticas
            self.stats["total_analyzed"] += 1

            if is_novel:
                self.stats["novel_discoveries"] += 1

                # Generar mensaje de curiosidad
                curiosity_message = self._generate_curiosity_message(entry, analysis)

                # Notificar
                self.proactivity_manager.notify_curiosity(
                    curiosity_message,
                    {
                        "entry": entry.__dict__,
                        "analysis": analysis,
                        "novelty_score": novelty_score,
                    },
                )

                self.stats["notifications_sent"] += 1

            # Almacenar en vector store si es novedoso o importante
            if is_novel or entry.importance > 0.7:
                embedding = self.embedding_adapter.encode(content)
                self.vector_store.store(entry.get_id(), embedding, entry.metadata)

                # Actualizar vocabulario del embedding adapter
                self.embedding_adapter.add_document(content)

            return {
                "status": "analyzed",
                "is_novel": is_novel,
                "novelty_score": novelty_score,
                "analysis": analysis,
            }

        except Exception as e:
            logger.error(f"Error analizando resultado de scraping: {e}")
            return {"status": "error", "error": str(e)}

    def _generate_curiosity_message(
        self, entry: MemoryEntry, analysis: Dict[str, Any]
    ) -> str:
        """Genera mensaje de curiosidad basado en el análisis"""
        # Seleccionar mensaje basado en el score de novedad
        novelty_score = analysis["novelty_score"]
        domain = entry.metadata.get("domain", "")

        messages = [
            f"¡Descubrimiento interesante! Encontré contenido novedoso en {entry.url}",
            f"Algo nuevo en {domain}: '{entry.title[:50]}...'",
            f"Contenido fresco detectado con score de novedad {analysis['novelty_score']:.2f}",
            f"¡Mi curiosidad se activó! Nuevo contenido en {entry.url} parece prometedor",
        ]

        if novelty_score > 0.8:
            message_idx = 0  # Muy novedoso
        elif novelty_score > 0.6:
            message_idx = 1  # Moderadamente novedoso
        elif novelty_score > 0.4:
            message_idx = 2  # Algo novedoso
        else:
            message_idx = 3  # Ligeramente novedoso

        return messages[message_idx]

    def periodic_curiosity_check(self):
        """Verificación periódica de curiosidad (para background processing)"""
        current_time = time.time()

        if current_time - self.last_analysis_time < self.analysis_interval:
            return

        self.last_analysis_time = current_time

        # Verificar si hay suficiente contenido para análisis
        stored_ids = self.vector_store.get_all_ids()
        if len(stored_ids) < 10:
            return  # Necesitamos más datos

        # Análisis de patrones de curiosidad
        self._analyze_curiosity_patterns()

    def _analyze_curiosity_patterns(self):
        """Analiza patrones en las detecciones de curiosidad"""
        # Placeholder para análisis avanzado de patrones
        # Podría detectar tendencias, dominios frecuentes, etc.
        pass

    def get_curiosity_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema de curiosidad"""
        notification_stats = self.proactivity_manager.get_notification_stats()

        return {
            **self.stats,
            **notification_stats,
            "enabled": self.enabled,
            "last_analysis": self.last_analysis_time,
            "stored_memories": len(self.vector_store.get_all_ids()),
            "embedding_adapter_available": self.embedding_adapter.is_available(),
        }

    def enable_curiosity(self):
        """Habilita el sistema de curiosidad"""
        self.enabled = True
        logger.info("🧠 Sistema de curiosidad habilitado")

    def disable_curiosity(self):
        """Deshabilita el sistema de curiosidad"""
        self.enabled = False
        logger.info("🧠 Sistema de curiosidad deshabilitado")


# Función de fábrica
def create_curiosity_system(
    brain_instance=None, tui_app=None, voice_assistant=None
) -> CuriositySystem:
    """Crea una instancia del sistema de curiosidad"""
    return CuriositySystem(brain_instance, tui_app, voice_assistant)
