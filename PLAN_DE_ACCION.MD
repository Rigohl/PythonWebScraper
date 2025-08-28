# Plan de Acción: Hacia la Inteligencia y la Eficiencia

Este plan se enfoca en implementar las capacidades de inteligencia, velocidad y experiencia de usuario definidas en la hoja de ruta estratégica.

---

## Fase A: Implementación de Inteligencia Estratégica (Fase 4 de `MEJORAS.md`)

**Objetivo:** Transformar el scraper de una herramienta reactiva a un agente que aprende y se adapta.

- [x] **A.1: Evolucionar el Agente de Aprendizaje por Refuerzo (RL)**
  - [x] **A.1.1:** Integrar `stable-baselines3` y `gymnasium` como dependencias.
  - [x] **A.1.2:** Refactorizar `src/rl_agent.py` para definir un entorno Gym (`ScrapingEnv`) con espacios de estado y acción claros.
  - [x] **A.1.3:** Implementar un modelo PPO (`stable_baselines3.PPO`) dentro del agente.
  - [x] **A.1.4:** Implementar la lógica de `learn()` para entrenar el modelo con la tupla `(estado, acción, recompensa, nuevo_estado)`.
  - [x] **A.1.5:** Añadir persistencia para guardar/cargar el modelo entrenado, permitiendo aprendizaje continuo.

- [x] **A.2: Implementar Extracción de Datos con LLMs (Zero-Shot)**
  - [x] **A.2.1:** Integrar la librería `instructor` y `openai`.
  - [x] **A.2.2:** Reemplazar la lógica simulada en `LLMExtractor` con llamadas reales a la API de OpenAI usando `instructor`.
<<<<<<< HEAD
  - [x] **A.2.3:** Crear un nuevo flujo de trabajo en el `AdvancedScraper` que acepte un modelo Pydantic como esquema de extracción en lugar de selectores CSS.
=======
  - [x] **A.2.3:** Crear un nuevo flujo de trabajo en el `AdvancedScraper` que acepte un modelo Pydantic como esquema de extracción en lugar de selectores CSS. Se utiliza la carga dinámica de esquemas por dominio desde la base de datos.

>>>>>>> 0de5c87742ffc6142484400e9bc02c49b4faaab3

- [x] **A.3: Implementar Priorización Inteligente de la Frontera**
  - [x] **A.3.1:** Crear un script (`scripts/generate_frontier_dataset.py`) para generar un dataset de entrenamiento (CSV) a partir de la base de datos existente.
  - [x] **A.3.2:** Crear un script (`scripts/train_frontier_classifier.py`) para entrenar un modelo de clasificación simple (`scikit-learn`) con este dataset y guardarlo.
  - [x] **A.3.3:** Crear una clase `FrontierClassifier` e integrarla en la función `_calculate_priority` del orquestador para usar el modelo.

---

## Fase B: Mejoras de Experiencia de Usuario (TUI) y Velocidad

<<<<<<< HEAD
=======

**Objetivo:** Proporcionar mayor visibilidad al usuario y optimizar drásticamente el rendimiento.

>>>>>>> 0de5c87742ffc6142484400e9bc02c49b4faaab3

- [x] **B.1: Dashboard de Métricas por Dominio (TUI)**
- [x] **B.2: Pre-calificación de URLs con Peticiones `HEAD` (Velocidad)**
- [x] **B.3: Descubrimiento de APIs Ocultas (Velocidad Extrema)**

- [x] **B.4: Mecanismo de Alertas y Notificaciones (TUI)**
  - [x] **B.4.1:** Se ha creado una nueva clase `AlertsDisplay` en `src/tui.py` que contiene un widget `Log` para mostrar alertas críticas.
  - [x] **B.4.2:** `AlertsDisplay` se ha integrado en la composición de `ScraperTUIApp`.
  - [x] **B.4.3:** Se ha añadido un método `alert_callback` a `ScraperTUIApp` para que el orquestador pueda enviar mensajes de alerta y su nivel (warning, error).
  - [x] **B.4.4:** El `alert_callback` se pasa al constructor de `ScrapingOrchestrator` y se utiliza en puntos críticos de `_worker`, `_check_for_anomalies`, `_check_for_visual_changes`, `_has_repetitive_path`, `_prequalify_url`, y `run` para notificar al usuario.

---

## Fase C: Refinamiento y Robustez del Código Existente

**Objetivo:** Fortalecer la base del código, mejorar la fiabilidad y la calidad de los datos.

- [x] **C.1: Reintentos Adaptativos con Backoff Exponencial**
  - [x] **C.1.1:** La lógica de reintentos con backoff exponencial ya está implementada en el método `_worker` de `ScrapingOrchestrator`. En caso de `NetworkError`, el worker espera un tiempo que aumenta exponencialmente con cada intento fallido, multiplicado por un factor de backoff dinámico por dominio, antes de reintentar el scrapeo de la URL.

- [x] **C.2: Testing de Regresión por Dominio**
  - [x] **C.2.1:** Se ha creado la carpeta `tests/regression_fixtures/` con un fixture HTML de ejemplo (`toscrape_com_book.html`).
  - [x] **C.2.2:** Se ha creado un nuevo archivo de test (`tests/test_regression.py`) que itera sobre el fixture y verifica que la extracción de datos con LLM (simulada) funciona como se espera, previniendo futuras roturas.

- [x] **C.3: Protección contra Bucles y Trampas**
  - [x] **C.3.1:** En el orquestador, implementar un mecanismo para detectar y descartar URLs con patrones de ruta repetitivos.
  - [x] **C.3.2:** Añadir un contador de redirecciones por URL y descartarla si excede un umbral.

- [x] **C.4: Gestión de Duplicados por Contenido**
  - [x] **C.4.1:** Añadir un campo `content_hash: str` al modelo `ScrapeResult`.
  - [x] **C.4.2:** En `AdvancedScraper`, después de limpiar el texto, calcular un hash SHA256 del `cleaned_text` y asignarlo al resultado.
  - [x] **C.4.3:** En `DatabaseManager`, antes de `upsert`, comprobar si ya existe un registro con el mismo `content_hash`. Si es así, marcar el resultado como `DUPLICATE` y no seguir sus enlaces.

- [x] **C.5: Manejo Inteligente de Cookies y Sesiones**
  - [x] **C.5.1:** Se ha añadido una tabla `cookies` a `src/database.py` con métodos `save_cookies(domain, cookies_json)` y `load_cookies(domain)`.
  - [x] **C.5.2:** En `src/scraper.py`, antes de navegar a una URL, se cargan las cookies asociadas a su dominio desde la base de datos y se añaden a la instancia de Playwright `page.context`.
  - [x] **C.5.3:** Después de un scraping exitoso, las cookies de la página actual se recuperan y se guardan en la base de datos para su futura reutilización.
