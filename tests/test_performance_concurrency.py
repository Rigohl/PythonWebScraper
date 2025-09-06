import asyncio
import time
from unittest.mock import AsyncMock

import pytest

from src.scraper import AdvancedScraper


class MockBrowserAdapter:
    def __init__(self, delay=0.1):
        self.delay = delay
        self.call_count = 0

    async def get_content(self):
        self.call_count += 1
        await asyncio.sleep(self.delay)  # Simular delay de red
        return f"<html><body>Content {self.call_count}</body></html>"

    async def screenshot(self):
        return b"fake_screenshot"


class MockLLM:
    async def clean_text_content(self, text):
        return f"Cleaned: {text}"

    async def extract_structured_data(self, html, schema):
        return {"title": "Test", "content": "Mock content"}


class MockDB:
    def __init__(self):
        self.results = []

    def save_discovered_api(self, *args):
        pass

    def save_cookies(self, *args):
        pass

    def load_cookies(self, domain):
        return None

    def save_result(self, result):
        self.results.append(result)


@pytest.mark.asyncio
async def test_concurrency_performance_basic():
    """Medir throughput básico con múltiples workers simulados"""
    db = MockDB()
    adapter = MockBrowserAdapter(delay=0.05)  # 50ms delay
    llm = MockLLM()

    scraper = AdvancedScraper(db_manager=db, browser_adapter=adapter, llm_extractor=llm)

    urls = [f"https://example.com/page{i}" for i in range(10)]

    start_time = time.time()

    # Procesar URLs concurrentemente
    tasks = []
    for url in urls:
        task = scraper._process_content(
            url=url,
            full_html=f"<html><body>Test content for {url}</body></html>",
            response=type("Response", (), {"status": 200, "url": url})(),
            extraction_schema=None,
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    end_time = time.time()

    # Verificar que todas las URLs fueron procesadas
    assert len(results) == 10
    assert all(
        isinstance(r, type(results[0])) for r in results
    )  # Todos son ScrapeResult

    # Calcular métricas de rendimiento
    total_time = end_time - start_time
    throughput = len(urls) / total_time

    # Verificar rendimiento mínimo aceptable
    assert throughput > 5.0  # Al menos 5 URLs por segundo
    assert total_time < 5.0  # Menos de 5 segundos total

    print(".2f")
    print(".2f")


@pytest.mark.asyncio
async def test_memory_efficiency_under_load():
    """Verificar que no hay memory leaks bajo carga concurrente"""
    import os

    import psutil

    db = MockDB()
    adapter = MockBrowserAdapter(delay=0.01)  # Delay mínimo
    llm = MockLLM()

    scraper = AdvancedScraper(db_manager=db, browser_adapter=adapter, llm_extractor=llm)

    # Medir memoria inicial
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB

    # Procesar muchas URLs
    urls = [f"https://example.com/page{i}" for i in range(50)]

    tasks = []
    for url in urls:
        task = scraper._process_content(
            url=url,
            full_html=f"<html><body>Content {url}</body></html>",
            response=type("Response", (), {"status": 200, "url": url})(),
            extraction_schema=None,
        )
        tasks.append(task)

    await asyncio.gather(*tasks)

    # Medir memoria final
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory

    # Verificar que el aumento de memoria es razonable (< 50MB)
    assert memory_increase < 50.0, ".2f"
    print(".2f")


@pytest.mark.asyncio
async def test_scalability_with_different_concurrencies():
    """Probar escalabilidad con diferentes niveles de concurrencia"""
    db = MockDB()
    adapter = MockBrowserAdapter(delay=0.02)
    llm = MockLLM()

    scraper = AdvancedScraper(db_manager=db, browser_adapter=adapter, llm_extractor=llm)

    # Probar con diferentes tamaños de batch
    batch_sizes = [5, 10, 20]

    for batch_size in batch_sizes:
        urls = [f"https://example.com/page{i}" for i in range(batch_size)]

        start_time = time.time()

        tasks = []
        for url in urls:
            task = scraper._process_content(
                url=url,
                full_html=f"<html><body>Batch {batch_size} content {url}</body></html>",
                response=type("Response", (), {"status": 200, "url": url})(),
                extraction_schema=None,
            )
            tasks.append(task)

        await asyncio.gather(*tasks)
        end_time = time.time()

        batch_time = end_time - start_time
        throughput = batch_size / batch_time

        # Verificar que el throughput no degrada significativamente
        assert (
            throughput > 2.0
        ), f"Batch {batch_size}: throughput {throughput:.2f} too low"
        print(".2f")
