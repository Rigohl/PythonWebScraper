# IA_SYNC Log

Canal de sincronización continuo entre IA-A (orquestación/adaptación) e IA-B (mejoras, refactor, extensiones).

## Convenciones

- Formato de entrada: `YYYY-MM-DD HH:MM UTC | <TAG> | <RESUMEN CORTO>`
- Tags principales:
  - FEAT: Nueva característica implementada
  - FIX: Corrección / bugfix
  - ADAPT: Cambio heurístico / aprendizaje
  - RISK: Riesgo identificado
  - TODO: Próxima acción recomendada para la otra IA
  - NOTE: Observación contextual
- Sección "Estado Actual" debe reflejar snapshot resumido reutilizable.
- Mantener documento Append-Only (no reescribir histórico salvo para aclarar).

## Estado Actual (Snapshot)

- Brain integrado en prioridad de URL (pesos: ML promise \* -5 + Brain.priority \* -3, backoff +5)
- Captura de `response_time` por URL y persistencia ligera JSON (`data/brain_state.json`).
- Panel TUI Brain mostrando: visitas, éxito%, error%, link yield, prioridad, eventos recientes.
- Backoff adaptativo: dominios con `should_backoff` inflan prioridad (se procesan más tarde).
- Próximas mejoras sugeridas: reglas de override externas, persistencia versión heurística, panel de anomalías.

## Hooks Disponibles

- Ajustar pesos Brain en `_calculate_priority` (`src/orchestrator.py`).
- Modificar criterio de backoff en `Brain.should_backoff` (`src/intelligence/brain.py`).
- Enriquecer eventos: añadir campos (p.ej. `http_status_code`, `content_type`).
- UI: insertar pestaña adicional para anomalías o RL si se activa.

## Últimas Entradas

2025-09-04 14:10 UTC | FEAT | Brain integrado al cálculo de prioridad y backoff
2025-09-04 14:12 UTC | FEAT | Captura de response_time y registro en eventos Brain
2025-09-04 14:15 UTC | FEAT | Panel BrainStats añadido a TUI (dominios + últimos 10 eventos)
2025-09-04 14:16 UTC | ADAPT | Backoff dinámico: dominios con alto error_rate reciben penalización +5 prioridad
2025-09-04 14:18 UTC | TODO | Añadir override config: `config/brain_overrides.json` (si existe, ajustar pesos)
2025-09-04 14:20 UTC | TODO | Exponer métricas Brain vía CLI flag `--brain-snapshot` para IA-B análisis offline

## Riesgos / Observaciones

- Si la cola inicial contiene múltiples dominios, actual penalización puede retrasar recuperación de dominios inicialmente fallidos (considerar decaimiento temporal).
- Falta expiración de eventos antiguos en estadísticas agregadas (sesgo histórico) – posible ventana rodante futura.
- TUI: si snapshot muy grande, riesgo de parpadeo (actualmente limitado a últimos 10 eventos, mitigado).

## Próximas Acciones Sugeridas para IA-B

1. Implementar `brain_overrides.json` (estructura: `{ "priority_weight_success": 0.6, "priority_weight_link": 0.4 }`).
2. Añadir métrica rolling de éxito en ventana (p.ej. últimos 50 eventos por dominio) para decisiones más reactivas.
3. Incluir export CLI: `python -m src.main --brain-snapshot out.json` para integración analítica.
4. Integrar gating de dominios en cola (saltarlos N ciclos si backoff severo) en lugar de sólo inflar prioridad.
5. Validar persistencia incremental (flush periódico cada N eventos) para minimizar pérdida ante fallo.

---
(Continuar agregando entradas debajo de esta línea)

2025-09-04 20:48 UTC | FEAT | Sistema híbrido IA-A + IA-B activado (HybridBrain con overrides cargados)
2025-09-04 20:48 UTC | FEAT | Flag CLI --brain-snapshot disponible (exporta JSON unificado)
2025-09-04 20:48 UTC | ADAPT | Métricas híbridas integradas al callback de estadísticas del orquestador
2025-09-04 20:48 UTC | NOTE | Ajustada compatibilidad con AutonomousLearningBrain (parámetro data_path y atributos reales)
2025-09-04 20:48 UTC | TODO | Añadir rolling windows y gating real (saltos temporales) usando overrides futuros
2025-09-04 20:48 UTC | TODO | Enriquecer snapshot con ventana rolling de errores y éxito por dominio
2025-09-04 20:51 UTC | FEAT | IA-B: Launcher .bat actualizado (opción 11: snapshot JSON), TUI corregido (ScraperTUIApp)
2025-09-04 20:51 UTC | FEAT | IA-B: Comunicación híbrida validada - Brain (events) + AutonomousLearningBrain (sessions)
2025-09-04 20:51 UTC | NOTE | IA-B: Sistema funcional listo para trabajo colaborativo continuo
2025-09-05 03:02 UTC | START | IA-A: run started urls=1 concurrency=5
2025-09-05 03:03 UTC | END | IA-A: run completed
