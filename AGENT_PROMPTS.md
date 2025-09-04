# Prompts de Misión para Asistentes de IA

Usa estos prompts para iniciar las sesiones de trabajo con cada asistente.

---

## Prompt para el Asistente 1

**Objetivo:** Iniciar el trabajo en los paquetes de refactorización asignados.

```
Actúa como un ingeniero de software de clase mundial. Somos un equipo de dos asistentes de IA colaborando para refactorizar un proyecto de web scraping.

Nuestro plan de trabajo está en el archivo `REFACTOR_PLAN.md`. Tu rol es "Asistente 1".

Tu primera misión es tomar el **Paquete de Trabajo P01 (Núcleo de Orquestación)**.

Realiza una refactorización completa de los archivos `orchestrator.py`, `runner.py` y `main.py`. Tu trabajo debe incluir:
1.  Aplicar formato con `black` e `isort`.
2.  Corregir cualquier error lógico o "code smell" que encuentres.
3.  Mejorar la legibilidad y añadir los comentarios que sean necesarios.
4.  Asegurar que todas las `datetime` usen `timezone.utc`.

Cuando termines, proporciona un `diff` con todos tus cambios y actualiza el estado del paquete P01 a `LISTO PARA REVISIÓN` en `REFACTOR_PLAN.md` para que tu compañero (Asistente 2) pueda revisar tu trabajo.
```

---

## Prompt para el Asistente 2 (Gemini)

**Objetivo:** Iniciar el trabajo en los paquetes de refactorización asignados.

```
Actúa como un ingeniero de software de clase mundial. Somos un equipo de dos asistentes de IA colaborando para refactorizar un proyecto de web scraping.

Nuestro plan de trabajo está en el archivo `REFACTOR_PLAN.md`. Tu rol es "Asistente 2 (Gemini)".

Tu primera misión es tomar el **Paquete de Trabajo P04 (Utilidades y Managers)**.

Realiza una refactorización completa de los archivos `proxy_manager.py`, `user_agent_manager.py` y `fingerprint_manager.py`. Tu trabajo debe incluir:
1.  Aplicar formato con `black` e `isort`.
2.  Hacer que los managers sean **thread-safe** usando `threading.Lock` para proteger el estado compartido.
3.  Asegurar que todas las `datetime` usen `timezone.utc`.
4.  Mejorar la robustez y la legibilidad del código.

Cuando termines, proporciona un `diff` con todos tus cambios y actualiza el estado del paquete P04 a `LISTO PARA REVISIÓN` en `REFACTOR_PLAN.md` para que tu compañero (Asistente 1) pueda revisar tu trabajo.
```
