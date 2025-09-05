# Architecture Mapping (Draft)

> Estado: Borrador inicial. No modificar lógica del código asociado. Se completará con más detalle tras revisión adicional.

| Módulo | Propósito | Dependencias Entrantes (quién lo importa) | Dependencias Salientes (qué importa) | Side Effects (I/O, red, disco) | Puntos de Extensión / Hooks |
|--------|-----------|-------------------------------------------|--------------------------------------|-------------------------------|-----------------------------|
| `src/orchestrator.py` | Coordina flujo de crawling concurrente, gestión de cola, RL, robots, prequalification y métricas de dominio. | `runner`, TUI (`tui/app.py`) | `asyncio`, `httpx`, `playwright`, `DatabaseManager`, `AdvancedScraper`, `UserAgentManager`, `LLMExtractor`, `RLAgent`, `FrontierClassifier`, `settings` | Red (HEAD/GET, robots.txt), Disco (DB vía manager), CPU (hashes), Mem (colas) | `ScrapingOrchestrator` acepta inyección de `db_manager`, `user_agent_manager`, `llm_extractor`, `rl_agent`, `frontier_classifier`, callbacks de stats/alertas. |
| `src/scraper.py` | Extrae contenido y metadatos de una sola página: cookies, APIs JSON, contenido principal, links, hashes, clasificación. | `orchestrator` | `playwright.Page`, `BeautifulSoup`, `readability.Document`, `html2text`, `imagehash`, `PIL`, `DatabaseManager`, `LLMExtractor`, `settings` | Red (navegación), Disco (DB cookies/APIs), CPU (hash, parse DOM, screenshot) | Inyección de `DatabaseManager`, `LLMExtractor`, `extraction_schema` dinámico. |
| `src/runner.py` | Función helper para inicializar dependencias y lanzar `ScrapingOrchestrator`. | CLI / TUI | `async_playwright`, `DatabaseManager`, `UserAgentManager`, `LLMExtractor`, `RLAgent`, `settings` | Red (lanzar browser headless descarga), Disco (modelo RL) | Posible punto para DI adicional (proxy manager, fingerprint). |
| `src/database.py` | Persistencia SQLite (páginas, APIs, cookies, esquemas LLM) + deduplicación exacta y difusa. | `scraper`, `orchestrator`, export scripts/tests | `dataset`, `json`, `datetime`, `ScrapeResult` | Disco (SQLite), CPU (Jaccard, hashing), Export (CSV/JSON) | Métodos CRUD extensibles; potencial hook para índices adicionales / migraciones. |
| `src/settings.py` | Configuración central vía `BaseSettings` (env / .env). Toggles de features. | Todos los demás | `pydantic_settings` | Lee variables de entorno | Extensión añadiendo nuevos campos y toggles. |
| `src/proxy_manager.py` | Gestión simple de ciclo de vida de proxies. | (Actualmente no referenciado en núcleo) | `random`, `datetime` | N/A | Extender para backoff adaptativo, rotación avanzada. |
| `src/fingerprint_manager.py` | Genera fingerprints (UA + viewport + JS overrides) | Potencial uso futuro (no visto en orchestrator actual) | `dataclasses`, `random`, `UserAgentManager` | N/A | Inyección de PRNG y viewports; ampliar con canvas / WebGL spoofing. |
| `src/rl_agent.py` | Agente RL (PPO o dummy) para ajustar backoff. | `orchestrator`, bridges `intelligence/rl_agent.py` | `stable_baselines3` (opcional), `gymnasium` (opcional), `numpy` | Disco (modelo .zip) | Acciones ampliables (más que backoff), buffer experiencia. |
| `src/llm_extractor.py` | Limpieza, extracción y resumen con LLM con fallback offline determinista. | `scraper`, `orchestrator` | `openai` (opcional), `instructor` (opcional), `pydantic` | Red (si online), CPU (regex) | Inyectar modelo, extender prompts y pipelines de extracción. |
| `src/user_agent_manager.py` | Rotación y bloqueo temporal de User-Agents. | `orchestrator`, `fingerprint_manager` | `datetime` | N/A | Ajustar política de rotación, estrategias de liberación. |
| `src/tui/app.py` | Interfaz textual (Textual) para monitoreo y control del crawler. | Usuario final | `textual`, `runner`, `settings` | Consola (stdout), Disco (logs) | Callbacks `stats_update_callback`, `alert_callback`. |

## Observaciones Iniciales

- Duplicación parcial: Hay dos rutas de `database.py` (`src/database.py` y `src/db/database.py`) y bridges de compatibilidad (`managers`, `intelligence`). Confirmar cuál es canonical (`src/database.py`).
- Orchestrator con responsabilidad amplia (cola, RL, robots, análisis, backoff, dynamic schema). Considerar separar: prequalification, RL, anomaly detection, link filtering.
- Deduplicación fuzzy en DB podría volverse costosa con gran volumen (iteración completa de tabla). Requiere índices y quizá caching de hashes parciales.

> Próximos pasos: completar columnas de dependencias entrantes reales (usar búsqueda inversa), añadir métricas de tamaño de funciones y líneas para smells.
