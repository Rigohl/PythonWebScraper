import logging
from playwright.async_api import async_playwright
from src.orchestrator import ScrapingOrchestrator
from src.database import DatabaseManager
from src.settings import settings
from src.user_agent_manager import UserAgentManager
from src.llm_extractor import LLMExtractor
from src.rl_agent import RLAgent

async def run_crawler(
    start_urls: list[str],
    db_path: str,
    concurrency: int,
    respect_robots_txt: bool,
    use_rl: bool
):
    """
    Configura y ejecuta el proceso de crawling.
    Esta función contiene la lógica principal del crawler para ser reutilizable.
    """
    logging.info(f"Iniciando crawler con {concurrency} trabajadores para las URLs: {start_urls}")

    # 1. Crear dependencias
    db_manager = DatabaseManager(db_path=db_path)
    user_agent_manager = UserAgentManager(user_agents=settings.USER_AGENT_LIST)
    llm_extractor = LLMExtractor()
    rl_agent = RLAgent(model_path=settings.RL_MODEL_PATH)

    # 2. Gestionar el ciclo de vida de Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # 3. Crear el orquestador e inyectar dependencias
        orchestrator = ScrapingOrchestrator(
            start_urls=start_urls, db_manager=db_manager,
            user_agent_manager=user_agent_manager, llm_extractor=llm_extractor,
            rl_agent=rl_agent, concurrency=concurrency,
            respect_robots_txt=respect_robots_txt, use_rl=use_rl
        )

        # 4. Ejecutar el crawler
        await orchestrator.run(browser=browser)
        await browser.close()
