playwright
beautifulsoup4
lxml
requests
httpx
fastapi
uvicorn
python-multipart
SQLAlchemy
alembic
psycopg2-binary
tenacity
loguru
pydantic
python-dotenv
async-timeout
ollama
langchain
langchain-community
langchain-core
langchain-openai
tiktoken
# Web Scraper PRO

Un crawler y archivador web inteligente, diseñado para ser adaptable, resiliente y fácil de usar.

## Prerrequisitos

- Python 3.10 o superior.

## ¿Cómo Empezar?

1. **Instalar Dependencias:**
    Ejecuta el script para crear el entorno virtual e instalar todas las librerías necesarias.

    ```bash
    .\1-Install-Dependencies.bat
    ```

2. **Lanzar la Aplicación:**
    Una vez instaladas las dependencias, ejecuta el scraper a través de su interfaz gráfica de usuario (TUI).

    ```bash
    .\2-Launch-Scraper.bat
    ```

    Esto abrirá una interfaz en tu terminal donde podrás introducir la URL de inicio y configurar los parámetros del crawling.

3. **(Opcional) Ejecución por Línea de Comandos (CLI):**
    Para automatización, también puedes ejecutarlo directamente con `python`.

    ```bash
    # Iniciar un crawling desde la CLI
    .\.venv\Scripts\python.exe src/main.py --crawl http://toscrape.com/
    ```

    Para ver todas las opciones, usa `.\.venv\Scripts\python.exe src\main.py --help`.

---

## Configuración

El proyecto utiliza `pydantic-settings` para gestionar la configuración, lo que permite una gran flexibilidad. La configuración se carga desde las siguientes fuentes, en orden de prioridad:

1. **Variables de entorno del sistema.**
2. **Un archivo `.env`** en la raíz del proyecto.
3. **Valores por defecto** definidos en `src/settings.py`.

Para personalizar tu configuración, simplemente copia el archivo `.env.example` a `.env` y modifica los valores.

```bash
# Ejemplo de contenido para tu archivo .env
CONCURRENCY=10
LLM_API_KEY="sk-xxxxxxxxxxxxxxxxxxxx"
DB_PATH="data/mi_base_de_datos.db"
```

---

## Cómo Funciona (Flujo Detallado)

El proceso de scraping es gestionado por un orquestador concurrente:

1. **Inicio:** El proceso comienza con una o más URLs iniciales.
2. **Cola de Trabajo:** Estas URLs se añaden a una cola de prioridad (`asyncio.PriorityQueue`), dando preferencia a las URLs que probablemente sean más importantes (ej. con menor profundidad de ruta y según el tipo de contenido de la página padre).
3. **Pre-calificación y `robots.txt`:** Antes de encolar una URL, el sistema realiza una petición `HEAD` ultrarrápida para verificar que el tipo y tamaño del contenido son adecuados, descartando archivos grandes o no deseados sin necesidad de abrir un navegador. A continuación, respeta las directivas de `robots.txt` por defecto para un comportamiento ético (opción configurable).
4. **Trabajadores (Workers):** Se lanza un número configurable de "trabajadores" asíncronos. Cada trabajador es una tarea que se ejecuta en un bucle infinito, esperando URLs en la cola.
5. **Inteligencia y Adaptación:** El orquestador integra módulos para:
    - **Rotación de User-Agents:** Gestiona un pool de User-Agents para simular diferentes navegadores y reducir la probabilidad de bloqueo.
    - **Navegación Sigilosa (Stealth):** Gracias a la integración con `playwright-stealth`, cada página se parchea automáticamente para ocultar las huellas típicas de la automatización, superando muchas defensas anti-bot.
    - **Gestión de Huellas Digitales (Fingerprinting):** Más allá del modo sigiloso, el `FingerprintManager` genera perfiles de navegador completos y consistentes. Para cada página, se aplica no solo un User-Agent, sino también un tamaño de viewport y propiedades de JavaScript (como `navigator.platform`) que se corresponden con ese perfil, frustrando las técnicas de fingerprinting avanzadas.
    - **Integración con LLMs:** La arquitectura incluye un `LLMExtractor` que actualmente se usa para limpiar y resumir el contenido extraído, mejorando la calidad de los datos guardados.
    - **Selectores Auto-reparables (Self-Healing):** Si un selector CSS para extraer datos específicos (definido en `config.py`) falla, el scraper busca en su historial el texto del dato extraído previamente y lo localiza en la nueva página, generando un nuevo selector y reportando el evento.
    - **Optimización por RL (WIP):** Se ha diseñado un esqueleto para un agente de Aprendizaje por Refuerzo (`rl_agent.py`) que en el futuro podrá optimizar dinámicamente la estrategia de scraping (retrasos, reintentos, etc.).
    - **Protección contra Bucles:** El sistema detecta y descarta automáticamente URLs que caen en patrones de ruta repetitivos (como calendarios infinitos) o que exceden un número máximo de redirecciones, evitando el consumo inútil de recursos.
