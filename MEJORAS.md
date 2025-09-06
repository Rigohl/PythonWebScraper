# Mejoras aplicadas por etapas

## Etapa 1 — Adapters

- Refactor:
  - Añadido `__all__` y configuración de logger en `src/adapters/__init__.py`.
  - Añadidos tests en `tests/test_adapters.py` para `MockBrowserAdapter`, `HttpxAdapter` (con cliente mock), `OfflineLLMAdapter` y `MockLLMAdapter`.
- Mejoras:
  - Adapters ahora tienen manejo de errores más explícito y logging uniforme.
  - Se añadió un `NullHandler` por defecto para evitar warnings cuando no hay logging configurado.
- Próximos pasos:
  - Ejecutar tests automáticos y corregir fallos.

