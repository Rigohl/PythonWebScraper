# Hoja de Ruta Estratégica: PythonWebScraper Evolution

Este documento es la guía estratégica para la evolución del proyecto. Define la visión, la arquitectura objetivo y un plan de acción detallado para transformar un scraper avanzado en una **plataforma de inteligencia de datos autónoma**.

---

## Visión del Producto

Crear un agente autónomo que no solo extraiga datos, sino que los **comprenda y contextualice**. Un sistema que navegue la web de forma similar a un humano, se adapte en tiempo real a contramedidas (bloqueos, CAPTCHAs, cambios de layout), aprenda de cada interacción para optimizar su estrategia y transforme el caos de la web en un grafo de conocimiento limpio y accionable, requiriendo intervención humana solo para definir los objetivos de alto nivel.

---

## Fase 1: Excelencia Operativa y Deuda Técnica (Prioridad Alta)

Esta fase se centra en robustecer el código existente, mejorar la mantenibilidad y establecer una base sólida para futuras expansiones.

- **Gestión de Configuración Avanzada:** (Completado)
  - **Problema:** `config.py` era estático y no se adaptaba a diferentes entornos (desarrollo, producción) ni permitía overrides sencillos.
  - **Solución Implementada:** Se ha migrado toda la configuración a un nuevo módulo `src/settings.py` que utiliza `pydantic-settings`. Ahora, la aplicación carga su configuración desde un archivo `.env` y variables de entorno, con validación de tipos automática. Esto permite, por ejemplo, cambiar la concurrencia con `CONCURRENCY=10` en el `.env` sin tocar el código.

- **Manejo de Errores Centralizado:** (Completado)
  - **Problema:** El manejo de excepciones estaba disperso, dificultando la toma de decisiones centralizada.
  - **Solución Implementada:** Se ha creado `src/exceptions.py` con una jerarquía de errores (`NetworkError`, `ParsingError`, etc.). El `scraper` ahora lanza estas excepciones específicas, y el `orchestrator` las captura para decidir si reintentar o descartar una URL. Esto robustece enormemente la lógica de fallos.

- **Suite de Pruebas Exhaustiva:** (En Progreso)
  - **Problema:** La cobertura de pruebas era mínima, lo que hacía que los cambios futuros fueran arriesgados.
  - **Solución Implementada:** Se ha configurado `pytest` como el framework de pruebas del proyecto. Se han creado los archivos de configuración (`pytest.ini`, `tests/conftest.py`) y se han implementado tests iniciales para el `AdvancedScraper` (verificando la extracción de datos de HTML local) y para el `ScrapingOrchestrator` (verificando la lógica de priorización).
  - **Próximos Pasos:** Expandir la cobertura de `test_orchestrator.py` para simular el ciclo de vida completo de un worker. Añadir pruebas para la TUI y los managers de User-Agent/Proxy.

- **Calidad de Código Automatizada:** (Completado)
  - **Problema:** El estilo de código y la calidad no se forzaban de manera automática, llevando a inconsistencias.
  - **Solución Implementada:** Se han añadido las dependencias de desarrollo (`pre-commit`, `black`, `isort`, `flake8`) a `requirements.txt`. Esto sienta las bases para configurar un archivo `.pre-commit-config.yaml` que formateará y validará el código automáticamente antes de cada commit, garantizando un código limpio y consistente en todo el proyecto.

- **Estructura de Proyecto Refinada:** (Completado)
  - **Problema:** Los modelos de datos Pydantic (como `ScrapeResult`) estaban definidos junto al código que los usaba (ej. `scraper.py`).
  - **Solución Implementada:** Se ha creado un directorio `src/models/` y los modelos de datos se han movido allí (inferido por `from src.models.results import ScrapeResult`). Esto separa limpiamente los esquemas de datos de la lógica de negocio, mejorando la organización.

---

## Fase 2: Inteligencia Táctica y Evasión (Completado y a Mejorar)

Esta fase se enfoca en hacer el scraper más resiliente, adaptativo y difícil de detectar.

