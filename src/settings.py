from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Dict

class Settings(BaseSettings):
    """
    Gestiona la configuración de la aplicación cargando desde un archivo .env y variables de entorno.
    """
    # --- Configuración del Crawler ---
    CONCURRENCY: int = 5
    DEFAULT_DELAY: int = 1
    MAX_RETRIES: int = 3
    INITIAL_RETRY_BACKOFF_FACTOR: int = 2

    # --- User-Agent y Proxies ---
    USER_AGENT: str = "PythonWebScraperPRO/1.0"
    USER_AGENT_LIST: List[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/109.0.1518.78",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/108.0",
    ]

    # --- Configuración de Prioridades de Contenido ---
    CONTENT_TYPE_PRIORITIES: Dict[str, int] = {
        "PRODUCT": 1,
        "BLOG_POST": 2,
        "ARTICLE": 2,
        "GENERAL": 3,
        "UNKNOWN": 4,
    }

    # --- Configuración de Detección de Anomalías ---
    ANOMALY_THRESHOLD_LOW_QUALITY: float = 0.3

    # --- Configuración de LLM ---
    LLM_API_KEY: str = "YOUR_LLM_API_KEY_HERE"

    # --- Configuración de RL Agent ---
    RL_MODEL_PATH: str = "models/rl_agent_model.pkl"

    # --- Configuración del Scraper ---
    SCRAPER_VERSION: str = "0.11.0"
    VISUAL_CHANGE_THRESHOLD: int = 5
    MIN_CONTENT_LENGTH: int = 250
    FORBIDDEN_PHRASES: List[str] = [
        "acceso denegado", "enable javascript", "habilite las cookies",
        "acceso restringido", "login required", "please log in"
    ]
    BLOCKED_RESOURCE_TYPES: List[str] = [
      'image', 'stylesheet', 'font', 'media', 'other'
    ]
    RETRYABLE_STATUS_CODES: List[int] = [429, 500, 502, 503, 504]

    # --- Configuración de la Base de Datos ---
    DB_PATH: str = "data/scraper_database.db"

    # --- Configuración de la TUI ---
    TUI_LOG_PATH: str = "logs/scraper_run.md"

    # --- Esquema de Extracción de Datos ---
    EXTRACTION_SCHEMA: Dict[str, Dict[str, str]] = {
        "books.toscrape.com": {
            "price": ".price_color"
        }
    }

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

settings = Settings()
