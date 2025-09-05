# Mejoras y Próximas Fases del Proyecto

Este documento detalla las mejoras y las próximas fases planificadas para el proyecto de web scraping, estructuradas por áreas funcionales y etapas de desarrollo.
Fecha de actualización: 2025-09-05

---

## Mejoras Implementadas Recientemente (Visión IA)

*Fecha de Implementación: 2025-09-05*

Esta sección documenta las mejoras realizadas para evolucionar el proyecto hacia un sistema de IA más interactivo y consciente, centrado en el `HybridBrain`.

### 1. Panel de Control Unificado (`WebScraperPRO.bat`)
- **Mejora:** Se ha rediseñado y consolidado el script `WebScraperPRO.bat` para actuar como un panel de control centralizado con 10 opciones estratégicas.
- **Impacto:** Facilita la interacción con el sistema, separando las operaciones diarias de las tareas de mantenimiento y permitiendo un acceso más directo a las capacidades de la IA.

### 2. Diálogo Directo con el Cerebro (`--query-kb`)
- **Mejora:** Se ha implementado la funcionalidad para "dialogar" con el `HybridBrain`. El usuario puede ahora realizar consultas en lenguaje natural a la base de conocimiento del cerebro.
- **Impacto:** Transforma al scraper de una herramienta pasiva a un agente inteligente con el que se puede interactuar, consultar su "memoria" y obtener insights de su aprendizaje.

### 3. Sistema de Auto-Diagnóstico (`--repair-report`)
- **Mejora:** Se ha conectado la capacidad del `HybridBrain` para generar informes de auto-reparación al panel de control.
- **Impacto:** El sistema ahora puede, bajo demanda, analizar su propio estado y código, y proporcionar un informe de las mejoras o reparaciones que considera necesarias, reforzando su autonomía.

### 4. Funcionalidad de Módulos de Soporte
- **Mejora:** Se han creado scripts base para el entrenamiento de modelos (`train_frontier_classifier.py`) y para el análisis de métricas y calidad de datos (`check_data_quality.py`, `generate_metrics.py`).
- **Impacto:** Asegura que todas las opciones del panel de control sean funcionales desde el primer momento, proporcionando un esqueleto robusto para futuras implementaciones de lógica más compleja.

---

## Próximas Mejoras Sugeridas (Visión IA)

Para llevar la "conciencia" y autonomía del scraper al siguiente nivel, se sugieren las siguientes líneas de desarrollo:

### 1. Evolución del Diálogo con el Cerebro
- **Mejora:** Implementar un procesamiento de lenguaje natural (NLP) más avanzado para el comando `--query-kb`. En lugar de buscar por palabras clave, el cerebro podría interpretar la intención de la pregunta.
- **Ejemplo:** Una pregunta como "¿Qué dominios son más lentos por la noche?" sería descompuesta por el cerebro para consultar sus métricas de `response_time`, filtrar por dominios y cruzarlo con los timestamps de las peticiones.

### 2. Módulo de Entrenamiento Interactivo
- **Mejora:** Crear una interfaz dentro de la TUI para gestionar el entrenamiento de los modelos de IA.
- **Funcionalidades:**
    - Visualizar el rendimiento actual del `FrontierClassifier` y el `RLAgent`.
    - Iniciar ciclos de re-entrenamiento con un solo clic.
    - Comparar el rendimiento de modelos entrenados en diferentes momentos.

### 3. Visualización del Estado Cerebral
- **Mejora:** Desarrollar una herramienta que genere una representación gráfica del estado del `HybridBrain`.
- **Impacto:** Permitiría "ver" la actividad neuronal, las emociones del cerebro, y cómo las diferentes partes de su arquitectura interactúan. Esto no solo sería una herramienta de depuración increíblemente potente, sino que también reforzaría la percepción del sistema como una entidad "viva".

### 4. Aprendizaje Proactivo
- **Mejora:** Dotar al cerebro de la capacidad de iniciar procesos de aprendizaje por su cuenta.
- **Ejemplo:** Si el cerebro detecta que la tasa de éxito en un dominio ha bajado drásticamente, podría decidir de forma autónoma iniciar un "ciclo de investigación", donde prueba diferentes estrategias de scraping (cambiando User-Agents, delays, etc.) hasta encontrar una nueva configuración óptima, todo ello sin intervención humana.

