"""
Pruebas unitarias para el sistema de curiosidad y proactividad
Unit tests for curiosity and proactivity system
"""

import os
import tempfile
import time

import pytest

from src.intelligence.curiosity import (
    CuriositySystem,
    MemoryEntry,
    NoveltyDetector,
    ProactivityManager,
    TFIDFEmbeddingAdapter,
    VectorStore,
    create_curiosity_system,
)


class TestTFIDFEmbeddingAdapter:
    """Pruebas para el adaptador TF-IDF"""

    def test_encode_empty_text(self):
        adapter = TFIDFEmbeddingAdapter()
        vector = adapter.encode("")
        assert vector == []

    def test_encode_single_word(self):
        adapter = TFIDFEmbeddingAdapter()
        adapter.add_document("hello world")
        vector = adapter.encode("hello")
        assert len(vector) > 0
        assert vector[adapter.vocab.get("hello", 0)] > 0

    def test_similarity_identical_vectors(self):
        adapter = TFIDFEmbeddingAdapter()
        adapter.add_document("test document")
        vec1 = adapter.encode("test")
        vec2 = adapter.encode("test")
        similarity = adapter.similarity(vec1, vec2)
        assert similarity == pytest.approx(1.0, abs=0.1)

    def test_similarity_different_vectors(self):
        adapter = TFIDFEmbeddingAdapter()
        adapter.add_document("hello world")
        adapter.add_document("goodbye universe")
        vec1 = adapter.encode("hello")
        vec2 = adapter.encode("goodbye")
        similarity = adapter.similarity(vec1, vec2)
        assert similarity < 0.5

    def test_is_available(self):
        adapter = TFIDFEmbeddingAdapter()
        assert adapter.is_available() is True


