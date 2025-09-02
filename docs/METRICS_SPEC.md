# Metrics Specification (Draft)

## 1. Objetivos

Definir base mínima de métricas para: salud del crawler, eficiencia de extracción, calidad de contenido y efectividad de mitigaciones/adaptaciones.

## 2. Dimensiones Clave

- Dominio
- Status (SUCCESS / FAILED / RETRY / DUPLICATE / LOW_QUALITY / EMPTY)
- Content Type (PRODUCT / BLOG_POST / ARTICLE / GENERAL / UNKNOWN)

## 3. Métricas Propuestas

| Nombre | Tipo | Labels | Descripción | Fuente | Frecuencia |
|--------|------|--------|-------------|--------|------------|
| `crawler_pages_total` | Counter | domain,status | Total de resultados procesados | Orchestrator `_update_domain_metrics` | Each page |
| `crawler_active_queue` | Gauge | domain | Tamaño cola pendiente (snapshot) | Orchestrator | Periodic / event |
| `crawler_backoff_factor` | Gauge | domain | Backoff actual adaptativo | Orchestrator domain_metrics | Cambio/anomalía |
| `crawler_content_length` | Histogram | content_type | Distribución longitud contenido limpio | Scraper `_process_content` | Each success |
| `crawler_fetch_latency_seconds` | Histogram | domain | Latencia de navegación (goto+networkidle) | Scraper timing | Each page |
| `crawler_duplicate_ratio` | Gauge | domain | Ratio duplicados sobre total | Post-cálculo (scan) | Periodic (batch) |
| `crawler_visual_change_distance` | Histogram | domain | Distancia perceptual entre hashes | Orchestrator `_check_for_visual_changes` | On change |
| `crawler_api_calls_captured_total` | Counter | domain | APIs JSON descubiertas | Scraper listener | Each capture |
| `crawler_rl_reward` | Histogram | domain | Recompensas RL emitidas | Orchestrator `_perform_rl_learning` | On learning |

## 4. Export / Backend

- Inicial: log estructurado JSON por línea (para parse externo).
- Futuro: Prometheus client (async safe) / OpenTelemetry metrics API.

## 5. Plan de Instrumentación Fases

| Fase | Alcance | Entregable |
|------|---------|-----------|
| 1 | Counters básicos + gauges queue/backoff (logging) | Hook en orchestrator + scraper |
| 2 | Histograms de latencia y tamaño | Agregar buckets estándar (P50,P90,P99) |
| 3 | Export Prometheus / OTEL | Endpoint /push gateway opcional |
| 4 | Alertas derivadas | Reglas: alto ratio duplicados, latencia P95>threshold |

## 6. Riesgos / Consideraciones

- Bloqueos: instrumentación synchronous en puntos críticos -> usar colas buffer si se añade IO.
- Cardinalidad: evitar label `url`; usar `domain`.
- Costo: hashing visual ya hecho; reutilizar distancia sin recálculo.

## 7. Variables de Entorno Relevantes (sitecustomize / settings)

- `ROBOTS_ENABLED`, `ETHICS_CHECKS_ENABLED`, `OFFLINE_MODE`, `FAST_TEST_MODE` (controlan comportamiento condicional).

## 8. Próximos Pasos

- Definir módulo `metrics.py` (no implementado aún) con interfaz mínima (counter/gauge/increment/observe) y backend null.