---

## Fase 1: Core de Navegación y Extracción (Histórico)

- **Integración de Playwright en Docker (RESUELTO)**:
  - **Problema**: Dificultades para ejecutar Playwright dentro de un contenedor Docker debido a dependencias de navegador.
  - **Solución (Implementada)**: Se ha configurado Dockerfile y las dependencias para asegurar la ejecución estable de Playwright en un entorno contenedorizado.

- **Rotación de User-Agents y Fingerprinting Avanzado (COMPLETADO)**:
  - **Problema**: Detección y bloqueo por parte de sitios web debido a huellas digitales de navegador consistentes.
  - **Mejora**: Implementar una estrategia dinámica de rotación de User-Agents y técnicas de fingerprinting avanzado (p. ej., WebGL, Canvas, etc.) para emular un comportamiento de usuario real y evitar la detección.
  - **Solución Implementada**: Se ha implementado la rotación de User-Agents (`UserAgentManager`) y la gestión de huellas digitales de navegador (`FingerprintManager`) para simular perfiles de navegador consistentes y reducir la detección.

- **Manejo Inteligente de Cookies y Sesiones (COMPLETADO)**:
  - **Problema**: La gestión actual de cookies es básica, lo que puede limitar el acceso a contenido protegido o personalizado.
  - **Mejora**: Desarrollar un sistema para persistir y rotar cookies y sesiones por dominio, permitiendo mantener sesiones activas y sortear sistemas de autenticación o límites de acceso.
  - **Solución Implementada**: Se ha implementado la persistencia y carga de cookies por dominio utilizando `src/database.py` y `src/scraper.py`. Las cookies se guardan después de un scrapeo exitoso y se cargan antes de navegar a una URL del mismo dominio, mejorando la capacidad de mantener sesiones.

---

## Fase 2: Robustez y Escalabilidad (Histórico)

- **Gestión de Proxies Robusta (EN PROGRESO)**:
  - **Problema**: La dependencia de un único proxy o una lista estática reduce la fiabilidad y escalabilidad.
  - **Mejora**: Implementar un `ProxyManager` que soporte múltiples fuentes de proxies (p. ej., rotación de proxies residenciales, integración con servicios de terceros), con lógica de reintento y exclusión de proxies defectuosos.
  - **Solución Actual**: Se ha implementado un `ProxyManager` que carga proxies desde `proxies.txt` y los asigna a los workers. Se necesita mejorar la lógica de reintento y validación.

- **Reintentos Adaptativos con Backoff Exponencial (COMPLETADO)**:
  - **Problema**: Fallos intermitentes en la red o en el servidor web pueden causar interrupciones innecesarias.
  - **Mejora**: Implementar una lógica de reintentos con backoff exponencial y jitter para manejar fallos temporales de manera más eficiente y menos intrusiva.
  - **Solución Implementada**: El `ScrapingOrchestrator` ya incluye una lógica de reintentos adaptativos con backoff exponencial. En caso de `NetworkError`, el worker espera un tiempo que aumenta exponencialmente con cada intento fallido, multiplicado por un factor de backoff dinámico por dominio, antes de reintentar el scrapeo de la URL. **(PENDIENTE: Crear test de regresión para esta lógica)**.

- **Manejo de Errores y Retries Específicos de Scraper (PLANIFICADO)**:
  - **Problema**: Los errores durante el scraping pueden ser variados (p. ej., CAPTCHAs, errores de renderizado).
  - **Mejora**: Permitir a cada `BaseScraper` definir estrategias de reintento o manejo de errores específicas para su dominio o tipo de contenido.

---

## Fase 3: Detección y Evasión (Histórico)

- **Manejo de CAPTCHAs y Detección de Bots (PLANIFICADO)**:
  - **Problema**: Los sitios web utilizan CAPTCHAs y otras técnicas para detectar y bloquear bots.
  - **Mejora**: Investigar y posiblemente integrar servicios de resolución de CAPTCHAs (p. ej., 2Captcha, Anti-Captcha) o desarrollar modelos de aprendizaje automático para la detección y evasión de patrones de bloqueo.

