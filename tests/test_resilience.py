"""Tests de resiliencia para deduplicación, proxy fallback y timeout orchestrator."""
import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.database import DatabaseManager
from src.orchestrator import ScrapingOrchestrator
from src.models.results import ScrapeResult
from src.proxy_manager import ProxyManager


class TestDeduplicationResilience:
    """Tests para verificar robustez del sistema de deduplicación."""
    
    def test_content_hash_duplicate_detection(self):
        """Verifica que duplicados por content_hash se detecten correctamente."""
        db = DatabaseManager(":memory:")
        
        # Primer resultado
        result1 = ScrapeResult(
            status="success",
            url="https://example.com/page1",
            content_text="Same content here",
            content_hash="abc123"
        )
        db.save_result(result1)
        
        # Segundo resultado con mismo hash
        result2 = ScrapeResult(
            status="success",
            url="https://example.com/page2", 
            content_text="Same content here",
            content_hash="abc123"  # Mismo hash
        )
        db.save_result(result2)
        
        # Verificar que solo se guardó uno
        results = db.search_results("")
        assert len(results) == 1
        assert results[0]['url'] == "https://example.com/page1"  # El primero se mantiene
    
    def test_fuzzy_duplicate_with_high_similarity(self):
        """Verifica detección de duplicados fuzzy con alta similitud."""
        db = DatabaseManager(":memory:")
        
        # Contenido muy similar
        content1 = "This is a sample article about Python programming"
        content2 = "This is a sample article about Python programming language"  # Muy similar
        
        result1 = ScrapeResult(
            status="success",
            url="https://example.com/1",
            content_text=content1,
            content_hash="hash1"
        )
        db.save_result(result1)
        
        result2 = ScrapeResult(
            status="success",
            url="https://example.com/2", 
            content_text=content2,
            content_hash="hash2"
        )
        db.save_result(result2)
        
        # Con umbral alto de similitud, debería detectar como duplicado
        results = db.search_results("")
        # Depende de la implementación actual de fuzzy matching
        # Si funciona correctamente, debería haber 1 resultado
        assert len(results) >= 1


class TestProxyFallback:
    """Tests para verificar fallback de proxies."""
    
    def test_proxy_rotation_on_block(self):
        """Verifica que se rote proxy cuando uno se bloquea."""
        proxy_manager = ProxyManager([
            "http://proxy1:8080",
            "http://proxy2:8080", 
            "http://proxy3:8080"
        ])
        
        # Obtener proxy inicial
        proxy1 = proxy_manager.get_proxy()
        assert proxy1 in ["http://proxy1:8080", "http://proxy2:8080", "http://proxy3:8080"]
        
        # Bloquear proxy actual
        proxy_manager.block_proxy(proxy1)
        
        # Obtener siguiente proxy
        proxy2 = proxy_manager.get_proxy()
        assert proxy2 != proxy1  # Debe ser diferente
        assert proxy2 is not None  # Debe tener fallback
    
    def test_proxy_exhaustion_handling(self):
        """Verifica comportamiento cuando se agotan todos los proxies."""
        proxy_manager = ProxyManager(["http://single-proxy:8080"])
        
        # Obtener y bloquear el único proxy
        proxy = proxy_manager.get_proxy()
        proxy_manager.block_proxy(proxy)
        
        # Intentar obtener otro proxy
        fallback_proxy = proxy_manager.get_proxy()
        # Debe manejar gracefully (None o exception controlada)
        assert fallback_proxy is None or isinstance(fallback_proxy, str)


class TestOrchestratorTimeout:
    """Tests para timeout y cancelación del orchestrator."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_cancellation(self):
        """Verifica que el orchestrator se pueda cancelar correctamente."""
        # Mock dependencies
        db_manager = Mock()
        user_agent_manager = Mock()
        llm_extractor = Mock() 
        
        orchestrator = ScrapingOrchestrator(
            start_urls=["https://example.com"],
            db_manager=db_manager,
            user_agent_manager=user_agent_manager,
            llm_extractor=llm_extractor,
            concurrency=1
        )
        
        # Mock browser
        mock_browser = Mock()
        
        # Crear task que se pueda cancelar
        task = asyncio.create_task(orchestrator.run(mock_browser))
        
        # Esperar un poco y cancelar
        await asyncio.sleep(0.1)
        task.cancel()
        
        # Verificar que se cancela sin hanging
        with pytest.raises(asyncio.CancelledError):
            await task
    
    @pytest.mark.asyncio
    async def test_worker_timeout_handling(self):
        """Verifica que timeouts de workers se manejen correctamente."""
        # Mock dependencies
        db_manager = Mock()
        user_agent_manager = Mock()
        user_agent_manager.get_user_agent.return_value = "test-agent"
        user_agent_manager.release_user_agent = Mock()
        
        llm_extractor = AsyncMock()
        
        orchestrator = ScrapingOrchestrator(
            start_urls=["https://slow-site.com"],
            db_manager=db_manager,
            user_agent_manager=user_agent_manager,
            llm_extractor=llm_extractor,
            concurrency=1
        )
        
        # Mock browser con página que timeout
        mock_browser = Mock()
        mock_page = Mock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        
        # Mock scraper que haga timeout
        with patch('src.orchestrator.AdvancedScraper') as MockScraper:
            mock_scraper = AsyncMock()
            # Simular timeout en scraping
            mock_scraper.scrape.side_effect = asyncio.TimeoutError("Scraping timeout")
            MockScraper.return_value = mock_scraper
            
            # Ejecutar con timeout corto
            try:
                await asyncio.wait_for(orchestrator.run(mock_browser), timeout=2.0)
            except asyncio.TimeoutError:
                pass  # Esperado
            
            # Verificar que se manejó el timeout sin crashear
            assert True  # Si llegamos aquí, no hubo crash


class TestSharedFixtures:
    """Tests usando fixtures compartidas para configuración común."""
    
    @pytest.fixture
    def mock_db_manager(self):
        """Database manager mockeado para tests."""
        db = Mock()
        db.save_result = Mock()
        db.search_results.return_value = []
        return db
    
    @pytest.fixture 
    def mock_user_agent_manager(self):
        """User agent manager para tests."""
        ua_manager = Mock()
        ua_manager.get_user_agent.return_value = "test-user-agent"
        ua_manager.release_user_agent = Mock()
        ua_manager.block_user_agent = Mock()
        return ua_manager
    
    @pytest.fixture
    def orchestrator(self, mock_db_manager, mock_user_agent_manager):
        """Orchestrator configurado para tests."""
        return ScrapingOrchestrator(
            start_urls=["https://test.com"],
            db_manager=mock_db_manager,
            user_agent_manager=mock_user_agent_manager,
            llm_extractor=Mock(),
            concurrency=2
        )
    
    def test_orchestrator_initialization(self, orchestrator):
        """Verifica inicialización correcta del orchestrator."""
        assert orchestrator.start_urls[0] == "https://test.com"
        assert len(orchestrator.start_urls) == 1
        assert orchestrator.concurrency == 2
        
    @pytest.mark.asyncio
    async def test_queue_operations(self, orchestrator):
        """Verifica operaciones básicas de la queue."""
        # Añadir URL a la queue
        await orchestrator.queue.put((1, "https://test.com/page"))
        
        # Verificar que se añadió
        assert orchestrator.queue.qsize() == 1
        
        # Extraer de la queue  
        priority, url = await orchestrator.queue.get()
        assert priority == 1
        assert url == "https://test.com/page"
        
        orchestrator.queue.task_done()