# Web Scraper PRO

Un crawler y archivador web inteligente, diseñado para ser adaptable, resiliente y fácil de usar.

## Prerrequisitos

- Python 3.10 o superior.

## ¿Cómo Empezar? (Método Simple)

### Opción 1: Launcher Unificado (Recomendado)

1. **Ejecutar el launcher principal:**

   **En Windows:**

   ```cmd
   WebScraperPRO.bat
   ```

   **En Linux/macOS:**

   ```bash
   ./WebScraperPRO.sh
   ```

   El launcher te guiará através de un menú interactivo donde podrás:
   - Instalar dependencias automáticamente
   - Ejecutar la interfaz TUI
   - Hacer crawling de URLs específicas
   - Exportar datos
   - Ejecutar tests y más

### Opción 2: Instalación Manual

1. **Instalar Dependencias:**

   ```bash
   pip install -r requirements.txt
   python -m playwright install
   ```

2. **Lanzar la Aplicación:**

   **Interfaz TUI (Recomendado):**

   ```bash
   python -m src.main --tui
   ```

   **Modo Demo (sin Playwright):**

   ```bash
   python -m src.main --demo
   ```

3. **(Opcional) Ejecución por Línea de Comandos (CLI):**
    Para automatización, también puedes ejecutarlo directamente (asegúrate de tener el entorno virtual activado).

    ```bash
    # Ejemplo: Iniciar un crawling desde la CLI (desde la raíz del proyecto)
    python3 -m src.main --crawl http://toscrape.com/
    ```

    Para ver todas las opciones, usa `python3 -m src.main --help`.

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
LLM_API_KEY is read from the environment or a `.env` file. Do NOT hardcode
real API keys in the repository. Create a `.env` file with the key like:

```powershell
setx LLM_API_KEY "sk-..."
```

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
    - **Manejo Inteligente de Cookies y Sesiones:** El sistema ahora persiste y reutiliza cookies por dominio, permitiendo mantener sesiones activas y sortear sistemas de autenticación o límites de acceso, mejorando la resistencia a la detección.
    - **Extracción Dinámica con LLMs (Zero-Shot):** El scraper ahora puede extraer datos estructurados directamente del HTML utilizando un LLM. Los esquemas de extracción se pueden definir dinámicamente por dominio y se almacenan en la base de datos, lo que elimina la necesidad de selectores CSS estáticos y mejora la adaptabilidad del scraper a los cambios en el diseño web.
    - **Alertas y Notificaciones en TUI:** Se ha implementado un sistema de alertas visuales directamente en la Interfaz de Usuario Textual (TUI), notificando al usuario sobre eventos críticos como fallos persistentes, bucles de redirección, problemas de calidad de contenido o cambios visuales significativos en las páginas.
    - **Reintentos Adaptativos con Backoff Exponencial:** El orquestador gestiona los reintentos de forma inteligente. En caso de fallos temporales (como errores de red), aplica un tiempo de espera que aumenta exponencialmente con cada intento, permitiendo al scraper recuperarse de interrupciones sin saturar el servidor objetivo.
    - **Agente de Aprendizaje por Refuerzo (RL) Evolucionado:** Se ha integrado un agente de RL basado en PPO (`stable-baselines3` y `gymnasium`). Este agente, a través del aprendizaje, puede ajustar dinámicamente parámetros de la estrategia de scraping como el factor de backoff, con el objetivo de optimizar el rendimiento y la resistencia a la detección de forma autónoma.
    - **Protección contra Bucles y Trampas:** El sistema detecta y descarta automáticamente URLs que caen en patrones de ruta repetitivos (como calendarios infinitos) o que exceden un número máximo de redirecciones, evitando el consumo inútil de recursos.
6. **Ciclo del Trabajador:**
    - **Extracción de Tarea:** Un trabajador toma una URL de la cola.
    - **Descarga y Análisis:** Usando una instancia de navegador compartida, el trabajador navega a la URL. Si la página falla por un error temporal, la reintentará varias veces. Una vez cargada, la procesa con el `AdvancedScraper` para extraer contenido y **enlaces visibles** (ignorando honeypots).
    - **Limpieza y Extracción Inteligente:** El texto extraído se procesa a través de un módulo de LLM para eliminar "información basura" (menús, pies de página, etc.). Si se ha definido un esquema de extracción para el dominio, el LLM también se utiliza para extraer datos estructurados directamente del HTML.
    - **Validación y Persistencia:** El resultado se valida con `Pydantic`. Antes de guardarlo, se calcula un hash del contenido. Si ya existe una página con el mismo contenido en la base de datos, se marca como `DUPLICATE` para evitar redundancia y procesar enlaces innecesarios. Finalmente, se guarda en la base de datos SQLite.
    - **Descubrimiento:** Si el scraping fue exitoso y no es un duplicado, los enlaces encontrados se analizan. Aquellos que pertenecen al mismo dominio y no han sido vistos antes, se añaden a la cola de trabajo para continuar el ciclo.
7. **Finalización:** El proceso continúa hasta que la cola se vacía y todos los trabajadores están inactivos. En ese momento, el orquestador cierra el navegador y finaliza.

---

## Estructura del Proyecto (Detallado)