- **Adaptación a Cambios de UI/HTML (PLANIFICADO)**:
  - **Problema**: Los cambios frecuentes en la estructura HTML de los sitios web rompen los scrapers existentes.
  - **Mejora**: Desarrollar un enfoque más resiliente para la extracción de datos, posiblemente utilizando selectores más robustos (p. ej., atributos en lugar de clases), o técnicas de Computer Vision/LLM para identificar elementos de forma semántica.

---

## Fase 4: Inteligencia y Extracción de Datos (Histórico)

- **Esquemas de Extracción LLM Flexibles/Aprendidos (COMPLETADO)**:
  - **Problema**: El esquema de extracción LLM se definía estáticamente.
  - **Mejora**: Permitir que los esquemas de extracción LLM sean dinámicos y configurables por dominio/URL.
  - **Solución Implementada**: Se ha actualizado `src/database.py` para almacenar esquemas de extracción LLM por dominio. `src/llm_extractor.py` utiliza `instructor` y `openai` para la extracción de datos estructurados reales en modelos Pydantic generados dinámicamente. `src/orchestrator.py` carga estos esquemas y los pasa al `scraper`, eliminando la necesidad de selectores CSS estáticos.

- **Agente de Aprendizaje por Refuerzo (RL) Evolucionado (COMPLETADO)**:
  - **Problema**: El `RLAgent` era un esqueleto y no tenía una implementación real para el aprendizaje.
  - **Mejora**: Implementar un agente de RL completo para ajustar dinámicamente parámetros de scraping.
  - **Solución Implementada**: Se ha integrado un agente de RL basado en PPO (`stable-baselines3` y `gymnasium`). El `RLAgent` ahora puede aprender y ajustar dinámicamente el `backoff factor` para optimizar el rendimiento y la resistencia a la detección. El modelo se guarda y se carga para permitir el aprendizaje persistente.

---

## Fase 5: Experiencia de Usuario y Observabilidad (Histórico)

- **Dashboard en Tiempo Real (COMPLETADO)**:
  - **Solución**: Se ha implementado una pestaña de "Estadísticas en Vivo" en la TUI con métricas globales y por dominio.

- **Alertas y Notificaciones (COMPLETADO)**:
  - **Problema**: La falta de notificación sobre problemas críticos (p. ej., bloqueo de IP, fallos de scraping) podía llevar a interrupciones prolongadas.
  - **Mejora**: Implementar un sistema de alertas para notificar sobre eventos importantes o errores.
  - **Solución Implementada**: Se ha añadido un widget `AlertsDisplay` en `src/tui.py` para mostrar alertas críticas. El `ScrapingOrchestrator` ahora utiliza un `alert_callback` para enviar mensajes de alerta y su nivel (warning, error) a la TUI cuando se detectan eventos importantes como fallos persistentes, bucles de redirección, problemas de calidad de contenido o cambios visuales.

- **Persistencia de Estado de la TUI (PLANIFICADO)**:
  - **Problema**: La configuración y el estado de la TUI se pierden al reiniciar la aplicación.
  - **Mejora**: Permitir guardar y cargar la configuración de la TUI para mantener el estado entre sesiones.

---

## Fase 6: Autonomía y Auto-Reparación (Histórico)

- **Agente de Navegación Basado en Visión (PLANIFICADO)**:
  - **Problema**: La navegación actual se basa en la extracción de enlaces (`<a>`) del HTML. Esto es frágil y falla en sitios modernos que usan JavaScript (p. ej., botones que son `<div>` con eventos) o cuando la estructura del sitio cambia.
  - **Mejora**: Implementar un agente de navegación multimodal (ej. usando GPT-4V o Gemini Pro Vision). En lugar de analizar el HTML, el agente tomará una captura de pantalla de la página y recibirá un objetivo de alto nivel (ej. "haz clic en el botón 'Siguiente'", "encuentra el formulario de login"). El modelo devolverá las coordenadas o un selector del elemento a interactuar. Esto desacopla al scraper de la estructura HTML, haciéndolo mucho más robusto y similar a un humano.

