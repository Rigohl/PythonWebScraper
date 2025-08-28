# Hoja de Ruta Estratégica: PythonWebScraper Evolution

Este documento es la guía estratégica para la evolución del proyecto. Define la visión, la arquitectura objetivo y un plan de acción detallado para transformar un scraper avanzado en una **plataforma de inteligencia de datos autónoma.**

---

## Visión del Producto

Crear un agente autónomo que no solo extraiga datos, sino que los **comprenda y contextualice.** Un sistema que navegue la web de forma similar a un humano, se adapte en tiempo real a contramedidas (bloqueos, CAPTCHAs, cambios de layout), aprenda de cada interacción para optimizar su estrategia y transforme el caos de la web en un grafo de conocimiento limpio y accionable, requiriendo intervención humana solo para definir los objetivos de alto nivel.

---

## Fases y Mejoras

### Puntos a Corregir (Refactorización Inmediata - Prioridad Alta)

Estos son problemas identificados que deberían abordarse para mejorar la estabilidad, la mantenibilidad y la coherencia del proyecto.

1.  **Redundancia en `src/settings.py`**:
    *   **Problema**: El archivo `src/settings.py` está vacío y no tiene un propósito claro, duplicando potencialmente la gestión de configuración ya manejada por `src/config.py`.
    *   **Acción Recomendada**: Eliminar `src/settings.py` por completo o redefinir su propósito para que contenga *únicamente* constantes o configuraciones muy específicas de módulos que no sean adecuadas para el `.env` o `config.py`.
2.  **Archivos Estáticos no Servidos en FastAPI**:
    *   **Problema**: La API de FastAPI tiene una ruta raíz que intenta cargar `styles.css`, pero el middleware `StaticFiles` en `src/app.py` está comentado, lo que impide que los estilos se sirvan correctamente.
    *   **Acción Recomendada**: Descomentar y configurar `app.mount("/static", StaticFiles(directory="static"), name="static")` en `src/app.py` para habilitar el servicio de archivos estáticos.
3.  **Función `run_api_server` Redundante en `src/app.py`**:
    *   **Problema**: La función `run_api_server` está definida en `src/app.py`, pero `src/main.py` lanza el servidor Uvicorn directamente. Esto hace que la función sea innecesaria.
    *   **Acción Recomendada**: Eliminar la función `run_api_server` de `src/app.py`.
4.  **Integración Incompleta de `FingerprintManager`**:
    *   **Problema**: El `FingerprintManager` se inicializa y se le pide una huella digital, pero la salida (`current_fingerprint`) solo se registra y no se utiliza activamente para configurar las opciones de Playwright dentro de `src/scraper.py`. Esto reduce la efectividad de la estrategia anti-detección.
    *   **Acción Recomendada**: Modificar `src/scraper.py` (o el `Orchestrator` al llamar al `Scraper`) para que configure el navegador de Playwright con los detalles de huella digital proporcionados por `FingerprintManager` (ej., añadiendo cabeceras específicas, configurando el viewport, o inyectando JavaScript para falsear propiedades del `navigator`).

---

## Fase 1: Excelencia Operativa y Deuda Técnica (Prioridad Alta)

Esta fase se centra en robustecer el código existente, mejorar la mantenibilidad y establecer una base sólida para futuras expansiones.

- **Gestión de Configuración Avanzada:** (Completado)
  - **Problema:** `config.py` era estático y no se adaptaba a diferentes entornos (desarrollo, producción) ni permitía overrides sencillos.
  - **Solución Implementada:** Se ha migrado toda la configuración a un nuevo módulo `src/settings.py` (ahora `src/config.py` con `pydantic-settings`). Ahora, la aplicación carga su configuración desde un archivo `.env` y variables de entorno, con validación de tipos automática. Esto permite, por ejemplo, cambiar la concurrencia con `CONCURRENCY=10` en el `.env` sin tocar el código.

