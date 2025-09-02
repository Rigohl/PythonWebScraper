# Code Smells Report

## Resumen Ejecutivo
- **17 archivos** necesitan reformateo (black).
- **14 archivos** tienen imports mal ordenados (isort).  
- **208 infracciones** flake8 (líneas largas, imports unused, espaciado).
- **12 archivos** exceden 60 líneas (rango: 91-562 líneas).

## 1. Archivos Grandes (>60 líneas)

| Archivo | Líneas | Observación |
|---------|---------|-------------|
| `src/orchestrator.py` | 562 | **CRÍTICO** - Clase God con múltiples responsabilidades |
| `src/database.py` | 452 | Alto - Persistencia + dedupe + exports |
| `src/tui/app.py` | 314 | Medio - UI compleja razonable |
| `src/scraper.py` | 334 | Medio - Pipeline scraping, modular |
| `src/main.py` | 216 | Medio - Entry point con CLI |
| `src/llm_extractor.py` | 214 | Medio - LLM integration |
| `src/rl_agent.py` | 210 | Medio - ML wrapper |
| `src/_autopolicy.py` | 142 | Bajo - Config policy |
| `src/fingerprint_manager.py` | 141 | Bajo - Browser fingerprinting |
| `src/user_agent_manager.py` | 126 | Bajo - UA rotation |
| `src/settings.py` | 122 | Bajo - Configuración |
| `src/frontier_classifier.py` | 91 | Bajo - ML classifier stub |

## 2. Violaciones de Estilo (Top)

### Black - Necesitan Formateo (17 archivos):
- `orchestrator.py`, `scraper.py`, `main.py`, `llm_extractor.py`
- `database.py`, `rl_agent.py`, `user_agent_manager.py`
- `tui/app.py`, `settings.py`, `_autopolicy.py` (crítico: 72+ errores)

### Flake8 - Principales Patrones (208 total):
- **E501**: 54 líneas >120 chars (principalmente `orchestrator.py`, `main.py`)
- **E261**: 24 comentarios mal espaciados  
- **E302**: 20 espacios entre funciones/clases
- **E701/E702**: 34 statements en una línea (`;` y `:`)
- **F401**: 7 imports no usados
- **E401**: Multiple imports (`,`)

### ISordered - Imports Desordenados (14 archivos):
Afecta especialmente `orchestrator.py`, `scraper.py`, `main.py`.

## 3. Candidatos a Refactor (Complejidad)

### Alta Prioridad:
1. **`ScrapingOrchestrator`** (562 líneas):
   - Múltiples responsabilidades: queue management, RL, robots, prequalification, metrics
   - Métodos largos: `_worker` (~150 líneas), `_add_links_to_queue` (~50 líneas)
   - **Sugerencia**: Extraer `PrequalificationService`, `MetricsCollector`, `RLCoordinator`

### Media Prioridad:
2. **`DatabaseManager`** (452 líneas):
   - Combina: persistence, dedupe, export, search
   - Método `save_result` complejo (fuzzy dedupe O(N^2))
   - **Sugerencia**: Separar `DeduplicationEngine`, `ExportService`

3. **`AdvancedScraper`** (334 líneas):
   - Pipeline bien estructurado, pero método `scrape` largo
   - **Sugerencia**: Extraer `ContentProcessor`, `LinkExtractor`

## 4. Duplicación Sospechosa

### Patterns Repetidos:
- **Error handling**: try/except patterns similares en orchestrator, scraper
- **Logging + alerts**: `self.logger.warning` + `if self.alert_callback` en ~10 ubicaciones
- **URL validation**: parsing logic duplicada entre orchestrator/scraper  
- **Settings access**: `getattr(settings, 'FLAG', default)` pattern repetido

### Imports Bridge Duplicados:
- `src/intelligence/` re-exporta `src/llm_extractor.py`, `src/rl_agent.py`
- `src/managers/` re-exporta `src/user_agent_manager.py`
- **Sugerencia**: Consolidar en una ubicación o eliminar bridges

## 5. Anti-Patrones Detectados

1. **God Class**: `ScrapingOrchestrator` violates SRP
2. **Long Parameter Lists**: Algunos constructors >5 params
3. **Primitive Obsession**: URLs, domains como strings sin value objects
4. **Feature Envy**: `orchestrator.py` accede internals de `database`, `scraper`
5. **Comments Code**: Algunos TODOs y comentarios obsoletos

## 6. Recomendaciones Inmediatas

### Crítico (Hacer Ahora):
- Aplicar formatters: `black src/`, `isort src/` (sin cambios lógicos)
- Remover imports unused y fix líneas largas críticas

### Medio Plazo:
- Refactor `ScrapingOrchestrator`: extraer 2-3 service classes
- Implementar URL/Domain value objects
- Consolidar error handling patterns

### Bajo Impacto:
- Split archivos 200+ líneas cuando sea natural
- Unified logging helper para evitar duplicación patterns

## 7. Métricos Técnicos

- **Archivos con >100 líneas**: 8/12 (67%)
- **Ratio comentarios**: Bajo (~5% estimated)
- **Complejidad ciclomática estimada**: Alta en orchestrator, media en resto
- **Cobertura imports**: ~7 unused de 200+ imports

---
*Generado automáticamente. Usar como guía, no como regla absoluta.*