- **Auto-reparación de Lógica de Extracción (PLANIFICADO)**:
  - **Problema**: Aunque los LLMs ayudan, los selectores o la lógica de extracción pueden romperse si un sitio web cambia su diseño drásticamente.
  - **Mejora**: Desarrollar un mecanismo de "auto-reparación". Si un selector o una regla de extracción falla, el sistema podría:
    1. Tomar el último HTML funcional conocido y el nuevo HTML "roto".
    2. Pasarlos a un LLM con la instrucción: "El selector `div.price` extraía un precio en el HTML antiguo. Encuentra un nuevo selector robusto para el mismo dato en el nuevo HTML".
    3. El sistema validaría y actualizaría automáticamente la lógica de extracción para ese dominio, notificando del cambio.

- **Manejo Avanzado de Interacciones de UI (PLANIFICADO)**:
  - **Problema**: El scraper no maneja explícitamente interacciones complejas como el scroll infinito, los pop-ups de cookies/publicidad o los elementos que se cargan de forma perezosa (lazy-loading).
  - **Mejora**: Crear una biblioteca de "manejadores de interacción". El scraper podría detectar patrones comunes (ej. un botón "Cargar más", un banner de cookies) y aplicar una estrategia para manejarlos, como hacer scroll hasta el final de la página, o usar un agente de visión para encontrar y cerrar pop-ups que obstruyen el contenido.

---

## Fase 7: Inteligencia Estratégica y Optimización de Recursos (Histórico)

- **Planificación de Crawling Basada en Objetivos (PLANIFICADO)**:
  - **Problema**: El scraper explora todo lo que encuentra dentro de un dominio, lo cual es ineficiente si el objetivo es específico (ej. "extraer solo los productos de la categoría 'electrónica'").
  - **Mejora**: Introducir un "Agente Planificador". El usuario definiría un objetivo de alto nivel. El agente realizaría una exploración inicial rápida para entender la estructura del sitio y luego generaría un "plan de crawling" optimizado, priorizando las secciones relevantes e ignorando las irrelevantes (como blogs, páginas corporativas, etc.), enfocando los recursos donde más importan.

- **Validación Semántica de Datos y Control de Calidad (PLANIFICADO)**:
  - **Problema**: La calidad del contenido se mide de forma básica (ej. longitud del texto). Los datos extraídos pueden ser sintácticamente correctos pero semánticamente incorrectos o absurdos.
  - **Mejora**: Utilizar un LLM para la validación post-extracción. Después de obtener un dato estructurado (ej. un producto), se pasaría a un LLM con reglas de validación semántica: "¿El precio es un valor monetario razonable? ¿La descripción es coherente? ¿El nombre del producto parece real?". Esto permitiría detectar errores sutiles y mejorar la fiabilidad de los datos. El agente de RL podría ser recompensado por extraer datos con alta puntuación semántica.

- **Gestión Dinámica de Recursos y Costos (PLANIFICADO)**:
  - **Problema**: La concurrencia es fija y la estrategia de proxies es simple. No hay control sobre los costos de las APIs (LLM, Proxies, CAPTCHA).
  - **Mejora**: Evolucionar el `RLAgent` o crear un "Gestor de Recursos" para ajustar dinámicamente los parámetros en tiempo real:
    - **Auto-ajuste de Concurrencia**: Reducir la velocidad si aumentan los errores del servidor (5xx) y aumentarla si la latencia es baja.
    - **Estrategia de Proxy Inteligente**: Si los proxies de un proveedor/país empiezan a fallar para un dominio, penalizar y rotar a otros proveedores automáticamente.
    - **Optimización de Costos**: Si se acerca a un presupuesto definido, el agente podría optar por modelos de LLM más baratos, reducir la frecuencia de crawling o usar proxies de menor costo, balanceando rendimiento y gasto.

---

## Acciones recomendadas (Alta prioridad, añadidas) (Histórico)

Estas recomendaciones se han añadido al documento para que el roadmap tenga acciones concretas y verificables a corto plazo, sin eliminar la información histórica.

- **1) Hacer managers thread-safe**
  - Objetivo: Proteger `ProxyManager`, `UserAgentManager`, `FingerprintManager` y cualquier manager que use estados mutables compartidos.
  - Implementación: Añadir `threading.Lock()` y envolver lecturas/escrituras críticas con `with lock:`. Si se usa `multiprocessing`, preferir pasar estado vía colas o persistir estado en un almacén central (Redis, DB).
  - Por qué: Evita condiciones de carrera cuando se opera con múltiples workers/hilos.