- **Manejo de Errores Centralizado:** (Completado)
  - **Problema:** El manejo de excepciones estaba disperso, dificultando la toma de decisiones centralizada.
  - **Solución Implementada:** Se ha creado `src/exceptions.py` con una jerarquía de errores (`NetworkError`, `ParsingError`, etc.). El `scraper` ahora lanza estas excepciones específicas, y el `orchestrator` las captura para decidir si reintentar o descartar una URL. Esto robustece enormemente la lógica de fallos.

- **Suite de Pruebas Exhaustiva:** (En Progreso)
  - **Problema:** La cobertura de pruebas era mínima, lo que hacía que los cambios futuros fueran arriesgados.
  - **Solución Implementada:** Se ha configurado `pytest` como el framework de pruebas del proyecto. Se han creado los archivos de configuración (`pytest.ini`, `tests/conftest.py`) y se han implementado tests iniciales para el `AdvancedScraper` (verificando la extracción de datos de HTML local) y para el `ScrapingOrchestrator` (verificando la lógica de priorización).
  - **Próximos Pasos:** Expandir la cobertura de `test_orchestrator.py` para simular el ciclo de vida completo de un worker. Añadir **pruebas de regresión funcional** específicas por dominio, utilizando fixtures de HTML real para asegurar que los cambios no rompan la extracción en sitios clave.

- **Calidad de Código Automatizada:** (Completado)
  - **Problema:** El estilo de código y la calidad no se forzaban de manera automática, llevando a inconsistencias.
  - **Solución Implementada:** Se han añadido las dependencias de desarrollo (`pre-commit`, `black`, `isort`, `flake8`) a `requirements.txt`. Esto sienta las bases para configurar un archivo `.pre-commit-config.yaml` que formateará y validará el código automáticamente antes de cada commit, garantizando un código limpio y consistente en todo el proyecto.

- **Estructura de Proyecto Refinada:** (Completado)
  - **Problema:** Los modelos de datos Pydantic (como `ScrapeResult`) estaban definidos junto al código que los usaba (ej. `scraper.py`).
  - **Solución Implementada:** Se ha creado un directorio `src/models/` y los modelos de datos se han movido allí (inferido por `from src.models.results import ScrapeResult`). Esto separa limpiamente los esquemas de datos de la lógica de negocio, mejorando la organización.

- **Desacoplamiento de Scraping y API en `main.py`**:
    *   **Problema**: La ejecución síncrona del proceso de scraping completo (`--scrape`) en `main.py` antes de iniciar la API (`--api`) puede bloquear el inicio de la API por un tiempo prolongado si el scraping es intensivo.
    *   **Mejora**: Refactorizar `main.py` para que, si se solicitan ambos (`--scrape --api`), el scraping se inicie como una tarea de fondo (similar a cómo lo hace el endpoint `/scrape/` en `app.py`) o en un proceso separado. Alternativamente, definir claramente que `--scrape` es para ejecuciones únicas CLI y la API para orquestar tareas.

---

## Fase 2: Inteligencia Táctica y Evasión (Completado y a Mejorar)

Esta fase se enfoca en hacer el scraper más resiliente, adaptativo y difícil de detectar.

- **Fundación Sólida:** (Completado) Arquitectura modular, concurrencia con `asyncio`, persistencia en SQLite (ahora PostgreSQL/SQLAlchemy), modelos con `Pydantic`.
- **Scraping Adaptativo:** (Completado) Throttling adaptativo, detección de cambios visuales, renderizado inteligente, detección de honeypots, reintentos.
- **Optimización de Rendimiento:** (Completado) Bloqueo de recursos.
- **Selectores "Auto-reparables":** (Completado)
- **Scraping Ético:** (Completado) Soporte para `robots.txt`.

- **Protección contra Bucles y Trampas:** (Completado)
  - **Problema:** El scraper podía caer en "trampas" de crawling (ej. calendarios con enlaces infinitos) o bucles de redirección.
  - **Solución Implementada:** Se ha implementado un detector de patrones de URL repetitivos (ej. `/a/b/a/b`) y un contador de redirecciones por URL para descartarlas si exceden un umbral configurable. Esto previene que el crawler caiga en bucles y consuma recursos inútilmente.

