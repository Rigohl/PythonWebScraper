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

## Cómo Funciona (Flujo Detallado)

El proceso de scraping es gestionado por un orquestador concurrente:

1. **Inicio:** El proceso comienza con una o más URLs iniciales.
2. **Cola de Trabajo:** Estas URLs se añaden a una cola de prioridad (`asyncio.PriorityQueue`), dando preferencia a las URLs que probablemente sean más importantes (ej. con menor profundidad de ruta y según el tipo de contenido de la página padre).
3. **Comprobación de `robots.txt`:** El scraper respeta las directivas de `robots.txt` por defecto para un comportamiento ético. Esta opción se puede desactivar desde la interfaz.
4. **Trabajadores (Workers):** Se lanza un número configurable de "trabajadores" asíncronos. Cada trabajador es una tarea que se ejecuta en un bucle infinito, esperando URLs en la cola.
5. **Inteligencia y Adaptación:** El orquestador integra módulos para:
    - **Rotación de User-Agents:** Gestiona un pool de User-Agents para simular diferentes navegadores y reducir la probabilidad de bloqueo.
    - **Integración con LLMs:** La arquitectura incluye un `LLMExtractor` que actualmente se usa para limpiar y resumir el contenido extraído, mejorando la calidad de los datos guardados.
    - **Selectores Auto-reparables (Self-Healing):** Si un selector CSS para extraer datos específicos (definido en `config.py`) falla, el scraper busca en su historial el texto del dato extraído previamente y lo localiza en la nueva página, generando un nuevo selector y reportando el evento.
    - **Optimización por RL (WIP):** Se ha diseñado un esqueleto para un agente de Aprendizaje por Refuerzo (`rl_agent.py`) que en el futuro podrá optimizar dinámicamente la estrategia de scraping (retrasos, reintentos, etc.).
6. **Ciclo del Trabajador:**
    - **Extracción de Tarea:** Un trabajador toma una URL de la cola.
    - **Descarga y Análisis:** Usando una instancia de navegador compartida, el trabajador navega a la URL. Si la página falla por un error temporal, la reintentará varias veces. Una vez cargada, la procesa con el `AdvancedScraper` para extraer contenido y **enlaces visibles** (ignorando honeypots).
    - **Limpieza Inteligente:** El texto extraído se procesa a través de un módulo de LLM para eliminar "información basura" como menús, pies de página o anuncios, asegurando que solo se guarde el contenido de alta calidad.
    - **Validación y Persistencia:** El resultado se valida con `Pydantic` y se guarda en la base de datos SQLite, incluyendo metadatos de linaje.
    - **Descubrimiento:** Si el scraping fue exitoso, los enlaces encontrados se analizan. Aquellos que pertenecen al mismo dominio y no han sido vistos antes, se añaden a la cola de trabajo.
7. **Finalización:** El proceso continúa hasta que la cola se vacía y todos los trabajadores están inactivos. En ese momento, el orquestador cierra el navegador y finaliza.

---

## Estructura del Proyecto (Detallado)

- `src/`: **Carpeta Principal del Código Fuente.**
  - `src/main.py`: **Punto de Entrada.** Parsea los argumentos de la CLI y decide si lanzar el crawler o la TUI.
  - `src/tui.py`: **Interfaz Gráfica de Usuario (TUI).** Construye y gestiona la interfaz interactiva con `textual`.
  - `src/orchestrator.py`: **El Cerebro del Crawler.** Contiene la clase `ScrapingOrchestrator`, que gestiona la cola de URLs, la concurrencia de los trabajadores y el ciclo de vida del navegador.
  - `src/scraper.py`: Contiene la clase `AdvancedScraper` y el modelo de datos `ScrapeResult` (Pydantic). Encapsula la lógica para descargar, analizar y validar la calidad y estructura de los datos de una sola página.
  - `src/database.py`: Contiene la clase `DatabaseManager`, que gestiona la comunicación con la base de datos SQLite.
  - `src/user_agent_manager.py`: Gestiona un pool de User-Agents para rotación y evasión de bloqueos.
  - `src/llm_extractor.py`: Módulo para la integración con Modelos de Lenguaje Grandes (LLMs) para extracción de datos y sumarización.
  - `src/rl_agent.py`: Módulo para un Agente de Aprendizaje por Refuerzo (RL) que optimiza la estrategia de scraping.
  - `src/config.py`: Archivo de configuración central.

- `tests/`: Carpeta que contiene todas las pruebas unitarias y de integración. La suite de pruebas ha sido mejorada y expandida para cubrir más funcionalidades.
- `requirements.txt`: Lista de todas las dependencias de Python.
- `styles.css`: Hoja de estilos para la TUI.
- `MEJORAS.md`: La hoja de ruta estratégica del proyecto.
- `README.md`: Este mismo archivo.