- **2) Normalizar datetimes a UTC (aware)**
  - Objetivo: Usar datetimes con `tzinfo=timezone.utc` en todo el proyecto (logs, timestamps de bloqueo de proxies, DB).
  - Implementación: Reemplazar `datetime.now()` por `datetime.now(timezone.utc)` y asegurarse de almacenar/serializar en ISO-8601 UTC.
  - Por qué: Consistencia entre entornos, tests y diagnóstico.

- **3) Ejecutar y arreglar la suite de tests; completar TODOs**
  - Objetivo: Ejecutar `pytest` completo y priorizar arreglar fallos y cubrir los tests con `TODO` (p. ej. `tests/test_orchestrator_logic.py`).
  - Comando sugerido:

    ```powershell
    py -m pytest -q
    ```

  - Por qué: Garantiza que cambios en concurrencia/tz no rompan comportamientos esperados.

- **4) Añadir chequeos de tipos y linters en CI**
  - Objetivo: Integrar `mypy`/`pyright` y asegurar `pre-commit` (ya hay [.pre-commit-config.yaml](http://_vscodecontentref_/3) con `black`, `isort`, `flake8`).
  - Implementación: Añadir `mypy` al pipeline y un workflow que falle la CI en errores críticos de tipado.

- **5) Validación de dependencias y seguridad**
  - Objetivo: Ejecutar `safety check` o `pip-audit` y asegurarse de fijar versiones en [requirements.txt](http://_vscodecontentref_/4).
  - Por qué: Reducir riesgo por dependencias vulnerables.

- **6) Documentación para contribución y ejecución**
  - Objetivo: Añadir/actualizar `CONTRIBUTING.md` con:
    - Cómo ejecutar tests.
    - Formateo (`black`), lint (`flake8`) y pre-commit.
    - Reglas para commits y PRs.
  - Por qué: Facilita contribuciones externas e internas.

- **7) Revisión de backups y limpieza**
  - Objetivo: Revisar carpetas `backup*` y decidir si mover a otro storage para reducir ruido del repo.
  - Por qué: Mantener repo legible; preservar historial fuera del tree principal si no se necesita frecuentemente.

- **8) Añadir test de regresión para backoff/adaptive retries**
  - Objetivo: Cobertura específica para la lógica de `backoff factor` y comportamiento del [RLAgent](http://_vscodecontentref_/5) frente a métricas de calidad.
  - Por qué: Evitar regresiones que afecten la resiliencia del crawler.

- **9) Asegurar privacidad y manejo de secretos**
  - Objetivo: Revisar logs y artefactos, asegurarse de que no se exponen API keys o datos sensibles; usar `.env` y `secrets` en CI.
  - Por qué: Cumplimiento y seguridad.

---

## Notas finales y próximos pasos sugeridos (breve) (Histórico)

- Priorizar la implementación de thread-safety y la normalización de datetimes (pasos 1 y 2) antes de desplegar cambios en producción.
- Ejecutar la suite de tests localmente y en CI (paso 3). Arreglar los tests `TODO` y añadir cobertura para la lógica crítica.
- Si quieres, puedo generar parches concretos (por ejemplo, aplicar locks en [proxy_manager.py](http://_vscodecontentref_/6)) y/o ejecutar [pytest](http://_vscodecontentref_/7) para listar fallos; indícame si deseas que proceda con esos cambios.
- Mantener este archivo como la fuente de verdad para roadmap; cualquier mejora o decisión importante añadirla aquí con fecha y responsable.

### Cambios operativos realizados (2025-08-31)

- Reorganización de backups: se movieron snapshots y scripts de backup desde la raíz del repositorio a `backups/snapshots/` y `backups/files/`.
- Añadidos `backups/RESTORE_GUIDE.md` y `backups/cleanup_backups.ps1`.
- Actualizado `README.md` para referenciar las nuevas ubicaciones de los scripts legacy.

Recomendación inmediata: decidir si `backups/` debe permanecer versionado. Si se desea excluirlo, añadir `backups/` a `.gitignore` y ejecutar `git rm -r --cached backups`.