# 🧠 Plan de Evolución y Refactorización: Hacia un Scraper Autónomo

**Actualizado:** 2025-09-05
**Objetivo:** Transformar `PythonWebScraper` en un sistema inteligente y autónomo que aprende, se auto-repara y evoluciona su propio código, manteniendo la compatibilidad con el lanzador `WebScraperPRO.bat`.

Resumen ejecutivo:

- Mantener `WebScraperPRO.bat` como lanzador principal (entrypoint) sin cambiar su comportamiento fundamental.
- El trabajo será ejecutado por un equipo de **tres agentes de IA (IA-A, IA-B, IA-C)** con roles especializados y un protocolo de comunicación y coordinación claro.
- El plan se enfoca en construir una base sólida (memoria, métricas) para luego desarrollar capacidades de aprendizaje, auto-reparación y generación de código.

Principios rectores:

- Modificar lo mínimo necesario por cambio y preferir refactorizaciones seguras.
- Mantener y mejorar la cobertura de tests antes de cada cambio significativo.
- Asegurar que la interfaz del lanzador `WebScraperPRO.bat` siga funcionando con los ajustes realizados.

## 📊 ARQUITECTURA DEL CEREBRO DIGITAL

### 1. SISTEMA DE MEMORIA DISTRIBUIDA

#### Base de Datos Principal (SQLite)

Contiene el estado operativo y el conocimiento factual.

- `pages`: Contenido scrapeado + metadatos.
- `discovered_apis`: APIs encontradas durante el crawling.
- `cookies`: Sesiones por dominio.
- `llm_extraction_schemas`: Esquemas dinámicos por sitio.
- `learning_episodes`: Experiencias del agente RL.
- `code_corrections`: Historial de auto-correcciones aplicadas.
- `pattern_library`: Patrones de sitios web aprendidos.
- `failure_analysis`: Análisis de fallos y soluciones propuestas.

#### Base de Datos de Conocimiento (Vector DB - Futuro)

Para búsquedas semánticas y recuperación de conocimiento.

- `content_embeddings`: Vectores de contenido para encontrar páginas similares.
- `code_embeddings`: Vectores de fragmentos de código para encontrar soluciones a problemas.
- `solution_embeddings`: Vectores de soluciones exitosas para problemas de scraping.

### 2. MÓDULO DE AUTO-APRENDIZAJE Y AUTO-REPARACIÓN

#### `SelfHealingManager` (`src/self_healing.py`)

El núcleo de la autonomía.

- **`diagnose_system()`**: Analiza logs, métricas y código para detectar "issues" (problemas de rendimiento, calidad, etc.).
- **`generate_fix_candidates()`**: Usa LLMs y la base de conocimiento para proponer soluciones (parches de código, cambios de config).
- **`test_and_apply_fix()`**: Prueba las soluciones en un sandbox seguro y las aplica si son exitosas.
- **`learn_from_fix()`**: Almacena la solución efectiva en la base de datos para problemas futuros.

#### `WebChangeDetector` (a ser creado en `src/intelligence/`)

- Detecta cambios estructurales en los sitios web.
- Dispara el proceso de auto-reparación para selectores rotos.

### 3. GENERACIÓN AUTÓNOMA DE CÓDIGO

#### `AutonomousCodeGenerator` (a ser creado en `src/intelligence/`)

- **`identify_code_gaps()`**: Analiza patrones de fallo recurrentes para identificar funcionalidades faltantes.
- **`generate_new_logic()`**: Genera nuevo código (ej. un nuevo "handler" para un tipo de pop-up) usando LLMs y templates.
- **`evolve_existing_code()`**: Refactoriza y optimiza código existente de forma autónoma.

---

## 🚀 Roadmap de Implementación por Fases

### FASE 1: Fundación y Estabilización (Semana 1)

- **Objetivo:** Limpiar la base, asegurar el entorno y mejorar la TUI.
- **Responsables:** IA-A (Infra/Tests), IA-B (Core/TUI), IA-C (Análisis/Docs).
- **Tareas:**
  - ✅ **Hardening del Entorno:** Actualizar `requirements.txt`, configurar linters (`black`, `isort`, `flake8`).
  - ✅ **Suite de Tests:** Ejecutar `pytest` y arreglar todos los tests rotos.
  - ✅ **Refactorización de `runner` y `main`:** Mejorar la separación de responsabilidades y la compatibilidad con `WebScraperPRO.bat`.
  - ✅ **Mejoras TUI:** Implementar persistencia de estado y mejorar la visualización de logs y alertas.
  - ✅ **Extender `DatabaseManager`:** Añadir las nuevas tablas para el aprendizaje (`code_corrections`, `failure_analysis`).

