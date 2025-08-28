# Plan de Acción para la Evolución del Scraper

Este documento es una guía paso a paso para implementar las mejoras definidas en `MEJORAS.MD`. Cada sección representa una tarea fundamental que se puede solicitar a Gemini Code Assist con prompts específicos.

## Fase 1: Excelencia Operativa y Deuda Técnica

- [x] **1.1: Calidad de Código Automatizada:** Configurar `pre-commit` con `black`, `isort` y `flake8`.
- [x] **1.2: Estructura de Proyecto Refinada:** Mover `ScrapeResult` a `src/models/results.py`.
- [x] **1.3: Manejo de Errores Centralizado:**
  - [x] Crear `src/exceptions.py`.
  - [x] Refactorizar `src/scraper.py` para lanzar excepciones personalizadas.
  - [x] Refactorizar `src/orchestrator.py` para manejar excepciones personalizadas.
- [x] **1.4: Suite de Pruebas Exhaustiva:**
  - [x] Configurar `pytest` y crear `tests/conftest.py`.
  - [x] Crear `tests/test_scraper.py` con pruebas de extracción y calidad.
  - [x] Crear `tests/test_orchestrator.py` con mocks para probar la lógica de orquestación.
- [ ] **1.5: Gestión de Configuración Avanzada:** Refactorizar `src/config.py` para usar `pydantic-settings`.

---

## Fase 3: Evasión de Nivel Humano

- [x] **3.1: Navegadores "Sigilosos":** Integrar `playwright-stealth`.
- [ ] **3.2: Gestión de Huellas Digitales (Fingerprinting):**
  - [ ] Crear `src/fingerprint_manager.py`.
  - [ ] Integrar `FingerprintManager` en el orquestador para aplicarlo a cada página.

---
