# Database Schema Evidence

**Fecha de análisis:** $(Get-Date)  
**Base de datos:** SQLite (`data/scraper_database.db`)  
**ORM:** dataset library  

## Resumen Ejecutivo

El sistema utiliza SQLite con 4 tablas principales gestionadas por `dataset` (ORM simple):
- **pages:** Datos scrapeados y metadatos 
- **discovered_apis:** APIs interceptadas
- **cookies:** Persistencia de sesiones
- **llm_extraction_schemas:** Esquemas dinámicos

## Tablas Core

### 1. Tabla `pages` (principal)

**Propósito:** Almacenar resultados de scraping con deduplicación

**Campos identificados desde ScrapeResult:**
```sql
-- Identificación y estado
status VARCHAR NOT NULL              -- "success", "failed", "retried" 
url VARCHAR NOT NULL                 -- URL fuente
scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP
scraper_version VARCHAR DEFAULT "1.0.0"

-- Contenido principal  
title VARCHAR                        -- <title> extraído
content_text TEXT                    -- Texto limpio final (post-LLM)
content_html TEXT                    -- HTML principal (readability)
links TEXT                          -- JSON array de enlaces encontrados

-- Datos estructurados
extracted_data TEXT                  -- JSON de datos semi-estructurados
healing_events TEXT                  -- JSON log de auto-correcciones
llm_extracted_data TEXT             -- JSON resultado LLM extraction
llm_summary TEXT                     -- Resumen generado por LLM

-- Hashes para deduplicación
content_hash VARCHAR(64)             -- SHA256 del contenido
normalized_content_hash VARCHAR(64)  -- Hash normalizado (sin espacios)
visual_hash VARCHAR(64)              -- Perceptual hash de screenshots

-- Métricas y metadata
http_status_code INTEGER             -- 200, 404, etc.
content_type VARCHAR                 -- "PRODUCT", "BLOG_POST", etc.
crawl_duration FLOAT                 -- Segundos de processing
error_message TEXT                   -- Error si status="failed"
retryable BOOLEAN DEFAULT FALSE      -- Si error permite retry
```

**Índices existentes:**
```sql
CREATE INDEX IF NOT EXISTS idx_pages_content_hash ON pages(content_hash);
CREATE INDEX IF NOT EXISTS idx_pages_normalized_content_hash ON pages(normalized_content_hash);
CREATE INDEX IF NOT EXISTS idx_pages_url ON pages(url);
```

### 2. Tabla `discovered_apis`

**Propósito:** Registrar APIs interceptadas durante navegación

**Esquema estimado:**
```sql
page_url VARCHAR NOT NULL           -- URL de la página que realizó la llamada
api_url VARCHAR NOT NULL            -- URL de la API interceptada  
payload_hash VARCHAR(64) NOT NULL   -- Hash del payload/body
timestamp DATETIME DEFAULT CURRENT_TIMESTAMP

-- Composite key: (page_url, api_url, payload_hash)
```

**Casos de uso:** 
- Detectar APIs GraphQL/REST
- Analizar comunicación AJAX
- Reverse-engineering de SPAs

### 3. Tabla `cookies`

**Propósito:** Persistir cookies por dominio entre sesiones

**Esquema estimado:**
```sql
domain VARCHAR NOT NULL PRIMARY KEY  -- "example.com"
cookies TEXT NOT NULL                -- JSON serializado
timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
```

**Funcionalidad:**
- Mantener sesiones autenticadas
- Bypass de cookie walls básicos
- Preservar state entre reinicios

### 4. Tabla `llm_extraction_schemas`

**Propósito:** Guardar esquemas dinámicos para extracción LLM

**Esquema estimado:**
```sql
schema_name VARCHAR NOT NULL         -- Identificador único del esquema
schema_definition TEXT NOT NULL     -- JSON Pydantic schema
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
```

**Casos de uso:**
- Esquemas de extracción personalizados
- Evolución de modelos de datos
- A/B testing de prompts

## Estrategia de Deduplicación

### Nivel 1: Hash Exacto
- `content_hash`: SHA256 del texto content_text final
- Evita crawls duplicados de misma página

