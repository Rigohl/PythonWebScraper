# TEAM STATUS (IA-A -> IA-B)

## Resumen Actual

- Orquestador estable con RL opcional y ahora módulo Brain adaptativo.
- Faltaba export fix: solucionado (se eliminó await erróneo en export CSV/JSON).
- Tests CLI de export pasan; integración previa OK.
- Nuevo módulo `Brain` registra eventos (éxitos, duplicados, errores) y calcula heurísticas dominio.
- Orchestrator ahora registra cada resultado en Brain (content_length, new_links, extracted_fields).

## Archivos Clave

- `src/main.py`: CLI (crawl, tui, demo, export-csv/json) – export usa `asyncio.to_thread`.
- `src/orchestrator.py`: Integrado `brain` opcional + registro de ExperienceEvent y flush final.
- `src/intelligence/brain.py`: Estado incremental + heurísticas (success_rate, link_yield, backoff hints).
- `src/database.py`: Export sync, deduplicación exacta y fuzzy.
- `src/runner.py`: Punto de entrada programático para crawling.

## Próximos Pasos Propuestos

1. TUI: Exponer métricas Brain (top_domains, error spikes) en panel lateral.
2. Prioridad Dinámica: Ajustar `_calculate_priority` usando `brain.domain_priority(domain)` si Brain activo.
3. Backoff Inteligente: Combinar `brain.should_backoff(domain)` con RL/backoff actual.
4. Persistencia Avanzada: Añadir rotación de `brain_state.json` (>1MB) y compresión opcional.
5. Métricas Prometheus (opcional): Exportar snapshot Brain vía endpoint HTTP.
6. Entrenamiento RL Híbrido: Usar heurísticas Brain como shaping reward adicional.

## Hooks Sugeridos

- `ScrapingOrchestrator._calculate_priority`: inyectar factor multiplicador.
- `ScrapingOrchestrator._scrape_with_retries`: medir response_time y actualizar en Brain.
- `ScrapingOrchestrator._add_links_to_queue`: antes de enqueuer, filtrar dominios en backoff Brain.

## Riesgos / Observaciones

- Import path legacy (`from .db.database`) mantenido; verificar que ruta espejo existe.
- Brain actualmente no es thread-safe—si se añade multiprocessing deberá protegerse.
- Response time aún no medido (placeholder None) – requiere timestamp start/stop en worker.

## Señales Disponibles (Brain.snapshot())

```json
{
  "domains": {"example.com": {"visits": 3, "success": 3, ...}},
  "top_domains": ["example.com"],
  "error_type_freq": {"network": 2},
  "recent_events": [...]
}
```

## Acción Inmediata Recomendada (IA-B)

- Integrar visualización en TUI.
- Añadir medición de `response_time` (wrap scrape in perf timer).
- Ajustar prioridad con Brain antes de poner en queue.

-- IA-A ✅

# TEAM STATUS LOG

[IA-C] [2025-09-04 12:00] [COMPLETADO] - He completado la refactorización inicial a una arquitectura de scrapers modulares. El sistema ahora carga dinámicamente los scrapers del directorio `src/scrapers`. Se ha implementado un scraper base y un scraper de ejemplo para `toscrape.com`. También se ha configurado un logging estructurado en JSON. Archivos: `src/scrapers/__init__.py`, `src/scrapers/base.py`, `src/scrapers/toscrape_scraper.py`, `src/runner.py`, `src/main.py`. [IA-C] [2025-09-04 12:01] [COMPLETADO] - Eliminado el archivo obsoleto src/scraper.py como parte de la limpieza final de la refactorización. Archivos: src/scraper.py. Próximo paso: Esperando revisión y tareas de la Fase 2.

[IA-B] [2025-09-04 12:30] [EN_PROGRESO] - Iteración inicial: ampliado prompt IA-B, añadido adaptador httpx resiliente (`src/adapters/httpx_adapter.py`), configuración `DUP_SCAN_LIMIT` en `settings.py`, utilitario de métricas (`src/metrics_persistence.py`) y tests de adapter (`tests/test_httpx_adapter.py`). Pytest interrumpido por carga pesada de dependencias RL (stable_baselines3/torch) -> se requiere aislar import de RL en tests o marcar skip condicional. Archivos: `AGENT_PROMPTS.md`, `src/adapters/httpx_adapter.py`, `src/settings.py`, `src/metrics_persistence.py`, `tests/test_httpx_adapter.py`. Próximo paso: Aislar carga RL para acelerar suite y re‑ejecutar pytest.