6. **Ciclo del Trabajador:**
    - **Extracción de Tarea:** Un trabajador toma una URL de la cola.
    - **Descarga y Análisis:** Usando una instancia de navegador compartida, el trabajador navega a la URL. Si la página falla por un error temporal, la reintentará varias veces. Una vez cargada, la procesa con el `AdvancedScraper` para extraer contenido y **enlaces visibles** (ignorando honeypots).
    - **Limpieza Inteligente:** El texto extraído se procesa a través de un módulo de LLM para eliminar "información basura" como menús, pies de página o anuncios, asegurando que solo se guarde el contenido de alta calidad.
    - **Validación y Persistencia:** El resultado se valida con `Pydantic`. Antes de guardarlo, se calcula un hash del contenido. Si ya existe una página con el mismo contenido en la base de datos, se marca como `DUPLICATE` para evitar redundancia y procesar enlaces innecesarios. Finalmente, se guarda en la base de datos SQLite.
    - **Descubrimiento:** Si el scraping fue exitoso y no es un duplicado, los enlaces encontrados se analizan. Aquellos que pertenecen al mismo dominio y no han sido vistos antes, se añaden a la cola de trabajo para continuar el ciclo.
7. **Finalización:** El proceso continúa hasta que la cola se vacía y todos los trabajadores están inactivos. En ese momento, el orquestador cierra el navegador y finaliza.

---

## Estructura del Proyecto (Detallado)

- `src/`: **Carpeta Principal del Código Fuente.**
  - `src/main.py`: **Punto de Entrada.** Parsea los argumentos de la CLI y decide si lanzar el crawler o la TUI.
  - `src/tui.py`: **Interfaz Gráfica de Usuario (TUI).** Construye y gestiona la interfaz interactiva con `textual`.
  - `src/orchestrator.py`: **El Cerebro del Crawler.** Contiene la clase `ScrapingOrchestrator`, que gestiona la cola de URLs, la concurrencia de los trabajadores y el ciclo de vida del navegador.
  - `src/scraper.py`: Contiene la clase `AdvancedScraper` y el modelo de datos `ScrapeResult` (Pydantic). Encapsula la lógica para descargar, analizar y validar la calidad y estructura de los datos de una sola página.
  - `src/database.py`: Contiene la clase `DatabaseManager`, que gestiona la comunicación con la base de datos SQLite.
  - `src/settings.py`: Módulo de configuración basado en `pydantic-settings` que carga desde variables de entorno y archivos `.env`.
  - `src/user_agent_manager.py`: Gestiona la rotación y el ciclo de vida de los User-Agents.
  - `src/fingerprint_manager.py`: Genera perfiles de navegador completos y consistentes para evasión avanzada.
  - `src/llm_extractor.py`: Integra LLMs para la limpieza y extracción de datos.
  - `src/rl_agent.py`: Esqueleto para un Agente de Aprendizaje por Refuerzo (RL) que optimiza la estrategia de scraping.

- `tests/`: Carpeta que contiene todas las pruebas unitarias y de integración. La suite de pruebas ha sido mejorada y expandida para cubrir más funcionalidades.
- `requirements.txt`: Lista de todas las dependencias de Python.
- `styles.css`: Hoja de estilos para la TUI.
- `MEJORAS.md`: La hoja de ruta estratégica del proyecto.
- `README.md`: Este mismo archivo.
