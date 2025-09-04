from typing import Dict, List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables and optional
    ``.env`` files. Extends the original project settings by adding sensible
    defaults for any missing keys and exposing additional parameters used by
    downstream modules. A default model name for the LLM is included so the
    ``LLMExtractor`` can operate without requiring users to customise the
    environment.

    Notes
    -----
    - ``LLM_MODEL`` defaults to ``gpt-3.5-turbo``. Override this via the
      environment to experiment with different models (e.g. gpt-4) without
      changing code.
    - ``CONCURRENCY``, ``USER_AGENT_LIST`` and database paths mirror the
      original repository. Feel free to adjust them in your ``.env``.
    """

    # --- Crawler configuration ---
    CONCURRENCY: int = 5
    DEFAULT_DELAY: int = 1
    MAX_RETRIES: int = 3
    INITIAL_RETRY_BACKOFF_FACTOR: int = 2
    REPETITIVE_PATH_THRESHOLD: int = 2
    MAX_REDIRECTS: int = 10
    ALLOWED_CONTENT_TYPES: List[str] = ["text/html", "application/xhtml+xml"]
    PREQUALIFICATION_ENABLED: bool = True
    MAX_CONTENT_LENGTH_BYTES: int = 10_000_000  # 10MB

    # --- User‑Agent and proxies ---
    USER_AGENT: str = "PythonWebScraperPRO/1.0"
    USER_AGENT_LIST: List[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/16.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/16.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Edge/109.0.1518.78",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Firefox/108.0",
    ]

    # --- Content type priorities ---
    CONTENT_TYPE_PRIORITIES: Dict[str, int] = {
        "PRODUCT": 1,
        "BLOG_POST": 2,
        "ARTICLE": 2,
        "GENERAL": 3,
        "UNKNOWN": 4,
    }

    # --- Anomaly detection configuration ---
    ANOMALY_THRESHOLD_LOW_QUALITY: float = 0.3
    # --- Deduplication / fuzzy matching ---
    # Jaccard similarity threshold used by the fuzzy deduplication routine in DatabaseManager
    DUPLICATE_SIMILARITY_THRESHOLD: float = 0.6

    # --- LLM configuration ---
    # LLM API key should be provided via environment variables or a secure
    # secrets manager. Default to None to avoid accidental check-ins of keys.
    LLM_API_KEY: Optional[str] = None
    # Name of the LLM model to call. Required by ``LLMExtractor``. Defaults to
    # gpt‑3.5‑turbo for broad compatibility. You can override this in your
    # environment or ``.env`` file.
    LLM_MODEL: str = "gpt-3.5-turbo"

    # --- Feature / Policy Toggles ---
    # By default we want a fast, fully local scraper experience, so all
    # potentially restrictive / external‑call features start disabled.
    ROBOTS_ENABLED: bool = False  # Respect robots.txt if True
    ETHICS_CHECKS_ENABLED: bool = (
        False  # Placeholder for future ethical / compliance filters
    )
    OFFLINE_MODE: bool = (
        True  # If True, never call remote LLM APIs even if keys are present
    )
    # Accelerated test mode (skips network HEAD prequalification & long stealth)
    FAST_TEST_MODE: bool = False

    # --- RL Agent configuration ---
    RL_MODEL_PATH: str = "models/rl_agent_model.pkl"

    # --- Scraper configuration ---
    SCRAPER_VERSION: str = "0.11.0"
    VISUAL_CHANGE_THRESHOLD: int = 5
    # Reduce for test fixtures which contain short HTML bodies
    MIN_CONTENT_LENGTH: int = 20
    FORBIDDEN_PHRASES: List[str] = [
        "acceso denegado",
        "enable javascript",
        "habilite las cookies",
        "acceso restringido",
        "login required",
        "please log in",
    ]
    BLOCKED_RESOURCE_TYPES: List[str] = [
        "image",
        "stylesheet",
        "font",
        "media",
        "other",
    ]
    RETRYABLE_STATUS_CODES: List[int] = [429, 500, 502, 503, 504]

    # --- Database configuration ---
    DB_PATH: str = "data/scraper_database.db"

    # --- TUI configuration ---
    TUI_LOG_PATH: str = "logs/scraper_run.md"

    # --- Extraction schema (legacy) ---
    EXTRACTION_SCHEMA: Dict[str, Dict[str, str]] = {
        "books.toscrape.com": {
            "price": ".price_color",
        },
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
