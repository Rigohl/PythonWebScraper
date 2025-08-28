# Mejoras y Próximas Fases del Proyecto

Este documento detalla las mejoras y las próximas fases planificadas para el proyecto de web scraping, estructuradas por áreas funcionales y etapas de desarrollo.

---

## Fase 1: Core de Navegación y Extracción

- **Integración de Playwright en Docker (RESUELTO)**:
  - **Problema**: Dificultades para ejecutar Playwright dentro de un contenedor Docker debido a dependencias de navegador.
  - **Solución (Implementada)**: Se ha configurado Dockerfile y las dependencias para asegurar la ejecución estable de Playwright en un entorno contenedorizado.
- **Rotación de User-Agents y Fingerprinting Avanzado (EN PROGRESO)**:
  - **Problema**: Detección y bloqueo por parte de sitios web debido a huellas digitales de navegador consistentes.
  - **Mejora**: Implementar una estrategia dinámica de rotación de User-Agents y técnicas de fingerprinting avanzado (p. ej., WebGL, Canvas, etc.) para emular un comportamiento de usuario real y evitar la detección.
  - **Solución Actual**: Se ha implementado la rotación de User-Agents basada en el archivo `user_agents.json` para cada worker de Playwright. Pruebas iniciales sugieren que mejora la resistencia a la detección.
- **Manejo Inteligente de Cookies y Sesiones (COMPLETADO)**:
  - **Problema**: La gestión actual de cookies es básica, lo que puede limitar el acceso a contenido protegido o personalizado.
  - **Mejora**: Desarrollar un sistema para persistir y rotar cookies y sesiones por dominio, permitiendo mantener sesiones activas y sortear sistemas de autenticación o límites de acceso.
  - **Solución Implementada**: Se ha implementado la persistencia y carga de cookies por dominio utilizando `src/database.py` y `src/scraper.py`. Las cookies se guardan después de un scrapeo exitoso y se cargan antes de navegar a una URL del mismo dominio, mejorando la capacidad de mantener sesiones.

---

## Fase 2: Robustez y Escalabilidad

- **Gestión de Proxies Robusta (EN PROGRESO)**:
  - **Problema**: La dependencia de un único proxy o una lista estática reduce la fiabilidad y escalabilidad.
  - **Mejora**: Implementar un `ProxyManager` que soporte múltiples fuentes de proxies (p. ej., rotación de proxies residenciales, integración con servicios de terceros), con lógica de reintento y exclusión de proxies defectuosos.
  - **Solución Actual**: Se ha implementado un `ProxyManager` que carga proxies desde `proxies.txt` y los asigna a los workers. Se necesita mejorar la lógica de reintento y validación.
- **Reintentos Adaptativos con Backoff Exponencial (COMPLETADO)**:
  - **Problema**: Fallos intermitentes en la red o en el servidor web pueden causar interrupciones innecesarias.
  - **Mejora**: Implementar una lógica de reintentos con backoff exponencial y jitter para manejar fallos temporales de manera más eficiente y menos intrusiva.
  - **Solución Implementada**: El `ScrapingOrchestrator` ya incluye una lógica de reintentos adaptativos con backoff exponencial. En caso de `NetworkError`, el worker espera un tiempo que aumenta exponencialmente con cada intento fallido, multiplicado por un factor de backoff dinámico por dominio, antes de reintentar el scrapeo de la URL.
- **Manejo de Errores y Retries Específicos de Scraper (PLANIFICADO)**:
  - **Problema**: Los errores durante el scraping pueden ser variados (p. ej., CAPTCHAs, errores de renderizado).
  - **Mejora**: Permitir a cada `BaseScraper` definir estrategias de reintento o manejo de errores específicas para su dominio o tipo de contenido.

---

## Fase 3: Detección y Evasión

- **Manejo de CAPTCHAs y Detección de Bots (PLANIFICADO)**:
  - **Problema**: Los sitios web utilizan CAPTCHAs y otras técnicas para detectar y bloquear bots.
  - **Mejora**: Investigar y posiblemente integrar servicios de resolución de CAPTCHAs (p. ej., 2Captcha, Anti-Captcha) o desarrollar modelos de aprendizaje automático para la detección y evasión de patrones de bloqueo.
- **Adaptación a Cambios de UI/HTML (PLANIFICADO)**:
  - **Problema**: Los cambios frecuentes en la estructura HTML de los sitios web rompen los scrapers existentes.
  - **Mejora**: Desarrollar un enfoque más resiliente para la extracción de datos, posiblemente utilizando selectores más robustos (p. ej., atributos en lugar de clases), o técnicas de Computer Vision/LLM para identificar elementos de forma semántica.

---

## Fase 4: Inteligencia y Extracción de Datos

- **Esquemas de Extracción LLM Flexibles/Aprendidos (COMPLETADO)**:
  - **Problema**: El esquema de extracción LLM se definía estáticamente.
  - **Mejora**: Permitir que los esquemas de extracción LLM sean dinámicos y configurables por dominio/URL.
  - **Solución Implementada**: Se ha actualizado `src/database.py` para almacenar esquemas de extracción LLM por dominio. `src/llm_extractor.py` utiliza `instructor` y `openai` para la extracción de datos estructurados reales en modelos Pydantic generados dinámicamente. `src/orchestrator.py` carga estos esquemas y los pasa al `scraper`, eliminando la necesidad de selectores CSS estáticos.
- **Agente de Aprendizaje por Refuerzo (RL) Evolucionado (COMPLETADO)**:
  - **Problema**: El `RLAgent` era un esqueleto y no tenía una implementación real para el aprendizaje.
  - **Mejora**: Implementar un agente de RL completo para ajustar dinámicamente parámetros de scraping.
  - **Solución Implementada**: Se ha integrado un agente de RL basado en PPO (`stable-baselines3` y `gymnasium`). El `RLAgent` ahora puede aprender y ajustar dinámicamente el `backoff factor` para optimizar el rendimiento y la resistencia a la detección. El modelo se guarda y se carga para permitir el aprendizaje persistente.

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

- **Mecanismo de Alertas y Notificaciones:** (Completado)
  - **Problema**: La falta de notificación sobre problemas críticos (p. ej., bloqueo de IP, fallos de scraping) podía llevar a interrupciones prolongadas.
  - **Mejora**: Implementar un sistema de alertas para notificar sobre eventos importantes o errores.
  - **Solución Implementada**: Se ha añadido un widget `AlertsDisplay` en `src/tui.py` para mostrar alertas críticas. El `ScrapingOrchestrator` ahora utiliza un `alert_callback` para enviar mensajes de alerta y su nivel (warning, error) a la TUI cuando se detectan eventos importantes como fallos persistentes, bucles de redirección, problemas de calidad de contenido o cambios visuales.

- **Persistencia de Estado de la TUI (PLANIFICADO)**:
  - **Problema**: La configuración y el estado de la TUI se pierden al reiniciar la aplicación.
  - **Mejora**: Permitir guardar y cargar la configuración de la TUI para mantener el estado entre sesiones.

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

- **2024-07-30**: Análisis inicial del proyecto y adición de "Puntos a Corregir" y "Posibles Mejoras" a la hoja de ruta estratégica.
- **2025-08-28**: Completada la implementación de Extracción de Datos Zero-Shot con LLMs (Tarea A.2).
*Se mantiene el changelog existente.*