- **Límites de Rastreo Configurables:** (Pendiente)
  - **Problema:** Un crawl puede crecer sin control, consumiendo recursos excesivos.
  - **Solución:** Añadir a la configuración límites globales como `MAX_PAGES_TO_CRAWL` o `MAX_CRAWL_DEPTH`.

---

## Fase 3: Evasión de Nivel Humano y Detección de Contramedidas (Próximos Pasos)

- **Navegadores "Sigilosos" (Stealth):** (Completado)
  - **Problema:** Los navegadores automatizados dejan huellas detectables (ej. `navigator.webdriver`).
  - **Solución Implementada:** Se ha integrado `playwright-stealth`. El `ScrapingOrchestrator` ahora aplica parches anti-detección a cada página que crea, haciendo el crawling significativamente más difícil de bloquear por servicios como Cloudflare.

- **Gestión de Huellas Digitales (Fingerprinting):** (Completado)
  - **Problema:** Usar solo `User-Agent` diferentes no es suficiente. Los sitios modernos analizan huellas complejas (fuentes, plugins, resolución de pantalla, WebGL, canvas).
  - **Solución Implementada:** Se ha creado un `FingerprintManager` que genera perfiles de navegador completos y consistentes. El orquestador ahora aplica a cada página un User-Agent, un viewport y un conjunto de propiedades JavaScript falseadas (`navigator.platform`, `navigator.webdriver`, etc.), haciendo que cada worker parezca un usuario único y legítimo.

- **Detección y Manejo de CAPTCHAs:** (Pendiente)
  - **Problema:** Un CAPTCHA detiene por completo el scraping.
  - **Solución:** Implementar un detector de CAPTCHAs.
    - **Detección:** Buscar elementos comunes (ej. `iframe[src*="recaptcha"]`, `div.g-recaptcha`).
    - **Acción:** Al detectar un CAPTCHA, el orquestador debe tomar una acción: 1) Descartar la URL y penalizar la ruta que llevó a ella. 2) Poner la URL en una cola de "revisión manual". 3) (Avanzado) Integrar con un servicio de resolución de CAPTCHAs como 2Captcha a través de su API.

---

## Fase 4: Inteligencia Estratégica y Autonomía (La Verdadera IA)

Esta fase convierte el scraper de una herramienta reactiva a un agente proactivo que aprende y planifica.

- **Agente de Aprendizaje por Refuerzo (RL) Evolucionado:** (Pendiente - Alta Prioridad)
  - **Problema:** El `RLAgent` actual es un esqueleto y el backoff adaptativo es una regla heurística simple. Su integración activa en la toma de decisiones del orquestador no es evidente.
  - **Solución:** Implementar un agente de RL completo (ej. con Q-Learning o PPO simple) e integrarlo activamente en el `Orchestrator` para que pueda ajustar dinámicamente parámetros como la velocidad de scraping, los intervalos de reintento, la selección de proxies/user agents, o incluso las estrategias de extracción de LLM, basándose en la retroalimentación del éxito o fallo de las operaciones en diferentes dominios.
    - **Estado (State):** Un vector que representa la situación actual para un dominio: `(ratio_fallos_recientes, ratio_baja_calidad, tiempo_carga_medio, captcha_detectado, ratio_bloqueos_4xx, ratio_errores_5xx)`.
    - **Acciones (Actions):** El conjunto de decisiones que el agente puede tomar: `(cambiar_user_agent, ajustar_delay, usar_proxy_premium, no_usar_proxy, activar_stealth, desactivar_stealth)`.
    - **Recompensa (Reward):** La señal que guía el aprendizaje. `+10` por un scrapeo exitoso y de alta calidad. `-5` por un fallo de red. `-20` por un bloqueo (403/429). `-2` por tiempo de carga excesivo.
  - **Resultado:** El scraper aprenderá la **estrategia óptima por dominio**. Para un sitio agresivo, aprenderá a ir más lento y usar proxies premium. Para un sitio permisivo, irá más rápido para maximizar la eficiencia.