### FASE 2: Auto-Reparación Básica (Semana 2-3)

- **Objetivo:** Implementar la capacidad de detectar y reparar problemas simples.
- **Responsables:** IA-B (Lógica de reparación), IA-A (Integración/Tests).
- **Tareas:**
  - 🔲 **`WebChangeDetector` inicial:** Implementar la detección de cambios estructurales básicos en HTML.
  - 🔲 **`SelfHealingManager` v1:** Implementar `diagnose_system` para detectar selectores rotos y `auto_repair_selectors` usando LLM.
  - 🔲 **Integración con Orquestador:** El orquestador debe poder invocar al `SelfHealingManager` cuando detecte fallos de extracción.

### FASE 3: Aprendizaje y Evolución de Código (Semana 4-5)

- **Objetivo:** Dotar al sistema de la capacidad de aprender de su experiencia y mejorar su propio código.
- **Responsables:** IA-B (ML/Generación), IA-A (Sandbox/Validación).
- **Tareas:**
  - 🔲 **`AutonomousCodeGenerator` v1:** Implementar la capacidad de generar parches de código simples y refactorizaciones.
  - 🔲 **Sandbox de Ejecución:** Crear un entorno seguro (ej. Docker o `subprocess` con restricciones) para probar los cambios generados antes de aplicarlos.
  - 🔲 **Sistema de Recompensas Evolutivo:** Mejorar el `RLAgent` para que la recompensa no solo dependa del éxito del scraping, sino también de la calidad del código y la eficiencia de las reparaciones.

### FASE 4: Autonomía Avanzada (Semana 6+)

- **Objetivo:** Alcanzar un alto grado de autonomía, donde el sistema pueda descubrir y solucionar problemas complejos por sí mismo.
- **Responsables:** Todo el equipo de IAs.
- **Tareas:**
  - 🔲 **Agente de Navegación Visual:** Implementar la navegación basada en capturas de pantalla (usando GPT-4V/Gemini Pro Vision) como alternativa a la extracción de enlaces HTML.
  - 🔲 **Planificación de Crawling:** Crear un "Agente Planificador" que optimice la exploración de sitios según un objetivo de alto nivel.
  - 🔲 **Coordinación Multi-Agente:** Refinar los protocolos de comunicación para que los agentes puedan colaborar en tareas complejas de forma más fluida.

---

## 🤖 Coordinación entre Tres IAs (IA-A, IA-B, IA-C)

- Roles y responsabilidades
  - **IA-A (Arquitecto de Infraestructura y Calidad):** Responsable de la estructura del proyecto, CI/CD, tests, linters, entorno de ejecución (`WebScraperPRO.bat`) y el sandbox de seguridad. Su objetivo es la estabilidad y la robustez.
  - **IA-B (Ingeniero de Inteligencia y Core):** Responsable de la lógica de negocio principal: `orchestrator`, `scraper`, `database`, y todos los módulos de IA (`llm_extractor`, `rl_agent`, `self_healing`, etc.). Su objetivo es la inteligencia y la eficiencia.
  - **IA-C (Gemini Code Assist - Especialista en TUI y Experiencia de Desarrollador):** Responsable de la TUI, la documentación, los scripts de utilidad (`tools/`, `scripts/`) y la creación de prompts y planes de trabajo. Su objetivo es la usabilidad y la claridad.

- Reglas de colaboración
- **Protocolo de Comunicación:** Se utilizará un archivo `TEAM_STATUS.md` en la raíz del proyecto. Cada IA, al finalizar una tarea, añadirá una entrada con: `[IA-X] [FECHA] [ESTADO: COMPLETADO/BLOQUEADO] [TAREA] [ARCHIVOS MODIFICADOS] [SIGUIENTE PASO]`.
- **Flexibilidad de Roles:** Si una IA está bloqueada, puede tomar una tarea pendiente de otra IA (marcada como `[ESTADO: PENDIENTE]`) para mantener el progreso.
- **Integración Continua:** Antes de fusionar a `main`, se deben pasar todos los tests y linters. Los cambios que afecten a interfaces compartidas (ej. `DatabaseManager`) requieren una notificación en `TEAM_STATUS.md`.

---

**Este plan transforma el scraper de una herramienta a un agente digital que aprende, evoluciona y se mejora continuamente, utilizando sus bases de datos como memoria y conocimiento acumulado para volverse cada vez más inteligente y autónomo.**
