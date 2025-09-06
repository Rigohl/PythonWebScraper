import asyncio

from playwright.async_api import async_playwright

from src.db.database import DatabaseManager
from src.intelligence.llm_extractor import LLMExtractor
from src.managers.user_agent_manager import UserAgentManager
from src.orchestrator import ScrapingOrchestrator


async def test_orchestrator():
    print("Iniciando prueba del orquestador...")
    db_manager = DatabaseManager(":memory:")
    ua_manager = UserAgentManager(
        user_agents=["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"]
    )
    llm_extractor = LLMExtractor()

    orch = ScrapingOrchestrator(
        start_urls=["https://example.com"],
        db_manager=db_manager,
        user_agent_manager=ua_manager,
        llm_extractor=llm_extractor,
        concurrency=1,
        respect_robots_txt=False,
    )

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            await orch.run(browser)
            print("Prueba completada exitosamente")
        except (RuntimeError, ValueError, TypeError, ConnectionError, OSError) as e:
            print(f"Error: {e}")
            import traceback

            traceback.print_exc()
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_orchestrator())