- **Extracción de Datos Impulsada por LLMs (Zero-Shot Extraction):** (Pendiente)
  - **Problema:** El `EXTRACTION_SCHEMA` es rígido y requiere que un humano defina selectores CSS.
  - **Solución:** Integrar un LLM (vía `instructor` o similar) para la extracción.
    - **Input al LLM:** El HTML crudo de la página y una descripción en lenguaje natural del objetivo: `"Extrae el nombre del producto, su precio y la moneda. El precio puede no tener símbolo."`
    - **Output del LLM:** Un objeto Pydantic/JSON con los datos extraídos: `{ "product_name": "...", "price": 19.99, "currency": "USD" }`.
  - **Resultado:** El scraper se vuelve universal. Ya no necesita selectores predefinidos, solo un objetivo. Esto elimina la principal causa de rotura de los scrapers.

- **Scraping Condicional por Reglas:** (Pendiente)
  - **Problema:** El scraper procesa todas las páginas que encuentra dentro de un dominio.
  - **Solución:** Implementar un sistema de reglas personalizadas por dominio en la configuración. Por ejemplo: `scrape_only_if: { title_contains: ["Product", "Article"], url_matches_regex: "/p/.*" }`. El scraper evaluaría estas reglas antes de realizar el scraping completo.

- **Priorización Inteligente de la Frontera de Rastreo:** (Mejora Pendiente)
  - **Problema:** La cola de prioridad actual se basa en la profundidad de la URL, una heurística simple.
  - **Solución:** Usar un modelo de clasificación simple (o un LLM) para predecir la "promesa" de una URL.
    - **Features:** Texto del ancla del enlace, URL de origen, URL de destino, tipo de contenido de la página padre.
    - **Objetivo:** Predecir la probabilidad de que la URL contenga datos de alta calidad o lleve a ellos.
  - **Resultado:** El crawler explorará de forma inteligente, priorizando las rutas más fructíferas y evitando perder tiempo en secciones irrelevantes del sitio (ej. "política de privacidad", "carreras").

- **Esquemas de Extracción LLM Flexibles/Aprendidos**:
    *   **Problema**: El esquema de extracción LLM se define actualmente de forma estática en `_process_page`. La visión del proyecto sugiere una "estrategia óptima por dominio", lo que implica adaptabilidad.
    *   **Mejora**: Permitir que los esquemas de extracción LLM sean dinámicos y configurables por dominio/URL, posiblemente almacenados en la base de datos, o desarrollar una lógica para que el sistema "aprenda" o adapte el esquema basándose en el contenido o el dominio.

---

## Fase 5: Experiencia de Usuario y Observabilidad

- **Dashboard en Tiempo Real:** (En Progreso)
  - **Solución:** Se ha implementado una pestaña de "Estadísticas en Vivo" en la TUI con métricas globales.

- **Dashboard de Métricas por Dominio:** (Completado)
  - **Problema:** Las estadísticas eran globales, impidiendo saber cómo se comportaba el scraper en un dominio específico.
  - **Solución Implementada:** Se ha añadido una tabla de métricas por dominio en la pestaña de "Estadísticas" de la TUI. Esta tabla muestra en tiempo real el `backoff_factor`, el número de páginas procesadas, los fallos y otros datos clave para cada dominio que se está rastreando. Esto proporciona una visibilidad granular sobre el rendimiento y la adaptación del scraper a las defensas de cada sitio.

- **Visualización de Resultados Extraídos:** (Pendiente)
  - **Problema:** Para consultar los datos, es necesario acceder directamente a la base de datos.
  - **Solución:** Añadir una nueva pestaña a la TUI o una pequeña interfaz web (con Flask/FastAPI) que permita buscar y visualizar los resultados guardados en la base de datos de forma amigable.

