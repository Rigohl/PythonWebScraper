# Schema Evolution (Draft)

## 1. Inventario Actual

### Tablas Reales (214 pages, 1 cookies):

**pages** (21 columnas):
- id (INTEGER, PRIMARY KEY)
- status, url, scraped_at, scraper_version (TEXT)
- title, content_text, content_html, links, extracted_data, healing_events (TEXT)
- content_hash, visual_hash, normalized_content_hash (TEXT) 
- error_message (TEXT), retryable (BOOLEAN)
- http_status_code (BIGINT), content_type (TEXT)
- crawl_duration (FLOAT)
- llm_summary, llm_extracted_data (TEXT)

**cookies** (4 columnas):
- id (INTEGER, PRIMARY KEY)
- domain, cookies (TEXT)
- timestamp (DATETIME)

### Índices Existentes:
- `ix_pages_81736358b1645103` ON pages(url)  
- `ix_cookies_9120580e94f134cb` ON cookies(domain)

### Tablas Faltantes:
- discovered_apis (mencionada en código, no existe en DB)
- llm_extraction_schemas (mencionada en código, no existe en DB)

## 2. Uso y Patrones de Consulta Esperados

- Búsqueda por `url` (primary key implícita en upsert) => requiere índice único.
- Búsqueda por `content_hash` para deduplicación => índice recomendado.
- Futuro: consultas por `status`, `timestamp` para métricas y housekeeping.

## 3. Problemas Identificados (placeholder)

- Falta de índice compuesto (`status`, `timestamp`) para expiración / limpieza.
- Deduplicación fuzzy recorre tabla completa => riesgo O(N^2) creciente.

## 4. Propuesta de Migración Inicial

```sql
-- Índices recomendados
CREATE INDEX IF NOT EXISTS idx_pages_content_hash ON pages(content_hash);
CREATE INDEX IF NOT EXISTS idx_pages_status_timestamp ON pages(status, timestamp);
CREATE INDEX IF NOT EXISTS idx_pages_normalized_content_hash ON pages(normalized_content_hash);
CREATE INDEX IF NOT EXISTS idx_apis_page_url ON discovered_apis(page_url);
CREATE INDEX IF NOT EXISTS idx_cookies_domain ON cookies(domain);
```

## 5. Evolución de Esquema (Fases)

| Fase | Cambio | Objetivo | Riesgo | Mitigación |
|------|--------|----------|--------|-----------|
| 1 | Añadir índices arriba | Mejorar dedupe y queries métricas | Bajo | Crear "IF NOT EXISTS" |
| 2 | Añadir tabla `metrics_snapshots` | Histórico de métricas dominio | Bajo | Tablas separadas |
| 3 | Externalizar contenido largo a tabla `page_blobs` | Reducir ancho fila principal | Medio | Migración incremental |
| 4 | Introducir `crawl_batch_id` en pages | Agrupar ejecuciones | Bajo | Default null |

## 6. Consideraciones de Integridad

- Upserts actuales pueden sobrescribir estados; añadir `last_seen` separado de `first_seen`.
- Añadir triggers (futuro) para mantener contador de duplicados.

## 7. Próximos Pasos

- Ejecutar PRAGMA table_info y .schema para completar inventario real.
- Medir cardinalidad de `content_hash` vs `normalized_content_hash`.