### Nivel 2: Hash Normalizado  
- `normalized_content_hash`: Hash tras normalización (espacios, mayúsculas)
- Detecta contenido similar con variaciones menores

### Nivel 3: Hash Visual
- `visual_hash`: Perceptual hash de screenshots (imagehash)
- Detecta páginas visualmente idénticas con HTML diferente

### Algoritmo de Fuzzy Matching
**Ubicación:** `DatabaseManager.is_similar_content()`

```python
def is_similar_content(self, content_text: str, threshold: float = 0.8) -> bool:
    """Fuzzy deduplication usando Jaccard similarity"""
    # Iteración completa sobre tabla pages
    for existing_page in self.table.all():
        if jaccard_similarity(content_text, existing_page['content_text']) > threshold:
            return True
    return False
```

**Nota crítica:** Este algoritmo escala O(n) y se volverá inviable con >10k páginas.

## Problemas de Performance Identificados

### 1. Fuzzy Deduplication Costosa
- **Problema:** Iteración completa de tabla en cada insert
- **Impacto:** O(n) operations, bloqueo DB
- **Solución:** Índices de n-gramas o embeddings + vector search

### 2. Falta de Particionamiento  
- **Problema:** Una sola tabla `pages` para todos los dominios
- **Impacto:** Queries lentas, índices grandes
- **Solución:** Partición por dominio o timestamp

### 3. JSON sin Schema
- **Problema:** Campos `extracted_data`, `links` como TEXT/JSON
- **Impacto:** No queryable, no validado
- **Solución:** SQLite JSON1 extension o tabla relacional

## Migraciones Pendientes

### Alta Prioridad
1. **Optimizar deduplicación:** Índices de similarity o cache
2. **Agregar timestamps:** created_at, updated_at en todas las tablas
3. **Foreign keys:** Relación pages → discovered_apis

### Media Prioridad
1. **Particionamiento:** Separar por fecha/dominio
2. **JSON schema validation:** Para campos estructurados
3. **Cleanup automático:** Retention policy para páginas antiguas

### Baja Prioridad
1. **Full-text search:** FTS5 para content_text
2. **Compresión:** GZIP para content_html grandes
3. **Audit log:** Tracking de cambios y accesos

## Uso de Memoria y Disco

### Estimaciones Actuales
- **Row size promedio:** ~10KB (content_html + texto)
- **Pages por dominio:** Variable, típicamente 100-1000
- **DB size crecimiento:** ~1MB por 100 páginas scrapeadas

### Proyecciones
- **10k páginas:** ~100MB DB
- **100k páginas:** ~1GB DB  
- **1M páginas:** ~10GB DB (requiere optimizaciones)

## Comandos de Análisis Útiles

### Inspection Schema
```bash
# Dentro de la DB
sqlite3 data/scraper_database.db ".schema"
sqlite3 data/scraper_database.db ".tables"
```

### Stats de Tablas
```sql
SELECT 
    COUNT(*) as total_pages,
    AVG(LENGTH(content_text)) as avg_content_size,
    COUNT(DISTINCT content_hash) as unique_content
FROM pages;
```

### Performance Analysis
```sql
EXPLAIN QUERY PLAN 
SELECT * FROM pages WHERE content_hash = 'abc123...';
```

## Validación del Modelo

El modelo `ScrapeResult` en `src/models/results.py` define la estructura que se serializa a la tabla `pages`. Cambios en este modelo requieren:

1. **Backward compatibility:** Campos opcionales con defaults
2. **Migration script:** Para DB existentes  
3. **Test coverage:** Validar serialization/deserialization

## Recomendaciones de Seguridad

### Control de Acceso
- SQLite no tiene autenticación nativa
- Proteger archivo DB con permisos de filesystem
- Considerar encriptación con SQLCipher para datos sensibles

### Injection Prevention  
- `dataset` library usa parámetros prepared
- Validar inputs en capa aplicación (Pydantic)
- Sanitizar URLs antes de storage

### Data Governance
- Implementar retention policies (GDPR compliance)
- Log de accesos para auditorías
- Backup/restore procedures

## Performance Benchmarks

*Pendiente: Ejecutar benchmarks con datasets de diferente tamaño para validar proyecciones de scaling*