- **Mecanismo de Alertas y Notificaciones:** (Pendiente)
  - **Problema:** Los eventos críticos (bloqueos masivos, detección de CAPTCHAs) solo se ven en los logs.
  - **Solución:** Integrar un sistema de notificaciones. En la TUI, podría ser un widget de "Alertas Críticas". A nivel de sistema, podría ser la integración con servicios como Sentry para errores, o webhooks para notificar a Slack/Discord.

---

## Fase 6: Integridad y Calidad de Datos

- **Gestión de Duplicados por Contenido:** (Completado)
  - **Problema:** URLs con parámetros diferentes pueden apuntar al mismo contenido, causando trabajo redundante y datos sucios.
  - **Solución Implementada:** El scraper ahora calcula un hash SHA256 del texto limpio de cada página. Antes de guardar un resultado, el `DatabaseManager` comprueba si ya existe un registro con el mismo hash. Si es así, la nueva página se marca como `DUPLICATE` y sus enlaces no se añaden a la cola, ahorrando recursos y manteniendo la base de datos limpia.

---

## Fase 7: Arquitectura de Plataforma y Escalabilidad (Visión a Largo Plazo)

Esta fase prepara el proyecto para operar a gran escala y ser extensible.

- **Descubrimiento de APIs Ocultas (Hidden APIs):** (Pendiente)
  - **Estrategia:** En lugar de renderizar y parsear HTML, interceptar y analizar las peticiones de red (XHR/Fetch) que hace la página. Si se detecta una API que devuelve JSON con los datos deseados, cambiar la estrategia para atacar directamente esa API, que es miles de veces más rápido y fiable que el scraping de UI.

- **Arquitectura de Plugins:** (Pendiente)
  - **Estrategia:** Refactorizar la lógica de extracción, guardado y notificación en un sistema de plugins. Esto permitiría a los usuarios añadir nuevas capacidades sin modificar el núcleo.

- **Soporte para Scraping Distribuido:** (Pendiente)
  - **Estrategia:** Usar una cola de mensajes centralizada (como RabbitMQ o Redis) en lugar de la `asyncio.Queue` local. Esto permitiría lanzar múltiples instancias del scraper (workers) en diferentes máquinas, todas consumiendo de la misma cola de URLs, logrando una escala masiva.

- **Control de Versiones de Datos y Configuración:** (Pendiente)
  - **Problema:** La configuración y los esquemas de extracción cambian, pero no hay trazabilidad.
  - **Solución:** Versionar los objetos de configuración (`Settings_v1_1`) y los esquemas de datos. Guardar junto a cada resultado la versión de la configuración con la que fue scrapeado, permitiendo reproducibilidad y análisis de cómo los cambios en la configuración afectan los resultados.

- **Creación de Grafos de Conocimiento:** (Pendiente)
  - **Estrategia:** Migrar de SQLite (que es propenso a corrupción en alta concurrencia) a una base de datos más robusta como PostgreSQL (para datos tabulares) o Neo4j (para datos relacionales). Modelar los datos como un grafo:
    - **Nodos:** `Page`, `Product`, `Article`, `Author`.
    - **Relaciones:** `(Page)-[:LINKS_TO]->(Page)`, `(Page)-[:CONTAINS]->(Product)`, `(Article)-[:WRITTEN_BY]->(Author)`.
  - **Resultado:** Permite análisis mucho más ricos sobre las relaciones entre los datos, no solo los datos en sí.

---

## Fase 8: Optimización de Velocidad Extrema

- **Pre-calificación de URLs con `HEAD`:** (Completado)
  - **Problema:** Lanzar un navegador completo solo para descubrir que una URL apunta a un archivo grande (ej. un PDF de 50MB) es un enorme desperdicio de recursos.
  - **Solución Implementada:** Antes de encolar una nueva URL, el orquestador ahora realiza una petición `HEAD` asíncrona y ultrarrápida. Esto le permite inspeccionar las cabeceras `Content-Type` y `Content-Length` para descartar al instante enlaces a tipos de archivo no deseados o a contenidos que exceden un tamaño máximo configurable, acelerando drásticamente el crawl.

