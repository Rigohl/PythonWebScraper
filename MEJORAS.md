# Mejoras y Próximas Fases del Proyecto

Este documento detalla las mejoras y las próximas fases planificadas para el proyecto de web scraping, estructuradas por áreas funcionales y etapas de desarrollo.

---

## Fase 1: Core de Navegación y Extracción

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

## Fase 2: Robustez y Escalabilidad

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

- **Dashboard en Tiempo Real (COMPLETADO)**:
  - **Solución**: Se ha implementado una pestaña de "Estadísticas en Vivo" en la TUI con métricas globales y por dominio.
- **Alertas y Notificaciones (COMPLETADO)**:
  - **Problema**: La falta de notificación sobre problemas críticos (p. ej., bloqueo de IP, fallos de scraping) podía llevar a interrupciones prolongadas.
  - **Mejora**: Implementar un sistema de alertas para notificar sobre eventos importantes o errores.
  - **Solución Implementada**: Se ha añadido un widget `AlertsDisplay` en `src/tui.py` para mostrar alertas críticas. El `ScrapingOrchestrator` ahora utiliza un `alert_callback` para enviar mensajes de alerta y su nivel (warning, error) a la TUI cuando se detectan eventos importantes como fallos persistentes, bucles de redirección, problemas de calidad de contenido o cambios visuales.
- **Persistencia de Estado de la TUI (PLANIFICADO)**:
  - **Problema**: La configuración y el estado de la TUI se pierden al reiniciar la aplicación.
  - **Mejora**: Permitir guardar y cargar la configuración de la TUI para mantener el estado entre sesiones.

