# Plan de Acción: Hacia la Inteligencia y la Eficiencia

 Este plan se enfoca en implementar las capacidades de inteligencia, velocidad y experiencia de usuario definidas en la hoja de ruta estratégica.

 ---

## Fase A: Implementación de Inteligencia Estratégica (Fase 4 de `MEJORAS.md`)

 **Objetivo:** Transformar el scraper de una herramienta reactiva a un agente que aprende y se adapta.

- [ ] **A.1: Evolucionar el Agente de Aprendizaje por Refuerzo (RL)**
  - [ ] **A.1.1:** Integrar `stable-baselines3` y `gymnasium` como dependencias.
  - [ ] **A.1.2:** Refactorizar `src/rl_agent.py` para definir un entorno Gym (`ScrapingEnv`) con espacios de estado y acción claros.
  - [ ] **A.1.3:** Implementar un modelo PPO (`stable_baselines3.PPO`) dentro del agente.
  - [ ] **A.1.4:** Implementar la lógica de `learn()` para entrenar el modelo con la tupla `(estado, acción, recompensa, nuevo_estado)`.
  - [ ] **A.1.5:** Añadir persistencia para guardar/cargar el modelo entrenado, permitiendo aprendizaje continuo.

- [ ] **A.2: Implementar Extracción de Datos con LLMs (Zero-Shot)**
  - [ ] **A.2.1:** Integrar la librería `instructor` y `openai`.
  - [ ] **A.2.2:** Reemplazar la lógica simulada en `LLMExtractor` con llamadas reales a la API de OpenAI usando `instructor`.
  - [ ] **A.2.3:** Crear un nuevo flujo de trabajo en el `AdvancedScraper` que acepte un modelo Pydantic como esquema de extracción en lugar de selectores CSS.

- [ ] **A.3: Implementar Priorización Inteligente de la Frontera**
  - [ ] **A.3.1:** Crear un script para generar un dataset de entrenamiento (CSV) a partir de la base de datos existente, etiquetando URLs como "prometedoras" o "no prometedoras".
  - [ ] **A.3.2:** Entrenar un modelo de clasificación simple (`scikit-learn`) con este dataset.
  - [ ] **A.3.3:** Crear un `FrontierClassifier` e integrarlo en la función `_calculate_priority` del orquestador.

 ---

## Fase B: Mejoras de Experiencia de Usuario (TUI) y Velocidad

 **Objetivo:** Proporcionar mayor visibilidad al usuario y optimizar drásticamente el rendimiento.

- [ ] **B.1: Dashboard de Métricas por Dominio (TUI)**
  - [ ] **B.1.1:** Añadir un widget `DataTable` a la pestaña de "Estadísticas" en la TUI.
  - [ ] **B.1.2:** Modificar el `stats_callback` para que el orquestador envíe las `domain_metrics` completas en cada actualización.
  - [ ] **B.1.3:** Poblar y actualizar la `DataTable` en tiempo real para mostrar `backoff_factor`, ratios de fallo, etc., por cada dominio.

- [ ] **B.2: Pre-calificación de URLs con Peticiones `HEAD` (Velocidad)**
  - [ ] **B.2.1:** En el orquestador, dentro de `_add_links_to_queue`, antes de poner una URL en la cola, realizar una petición `HEAD` asíncrona con `httpx`.
  - [ ] **B.2.2:** Inspeccionar las cabeceras `Content-Type` y `Content-Length` y descartar la URL si no cumple con los criterios definidos en `settings.py`.

- [ ] **B.3: Descubrimiento de APIs Ocultas (Velocidad Extrema)**
  - [ ] **B.3.1:** En el `AdvancedScraper`, añadir un listener al evento `response` de la página Playwright (`page.on("response", ...)`)
  - [ ] **B.3.2:** Dentro del listener, filtrar respuestas de tipo `fetch` o `xhr` que sean `application/json`.
  - [ ] **B.3.3:** Guardar la URL de la API y un hash del payload JSON en una nueva tabla de la base de datos, asociada a la página.

 ---

## Fase C: Refinamiento y Robustez del Código Existente

 **Objetivo:** Fortalecer la base del código, mejorar la fiabilidad y la calidad de los datos.

- [ ] **C.1: Testing de Regresión por Dominio**
  - [ ] **C.1.1:** Crear una carpeta `tests/regression_fixtures/` con archivos HTML reales guardados de sitios web objetivo.
  - [ ] **C.1.2:** Crear un nuevo archivo de test (`tests/test_regression.py`) que itere sobre estos fixtures y verifique que la extracción de datos clave no se rompe.

- [ ] **C.2: Protección contra Bucles y Trampas**
  - [ ] **C.2.1:** En el orquestador, implementar un mecanismo para detectar y descartar URLs con patrones de ruta repetitivos.
  - [ ] **C.2.2:** Añadir un contador de redirecciones por URL y descartarla si excede un umbral.

- [ ] **C.3: Gestión de Duplicados por Contenido**
  - [ ] **C.3.1:** Añadir un campo `content_hash: str` al modelo `ScrapeResult`.
  - [ ] **C.3.2:** En `AdvancedScraper`, después de limpiar el texto, calcular un hash SHA256 del `cleaned_text` y asignarlo al resultado.
  - [ ] **C.3.3:** En `DatabaseManager`, antes de `upsert`, comprobar si ya existe un registro con el mismo `content_hash`. Si es así, marcar el resultado como `DUPLICATE` y no seguir sus enlaces.