- **Descubrimiento y Explotación de APIs Ocultas (Prioridad Alta):** (Pendiente)
  - **Problema:** El scraping de HTML renderizado es lento y frágil.
  - **Solución:** Modificar el orquestador para que escuche las peticiones de red (XHR/Fetch) que la página realiza. Si detecta una petición a una API que devuelve los datos en formato JSON, puede "aprender" este endpoint. Para las siguientes URLs del mismo tipo, en lugar de renderizar la página, atacará directamente la API, lo que es órdenes de magnitud más rápido y fiable.

---

## Fase 9: Inteligencia Cognitiva

Esta fase se enfoca en dotar al agente de una comprensión casi humana del contenido que procesa.

- **Análisis Causal de Cambios con LLMs:** (Pendiente)
  - **Problema:** La detección de cambios visuales (pHash) nos dice que *algo* cambió, pero no el *qué* o el *porqué*.
  - **Solución:** Cuando se detecta un cambio visual significativo, enviar el HTML antiguo y el nuevo a un LLM con un prompt para que describa la diferencia en lenguaje natural. Ej: "El precio ha sido movido debajo de la imagen del producto" o "Se ha añadido un banner de promoción". Esto proporciona inteligencia accionable en lugar de una simple alerta.

- **Extracción Multi-Modal (Visión por Computadora):** (Pendiente)
  - **Problema:** El scraper es ciego a la información contenida dentro de las imágenes (ej. precios en banners, datos en infografías).
  - **Solución:** Integrar una librería de OCR (Optical Character Recognition) como `pytesseract`. Tras tomar una captura de pantalla, el scraper puede realizar un análisis OCR sobre ella para extraer texto. Esto le permite "leer" datos que no existen en el DOM HTML.

- **Construcción Activa de Grafos de Conocimiento con NER:** (Pendiente)
  - **Problema:** La idea de un grafo de conocimiento es potente, pero la creación de nodos y relaciones es manual.
  - **Solución:** Utilizar un LLM para realizar **Reconocimiento de Entidades Nombradas (NER)** sobre el contenido limpio. El agente identificará automáticamente entidades como `Personas`, `Organizaciones`, `Productos` y `Lugares`. Luego, creará los nodos correspondientes en la base de datos de grafos y las relaciones entre ellos (ej. `(Artículo)-[:MENCIONA]->(Organización)`). Esto transforma el scraper de un archivador a un constructor de conocimiento autónomo.

---

## Fase 10: Autonomía Estratégica

- **Descubrimiento Automático de Objetivos:** (Pendiente)
  - **Problema:** El scraper necesita que un humano le dé una URL inicial.
  - **Solución:** Darle al scraper un objetivo de alto nivel, como `"Encuentra artículos sobre Python 3.12"`. El agente usaría una API de búsqueda (como SerpAPI) o scraparía un motor de búsqueda para encontrar un conjunto de URLs semilla relevantes. A partir de ahí, iniciaría su proceso de crawling normal, volviéndose verdaderamente autónomo en la fase de descubrimiento.

- **Auto-configuración de Extracción con LLMs:** (Pendiente)
  - **Problema:** La extracción de datos aún depende de un `EXTRACTION_SCHEMA` predefinido.
  - **Solución:** Eliminar por completo el `EXTRACTION_SCHEMA`. En su lugar, el usuario proporciona un modelo Pydantic que describe los datos deseados (ej. `class Product(BaseModel): name: str; price: float;`). El scraper envía el HTML de la página y el esquema del modelo a un LLM (usando una librería como `instructor`) y le pide que "rellene" el modelo. Esto elimina la necesidad de escribir selectores CSS para siempre.

---

## Registro de Cambios (Changelog)

*   **2024-07-30**: Análisis inicial del proyecto y adición de "Puntos a Corregir" y "Posibles Mejoras" a la hoja de ruta estratégica.
*Se mantiene el changelog existente.*