- `src/`: **Carpeta Principal del Código Fuente.** Organizada por funcionalidad.
  - `main.py`: **Punto de Entrada.** Parsea argumentos de CLI y lanza la TUI o el crawler.
  - `runner.py`: **Orquestador de Ejecución.** Contiene la lógica para configurar y lanzar una sesión de crawling completa.
  - `settings.py`: Configuración global del proyecto vía `pydantic-settings`.
  - `orchestrator.py`: Gestiona la concurrencia, la cola de tareas y el ciclo de vida del crawling.
  - `scraper.py`: Lógica para descargar y procesar una única página con Playwright.
  - `db/`: **Persistencia de datos.**
    - `database.py`: Abstracción sobre la base de datos SQLite para guardar resultados, cookies, etc.
  - `intelligence/`: **Módulos de IA.**
    - `llm_extractor.py`: Integra LLMs para limpieza y extracción de datos estructurados.
    - `rl_agent.py`: Agente de Aprendizaje por Refuerzo para optimización dinámica.
  - `managers/`: **Gestores de recursos.**
    - `fingerprint_manager.py`: Genera perfiles de navegador para evasión.
    - `user_agent_manager.py`: Rota User-Agents para reducir bloqueos.
  - `models/results.py`: **Modelos de datos Pydantic.** Define la estructura de `ScrapeResult`.
  - `tui/`: **Interfaz de Usuario en Terminal.**
    - `app.py`: Define la aplicación Textual y sus componentes.
    - `styles.css`: Hoja de estilos para la TUI.
- `tests/`: Pruebas unitarias y de integración.
  - `tests/regression_fixtures/`: Contiene archivos HTML de sitios reales para realizar **testing de regresión**, asegurando que la lógica de extracción no se rompa con futuros cambios.
- `requirements.txt`: Lista de todas las dependencias de Python.
- `requirements-dev.txt`: Dependencias para desarrollo (testing, linting).
- `MEJORAS.md`: La hoja de ruta estratégica del proyecto.
- `README.md`: Este mismo archivo.

---

---

## Tabla de Módulos y Propósito

| Módulo/Carpeta         | Propósito Principal |
|------------------------|--------------------|
| src/main.py            | CLI/TUI, entrada principal |
| src/runner.py          | Orquestador de ejecución |
| src/settings.py        | Configuración global |
| src/orchestrator.py    | Lógica de scraping concurrente |
| src/scraper.py         | Descarga y procesamiento de páginas |
| src/db/database.py     | Persistencia y exportación de resultados |
| src/intelligence/      | IA: LLM y RL agent |
| src/managers/          | Gestión de User-Agents y fingerprint |
| src/models/results.py  | Modelos de datos Pydantic |
| src/tui/               | Interfaz de usuario textual |
| tests/                 | Pruebas unitarias/integración |

## Recomendaciones de Desarrollo

- Mantén los tests actualizados en `tests/`.
- Usa `.env` para configuración sensible.
- Documenta nuevas funciones y módulos.
- Ejecuta `pytest` antes de cada despliegue.
- Usa `requirements-dev.txt` para dependencias de desarrollo.
- Revisa `MEJORAS.md` para la hoja de ruta y sugerencias de optimización.

## Funcionalidades Clave

- Scraping concurrente y adaptable.
- Extracción inteligente con LLM (offline por defecto, configurable).
- Agente RL para optimización dinámica.
- Rotación avanzada de User-Agents y evasión de fingerprinting.
- Exportación de resultados a CSV/JSON.
- Interfaz TUI moderna y configurable.
- Sistema de alertas y notificaciones.
- Persistencia robusta en SQLite.
- Cumplimiento ético y robots.txt configurable desde la GUI.

## Buenas Prácticas

- Mantén la raíz del proyecto limpia: solo scripts, configs y docs.
- Los módulos deben estar en `src/` y organizados por funcionalidad.
- Los tests deben estar en `tests/` y cubrir todos los módulos principales.
- Elimina archivos temporales, duplicados y backups antiguos.
- Actualiza el README y la documentación con cada cambio relevante.

## Registro de Cambios

- **2025-08-31**: Auditoría, limpieza y reorganización completa del proyecto. README actualizado.
- **2025-08-28**: Completada la implementación de Extracción de Datos Zero-Shot con LLMs (Tarea A.2).

### Cambios operativos (2025-08-31)

- Reubiqué backups y scripts legacy a `backups/` para limpiar la raíz del repo.
- Añadí `backups/RESTORE_GUIDE.md` y `backups/cleanup_backups.ps1`.

---

## Quick start (actualizado)

- Instalar dependencias (si necesitas usar los scripts legacy):

  - Windows (legacy): `backups\\files\\backup_1-Install-Dependencies.bat`
  - Lanzar scraper (legacy): `backups\\files\\backup_2-Launch-Scraper.bat`

Alternatively, install dependencies manually and run the demo mode:

```powershell
python -m pip install -r requirements.txt
python -m src.main --demo
```

> Nota: Los scripts de instalación y lanzamiento legacy se han movido a `backups/files/` para mantener la raíz del repo más limpia. Revisa `backups/README.md` para más detalles.
