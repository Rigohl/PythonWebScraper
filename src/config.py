"""
Archivo de Configuración Central

Aquí se definen todas las constantes y parámetros para el scraper.
"""

# --- Configuración del Crawler ---
CONCURRENCY = 5
DEFAULT_DELAY = 1  # Segundos de espera entre peticiones por trabajador
MAX_RETRIES = 3
INITIAL_RETRY_BACKOFF_FACTOR = 2  # Segundos. backoff = factor * (2 ** (retry_attempt))

# --- User-Agent y Proxies ---
USER_AGENT = "PythonWebScraperPRO/1.0" # Default User-Agent if not using rotation
USER_AGENT_LIST = [
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
# Menor número = mayor prioridad
CONTENT_TYPE_PRIORITIES = {
    "PRODUCT": 1,
    "BLOG_POST": 2,
    "ARTICLE": 2,
    "GENERAL": 3,
    "UNKNOWN": 4,
}

# --- Configuración de Detección de Anomalías ---
ANOMALY_THRESHOLD_LOW_QUALITY = 0.3  # Porcentaje de páginas de baja calidad para considerar una anomalía (30%)

# --- Configuración de LLM ---
LLM_API_KEY = "YOUR_LLM_API_KEY_HERE" # Reemplazar con tu clave API real

# --- Configuración de RL Agent ---
RL_MODEL_PATH = "models/rl_agent_model.pkl" # Ruta al modelo del agente RL

# --- Configuración del Scraper ---
SCRAPER_VERSION = "0.11.0"
VISUAL_CHANGE_THRESHOLD = 5  # Distancia de Hamming. Menor es más similar. Un valor de 5 es un buen punto de partida.
MIN_CONTENT_LENGTH = 250
FORBIDDEN_PHRASES = [
    "acceso denegado", "enable javascript", "habilite las cookies",
    "acceso restringido", "login required", "please log in"
]
# Tipos de recursos a bloquear para acelerar la carga de la página
BLOCKED_RESOURCE_TYPES = [
  'image', 'stylesheet', 'font', 'media', 'other'
]
RETRYABLE_STATUS_CODES = [429, 500, 502, 503, 504]

# --- Configuración de la Base de Datos ---
DB_PATH = "data/scraper_database.db"

# --- Configuración de la TUI ---
TUI_LOG_PATH = "logs/scraper_run.md"

# --- Esquema de Extracción de Datos (Para Selectores Auto-reparables) ---
# Define qué datos extraer para dominios específicos.
# El scraper usará esto para la extracción y la auto-reparación.
EXTRACTION_SCHEMA = {
    "books.toscrape.com": {
        "price": ".price_color"
    }
}
