# Mejoras y Próximas Fases del Proyecto

Este documento detalla las mejoras y las próximas fases planificadas para el proyecto de web scraping, estructuradas por áreas funcionales y etapas de desarrollo.

---

## Fase 1: Core de Navegación y Extracción

-   **Integración de Playwright en Docker (RESUELTO)**:
    *   **Problema**: Dificultades para ejecutar Playwright dentro de un contenedor Docker debido a dependencias de navegador.
    *   **Solución (Implementada)**: Se ha configurado Dockerfile y las dependencias para asegurar la ejecución estable de Playwright en un entorno contenedorizado.
-   **Rotación de User-Agents y Fingerprinting Avanzado (EN PROGRESO)**:
    *   **Problema**: Detección y bloqueo por parte de sitios web debido a huellas digitales de navegador consistentes.
    *   **Mejora**: Implementar una estrategia dinámica de rotación de User-Agents y técnicas de fingerprinting avanzado (p. ej., WebGL, Canvas, etc.) para emular un comportamiento de usuario real y evitar la detección.
    *   **Solución Actual**: Se ha implementado la rotación de User-Agents basada en el archivo `user_agents.json` para cada worker de Playwright. Pruebas iniciales sugieren que mejora la resistencia a la detección.
-   **Manejo Inteligente de Cookies y Sesiones (COMPLETADO)**:
    *   **Problema**: La gestión actual de cookies es básica, lo que puede limitar el acceso a contenido protegido o personalizado.
    *   **Mejora**: Desarrollar un sistema para persistir y rotar cookies y sesiones por dominio, permitiendo mantener sesiones activas y sortear sistemas de autenticación o límites de acceso.
    *   **Solución Implementada**: Se ha implementado la persistencia y carga de cookies por dominio utilizando `src/database.py` y `src/scraper.py`. Las cookies se guardan después de un scrapeo exitoso y se cargan antes de navegar a una URL del mismo dominio, mejorando la capacidad de mantener sesiones.

---

## Fase 2: Robustez y Escalabilidad

-   **Gestión de Proxies Robusta (EN PROGRESO)**:
    *   **Problema**: La dependencia de un único proxy o una lista estática reduce la fiabilidad y escalabilidad.
    *   **Mejora**: Implementar un `ProxyManager` que soporte múltiples fuentes de proxies (p. ej., rotación de proxies residenciales, integración con servicios de terceros), con lógica de reintento y exclusión de proxies defectuosos.
    *   **Solución Actual**: Se ha implementado un `ProxyManager` que carga proxies desde `proxies.txt` y los asigna a los workers. Se necesita mejorar la lógica de reintento y validación.
-   **Reintentos Adaptativos con Backoff Exponencial (PLANIFICADO)**:
    *   **Problema**: Fallos intermitentes en la red o en el servidor web pueden causar interrupciones innecesarias.
    *   **Mejora**: Implementar una lógica de reintentos con backoff exponencial y jitter para manejar fallos temporales de manera más eficiente y menos intrusiva.
-   **Manejo de Errores y Retries Específicos de Scraper (PLANIFICADO)**:
    *   **Problema**: Los errores durante el scraping pueden ser variados (p. ej., CAPTCHAs, errores de renderizado).
    *   **Mejora**: Permitir a cada `BaseScraper` definir estrategias de reintento o manejo de errores específicas para su dominio o tipo de contenido.

---

## Fase 3: Detección y Evasión

-   **Manejo de CAPTCHAs y Detección de Bots (PLANIFICADO)**:
    *   **Problema**: Los sitios web utilizan CAPTCHAs y otras técnicas para detectar y bloquear bots.
    *   **Mejora**: Investigar y posiblemente integrar servicios de resolución de CAPTCHAs (p. ej., 2Captcha, Anti-Captcha) o desarrollar modelos de aprendizaje automático para la detección y evasión de patrones de bloqueo.
-   **Adaptación a Cambios de UI/HTML (PLANIFICADO)**:
    *   **Problema**: Los cambios frecuentes en la estructura HTML de los sitios web rompen los scrapers existentes.
    *   **Mejora**: Desarrollar un enfoque más resiliente para la extracción de datos, posiblemente utilizando selectores más robustos (p. ej., atributos en lugar de clases), o técnicas de Computer Vision/LLM para identificar elementos de forma semántica.

---

## Fase 4: Inteligencia y Extracción de Datos

-   **Esquemas de Extracción LLM Flexibles/Aprendidos (PLANIFICADO)**:
    *   **Problema**: El esquema de extracción LLM se define actualmente de forma estática en `_process_page`. La visión del proyecto sugiere una "estrategia óptima por dominio", lo que implica adaptabilidad.
    *   **Mejora**: Permitir que los esquemas de extracción LLM sean dinámicos y configurables por dominio/URL, posiblemente almacenados en la base de datos, o desarrollar una lógica para que el sistema "aprenda" o adapte el esquema basándose en el contenido o el dominio.

---

## Fase 5: Experiencia de Usuario y Observabilidad

-   **Dashboard en Tiempo Real:** (En Progreso)
    -   **Solución:** Se ha implementado una pestaña de "Estadísticas en Vivo" en la TUI con métricas globales.
-   **Alertas y Notificaciones (PLANIFICADO)**:
    *   **Problema**: La falta de notificación sobre problemas críticos (p. ej., bloqueo de IP, fallos de scraping) puede llevar a interrupciones prolongadas.
    *   **Mejora**: Implementar un sistema de alertas (p. ej., por correo electrónico, Slack) para notificar sobre eventos importantes o errores.
-   **Persistencia de Estado de la TUI (PLANIFICADO)**:
    *   **Problema**: La configuración y el estado de la TUI se pierden al reiniciar la aplicación.
    *   **Mejora**: Permitir guardar y cargar la configuración de la TUI para mantener el estado entre sesiones.
