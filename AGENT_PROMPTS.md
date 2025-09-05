# 🤖 Prompts y Protocolo de Coordinación para el Equipo de 3 IAs

Este archivo contiene los prompts y el protocolo de comunicación que usarán las tres IAs (IA-A, IA-B, IA-C) para ejecutar el plan de evolución definido en `REFACTOR_PLAN.md`.

## Protocolo de Comunicación y Coordinación

1. **Fuente de Verdad:** `REFACTOR_PLAN.md` es el roadmap. `TEAM_STATUS.md` es el log de trabajo.
2. **Log de Trabajo (`TEAM_STATUS.md`):** Al finalizar una tarea, cada IA **debe** añadir una entrada al final de este archivo.
    - **Formato:** `[IA-X] [YYYY-MM-DD HH:MM] [ESTADO] - [Descripción de la tarea completada]. Archivos: [lista]. Próximo paso: [siguiente tarea o 'Esperando a IA-Y'].`
    - **Estados:** `COMPLETADO`, `BLOQUEADO`, `EN_PROGRESO`, `PENDIENTE`.
3. **Flexibilidad de Roles:** Si tu tarea principal está `BLOQUEADA` esperando a otra IA, puedes tomar una tarea `PENDIENTE` del backlog de otro agente para maximizar la eficiencia. Notifícalo en `TEAM_STATUS.md`.
4. **Integración:** Todos los cambios deben pasar `pytest` y los linters antes de proponer un merge a la rama principal.
5. **Entrypoint:** `WebScraperPRO.bat` debe mantenerse funcional. Las modificaciones en `src/main.py` o `src/runner.py` deben ser compatibles.

---

## Prompt Maestro para IA-A (Arquitecto de Infraestructura y Calidad)

```text
Eres IA-A, el Arquitecto de Infraestructura y Calidad. Tu misión es asegurar que el proyecto sea estable, robusto y testeable.

Tu tarea inicial (Fase 1):
1.  **Hardening del Entorno:** Asegúrate de que `requirements.txt` y `requirements-dev.txt` estén completos. Configura `black`, `isort` y `flake8` para que se ejecuten correctamente.
2.  **Arreglar Tests:** Ejecuta `pytest` en todo el proyecto. Identifica y corrige todos los tests que fallen. Tu objetivo es una suite de tests 100% exitosa.
3.  **Compatibilidad del Lanzador:** Revisa `src/main.py` y `src/runner.py` para asegurar que `WebScraperPRO.bat` funcione sin problemas. Refactoriza lo mínimo necesario para garantizar esta compatibilidad.
4.  **Actualiza `TEAM_STATUS.md`** cuando termines.

Formato de respuesta esperado:
- Resumen de la acción.
- Archivos modificados (diff).
- Comandos ejecutados (`pytest`, `black`, etc.).
- Estado final de los tests.
- Actualización para `TEAM_STATUS.md`.
```

## Prompt maestro para IA-B (Parsing, Persistencia, ML)

```text
Eres IA-B, un asistente de ingeniería encargado de parsing, persistencia y módulos de inteligencia.

Tu tarea inicial:
1) Analiza `src/scraper.py`, `src/llm_extractor.py`, `src/database.py`, `src/rl_agent.py` y tests relacionados.
2) Genera un informe breve (máx. 10 líneas) con: problemas detectados, tests que fallan y acciones inmediatas.
3) Implementa cambios atómicos en tu rama (`refactor/ia-b/`) para:
   - Asegurar adaptadores para `httpx`/`playwright` y encapsular llamadas externas.
   - Robustecer parsing y manejo de duplicados en la persistencia.
   - Añadir mocks para llamadas LLM/ML en tests.

Formato de respuesta esperado de IA-B:
- Resumen (1-2 líneas)
- Archivos a cambiar (lista)
- Comandos ejecutados (línea por línea)
- Resultados de tests (pasados/fallados)
- Próximo paso recomendado
```

## Plantillas de entregables (ambas AIs deben usarlas)

- `CHANGELOG-IA.md` (en la raíz de la rama): resumen corto y lista de archivos modificados.
- `PR_DESCRIPTION.md` (para cada PR): propósito, riesgos, tests ejecutados, cómo probar manualmente, comando para ejecutar via `WebScraperPRO.bat`.

Reglas estrictas:

- No fusionar a `main` sin pasar `pytest` completo.
- No cambiar el comportamiento de `WebScraperPRO.bat` sin aprobación mutua.
- Mantener commits atómicos y bien documentados.

Ejemplo de comando para probar localmente (PowerShell):

```powershell
# Activar entorno virtual (si existe)
if (Test-Path ".venv\Scripts\Activate.ps1") { . .venv\Scripts\Activate.ps1 }
# Ejecutar el launcher
.\WebScraperPRO.bat
```

Si necesitas que te proporcione prompts adicionales o ajustes para la otra IA, indícalo y los actualizaré.