- **Fundación Sólida:** (Completado) Arquitectura modular, concurrencia con `asyncio`, persistencia en SQLite y modelos con `Pydantic`.
- **Scraping Adaptativo:** (Completado) Throttling adaptativo (backoff exponencial), detección de cambios visuales (pHash), renderizado inteligente (`networkidle`), detección de honeypots y reintentos.
- **Optimización de Rendimiento:** (Completado) Bloqueo de recursos innecesarios.
- **Selectores "Auto-reparables" (Self-Healing):** (Completado)
- **Módulo de Scraping Ético:** (Completado) Soporte para `robots.txt`.
- **CLI y Logging:** (Completado) Argumentos por línea de comandos y logging estructurado.
- **Exportación de Datos:** (Completado) Exportación a CSV.

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
  - **Problema:** El `RLAgent` actual es un esqueleto. El backoff adaptativo es una regla heurística simple.
  - **Solución:** Implementar un agente de RL completo (ej. con Q-Learning o PPO simple).
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

- **Priorización Inteligente de la Frontera de Rastreo:** (Mejora Pendiente)
  - **Problema:** La cola de prioridad actual se basa en la profundidad de la URL, una heurística simple.
  - **Solución:** Usar un modelo de clasificación simple (o un LLM) para predecir la "promesa" de una URL.
    - **Features:** Texto del ancla del enlace, URL de origen, URL de destino, tipo de contenido de la página padre.
    - **Objetivo:** Predecir la probabilidad de que la URL contenga datos de alta calidad o lleve a ellos.
  - **Resultado:** El crawler explorará de forma inteligente, priorizando las rutas más fructíferas y evitando perder tiempo en secciones irrelevantes del sitio (ej. "política de privacidad", "carreras").

---

## Fase 5: Experiencia de Usuario y Observabilidad (Mejoras TUI/GUI)

- **Dashboard en Tiempo Real:** (Pendiente)
  - **Problema:** La TUI actual es un lanzador, pero no ofrece visibilidad durante el crawling.
  - **Solución:** Implementar una pestaña de "Estadísticas en Vivo" en la TUI. El orquestador usará un sistema de `callbacks` para reportar métricas en tiempo real (URLs en cola, procesadas, éxitos, fallos) sin acoplarse a la TUI. Esto proporciona una visión clara del rendimiento y estado del crawler.

---

## Fase 5: Arquitectura de Plataforma y Escalabilidad (Visión a Largo Plazo)

Esta fase prepara el proyecto para operar a gran escala y ser extensible.

- **Descubrimiento de APIs Ocultas (Hidden APIs):** (Pendiente)
  - **Estrategia:** En lugar de renderizar y parsear HTML, interceptar y analizar las peticiones de red (XHR/Fetch) que hace la página. Si se detecta una API que devuelve JSON con los datos deseados, cambiar la estrategia para atacar directamente esa API, que es miles de veces más rápido y fiable que el scraping de UI.

- **Arquitectura de Plugins:** (Pendiente)
  - **Estrategia:** Refactorizar la lógica de extracción, guardado y notificación en un sistema de plugins. Esto permitiría a los usuarios añadir nuevas capacidades sin modificar el núcleo. Ejemplos: un plugin para guardar en PostgreSQL, un plugin para notificar por Slack, un plugin para un tipo específico de extracción.

- **Soporte para Scraping Distribuido:** (Pendiente)
  - **Estrategia:** Usar una cola de mensajes centralizada (como RabbitMQ o Redis) en lugar de la `asyncio.Queue` local. Esto permitiría lanzar múltiples instancias del scraper (workers) en diferentes máquinas, todas consumiendo de la misma cola de URLs, logrando una escala masiva.

- **Creación de Grafos de Conocimiento:** (Pendiente)
  - **Estrategia:** Migrar de SQLite a una base de datos de grafos como Neo4j. En lugar de una tabla plana de `(URL, contenido)`, modelar los datos como un grafo:
    - **Nodos:** `Page`, `Product`, `Article`, `Author`.
    - **Relaciones:** `(Page)-[:LINKS_TO]->(Page)`, `(Page)-[:CONTAINS]->(Product)`, `(Article)-[:WRITTEN_BY]->(Author)`.
  - **Resultado:** Permite análisis mucho más ricos sobre las relaciones entre los datos, no solo los datos en sí.

---

## Fase 6: Inteligencia Cognitiva y Comprensión del Contexto (El Futuro)

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

## Registro de Cambios (Changelog)

*Se mantiene el changelog existente.*
