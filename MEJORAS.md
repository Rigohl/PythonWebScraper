# Hoja de Ruta Estratégica: PythonWebScraper Evolution

Este documento es la guía estratégica para la evolución del proyecto. Define la visión, la arquitectura objetivo y un plan de acción detallado para transformar un scraper avanzado en una **plataforma de inteligencia de datos autónoma**.

---

## Visión del Producto

Crear un agente autónomo que no solo extraiga datos, sino que los **comprenda y contextualice**. Un sistema que navegue la web de forma similar a un humano, se adapte en tiempo real a contramedidas (bloqueos, CAPTCHAs, cambios de layout), aprenda de cada interacción para optimizar su estrategia y transforme el caos de la web en un grafo de conocimiento limpio y accionable, requiriendo intervención humana solo para definir los objetivos de alto nivel.

---

## Fase 1: Excelencia Operativa y Deuda Técnica (Prioridad Alta)

Esta fase se centra en robustecer el código existente, mejorar la mantenibilidad y establecer una base sólida para futuras expansiones.

- **Gestión de Configuración Avanzada:** (Mejora Pendiente)
  - **Problema:** `config.py` es bueno, pero es estático. No se adapta a diferentes entornos (desarrollo, producción) ni permite overrides sencillos.
  - **Solución:** Migrar `config.py` a un modelo basado en `Pydantic Settings`. Esto permite cargar configuraciones desde variables de entorno, archivos `.env` y valores por defecto, todo validado y tipado. Permitirá, por ejemplo, cambiar la concurrencia con una variable de entorno (`SCRAPER_CONCURRENCY=10`) sin tocar el código.

- **Manejo de Errores Centralizado:** (Mejora Pendiente)
  - **Problema:** El manejo de excepciones está disperso (`try/except` en `orchestrator`, `scraper`, etc.). Es difícil tener una visión global de los tipos de fallos.
  - **Solución:** Crear un módulo `src/exceptions.py` con excepciones personalizadas (`ScrapingError`, `NetworkError`, `ParsingError`, `ContentQualityError`). Esto permite capturar errores de forma más granular en el orquestador y tomar decisiones más inteligentes (ej. reintentar en `NetworkError`, descartar en `ParsingError`).

- **Suite de Pruebas Exhaustiva:** (Mejora Crítica Pendiente)
  - **Problema:** Solo existe `test_database.py`. La lógica de negocio principal (`orchestrator`, `scraper`) no está probada, lo que hace que los cambios futuros sean arriesgados.
  - **Solución:** Crear una suite de pruebas completa con `pytest`.
    - `test_scraper.py`: Usar HTML de prueba local para verificar la extracción, la auto-reparación de selectores y la detección de honeypots.
    - `test_orchestrator.py`: Usar `pytest-mock` para "mockear" (simular) el `AdvancedScraper` y el `DatabaseManager`. Probar la lógica de la cola, la gestión de URLs vistas, el respeto a `robots.txt` y la lógica de reintentos.
    - `test_tui.py`: Probar la lógica de la interfaz de usuario de forma aislada.

- **Calidad de Código Automatizada:** (Mejora Pendiente)
  - **Problema:** El estilo de código y la calidad no se fuerzan de manera automática.
  - **Solución:** Implementar `pre-commit` hooks. Configurar herramientas como `black` (formateador de código), `isort` (ordenador de imports) y `flake8` (linter) para que se ejecuten automáticamente antes de cada commit, garantizando un código limpio y consistente.

- **Estructura de Proyecto Refinada:** (Mejora Pendiente)
  - **Problema:** La estructura actual es funcional, pero puede mejorar.
  - **Solución:** Crear un directorio `src/models/` para todos los modelos de Pydantic (`ScrapeResult`, etc.), separando los esquemas de datos de la lógica de negocio.

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

- **Navegadores "Sigilosos" (Stealth):** (Pendiente - Alta Prioridad)
  - **Problema:** Los navegadores automatizados dejan huellas detectables (ej. `navigator.webdriver`).
  - **Solución:** Integrar `playwright-stealth` para aplicar parches que ocultan estas huellas, superando defensas de Cloudflare, Akamai, etc.

- **Gestión de Huellas Digitales (Fingerprinting):** (Pendiente)
  - **Problema:** Usar solo User-Agents diferentes no es suficiente. Los sitios modernos analizan huellas complejas (fuentes, plugins, resolución de pantalla, WebGL, canvas).
  - **Solución:** Crear un `FingerprintManager` que genere y rote perfiles de navegador completos y consistentes. Esto implica modificar no solo cabeceras, sino también ejecutar JS al inicio de cada página para falsear propiedades como `screen.width`, `navigator.plugins`, etc.

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

## Registro de Cambios (Changelog)

*Se mantiene el changelog existente.*