class TestVectorStore:
    """Pruebas para el almacén vectorial"""

    def setup_method(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        self.store = VectorStore(self.temp_db.name)

    def teardown_method(self):
        os.unlink(self.temp_db.name)

    def test_store_and_retrieve(self):
        vector = [0.1, 0.2, 0.3]
        metadata = {"test": "data"}
        self.store.store("test_id", vector, metadata)

        results = self.store.retrieve_similar(vector, limit=1)
        assert len(results) == 1
        entry_id, similarity, retrieved_metadata = results[0]
        assert entry_id == "test_id"
        assert similarity == pytest.approx(1.0, abs=0.1)
        assert retrieved_metadata["test"] == "data"

    def test_retrieve_similar_empty_store(self):
        vector = [0.1, 0.2, 0.3]
        results = self.store.retrieve_similar(vector)
        assert results == []

    def test_get_all_ids(self):
        vector = [0.1, 0.2, 0.3]
        self.store.store("id1", vector, {})
        self.store.store("id2", vector, {})

        ids = self.store.get_all_ids()
        assert len(ids) == 2
        assert "id1" in ids
        assert "id2" in ids


class TestNoveltyDetector:
    """Pruebas para el detector de novedad"""

    def setup_method(self):
        self.adapter = TFIDFEmbeddingAdapter()
        self.store = VectorStore(":memory:")
        self.detector = NoveltyDetector(self.adapter, self.store)

    def test_detect_novelty_completely_new(self):
        content = "completamente nuevo contenido"
        is_novel, score, analysis = self.detector.detect_novelty(content)
        assert is_novel is True
        assert score > 0.5
        assert analysis["novelty_score"] == score

    def test_detect_novelty_similar_content(self):
        # Añadir contenido similar primero
        self.adapter.add_document("contenido de prueba")
        self.store.store(
            "test1",
            self.adapter.encode("contenido de prueba"),
            {"timestamp": time.time()},
        )

        # Probar con contenido similar
        content = "contenido de prueba similar"
        is_novel, score, analysis = self.detector.detect_novelty(content)
        assert is_novel is False
        assert score < 0.5

    def test_context_signals_analysis(self):
        content = "contenido de prueba con muchas palabras " * 20
        metadata = {"timestamp": time.time(), "domain": "example.com"}

        _, _, analysis = self.detector.detect_novelty(content, metadata)
        assert "context_signals" in analysis
        signals = analysis["context_signals"]
        assert "temporal_freshness" in signals
        assert "content_complexity" in signals


class TestProactivityManager:
    """Pruebas para el gestor de proactividad"""

    def setup_method(self):
        self.manager = ProactivityManager()

    def test_notify_curiosity_no_handlers(self):
        message = "test message"
        self.manager.notify_curiosity(message)

        stats = self.manager.get_notification_stats()
        assert stats["total_notifications"] == 1
        assert stats["delivered_notifications"] == 0

    def test_rate_limiting(self):
        # Simular múltiples notificaciones rápidas
        for i in range(10):
            self.manager.notify_curiosity(f"message {i}")

        stats = self.manager.get_notification_stats()
        # Debería haber rate limiting
        assert stats["rate_limited"] > 0

    def test_notification_stats(self):
        self.manager.notify_curiosity("test1")
        self.manager.notify_curiosity("test2")

        stats = self.manager.get_notification_stats()
        assert stats["total_notifications"] == 2
        assert "delivery_rate" in stats


class TestCuriositySystem:
    """Pruebas para el sistema completo de curiosidad"""

    def setup_method(self):
        self.system = CuriositySystem()

    def test_initialization(self):
        assert self.system.enabled is True
        assert self.system.embedding_adapter is not None
        assert self.system.vector_store is not None
        assert self.system.novelty_detector is not None
        assert self.system.proactivity_manager is not None

    def test_analyze_scraping_result_no_content(self):
        result = {"url": "http://example.com", "title": "Test"}
        analysis = self.system.analyze_scraping_result(result)
        assert analysis["status"] == "no_content"

    def test_analyze_scraping_result_with_content(self):
        result = {
            "url": "http://example.com",
            "title": "Test Page",
            "content": "Este es un contenido de prueba único y novedoso",
            "domain": "example.com",
            "status": "SUCCESS",
        }

        analysis = self.system.analyze_scraping_result(result)
        assert analysis["status"] == "analyzed"
        assert "is_novel" in analysis
        assert "novelty_score" in analysis

    def test_curiosity_stats(self):
        stats = self.system.get_curiosity_stats()
        assert "total_analyzed" in stats
        assert "novel_discoveries" in stats
        assert "enabled" in stats
        assert stats["enabled"] is True

    def test_enable_disable_curiosity(self):
        self.system.disable_curiosity()
        assert self.system.enabled is False

        self.system.enable_curiosity()
        assert self.system.enabled is True

    def test_disabled_system_analysis(self):
        self.system.disable_curiosity()
        result = {
            "url": "http://example.com",
            "content": "test content",
            "status": "SUCCESS",
        }
        analysis = self.system.analyze_scraping_result(result)
        assert analysis["status"] == "disabled"


class TestMemoryEntry:
    """Pruebas para la entrada de memoria"""

    def test_memory_entry_creation(self):
        entry = MemoryEntry(
            content="test content",
            url="http://example.com",
            title="Test Title",
            timestamp=1234567890.0,
        )

        assert entry.content == "test content"
        assert entry.url == "http://example.com"
        assert entry.novelty_score == 0.5

    def test_memory_entry_id_generation(self):
        entry = MemoryEntry(
            content="test content",
            url="http://example.com",
            title="Test",
            timestamp=1234567890.0,
        )

        entry_id = entry.get_id()
        assert isinstance(entry_id, str)
        assert len(entry_id) > 0
        # ID debería ser consistente
        assert entry.get_id() == entry_id


class TestIntegration:
    """Pruebas de integración"""

    def test_create_curiosity_system(self):
        system = create_curiosity_system()
        assert isinstance(system, CuriositySystem)
        assert system.enabled is True

    def test_full_curiosity_workflow(self):
        system = CuriositySystem()

        # Simular varios resultados de scraping
        results = [
            {
                "url": "http://example1.com",
                "title": "Page 1",
                "content": "Contenido único de la página 1",
                "domain": "example1.com",
                "status": "SUCCESS",
            },
            {
                "url": "http://example2.com",
                "title": "Page 2",
                "content": "Contenido único de la página 2",
                "domain": "example2.com",
                "status": "SUCCESS",
            },
            {
                "url": "http://example1.com",
                "title": "Page 1 Again",
                "content": "Contenido único de la página 1",  # Contenido duplicado
                "domain": "example1.com",
                "status": "SUCCESS",
            },
        ]

        for result in results:
            analysis = system.analyze_scraping_result(result)
            assert analysis["status"] == "analyzed"

        # Verificar estadísticas
        stats = system.get_curiosity_stats()
        assert stats["total_analyzed"] == 3
        assert stats["novel_discoveries"] >= 2  # Al menos 2 descubrimientos novedosos

        # Verificar almacenamiento
        stored_ids = system.vector_store.get_all_ids()
        assert len(stored_ids) >= 2


if __name__ == "__main__":
    pytest.main([__file__])
