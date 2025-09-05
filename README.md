<!-- AUTO-GENERATED HIGH DETAIL README (Mantener actualizado) -->

# Web Scraper PRO – Plataforma Inteligente de Exploración Web

Sistema de crawling, extracción y aprendizaje incremental orientado a resiliencia, adaptabilidad y extensibilidad. Diseñado para:

- Operar en modo totalmente automatizado (crawler + IA híbrida)
- Ejecutar sesiones interactivas (TUI)
- Aplicar extracción estructurada dinámicamente (LLM Zero‑Shot)
- Aprender patrones de cada dominio y optimizar la estrategia- Modo "focus" a un dominio.

---

## 16.1. Chat IA Bilingüe con Procesamiento de Lenguaje Natural

El dashboard profesional incluye un chat inteligente bilingüe (F9 para activar) con capacidades de:

### 🗣️ Procesamiento de Lenguaje Natural

El chat puede entender y procesar peticiones en lenguaje natural tanto en español como en inglés. No necesitas memorizar comandos específicos:

**Ejemplos de uso:**

- "Busca información sobre Python" → Búsqueda automática en base de conocimiento
- "Inicia un scraping en amazon.com" → Configura y ejecuta scraping
- "Edita el archivo config.json" → Abre editor de archivos
- "Ejecuta 'dir' en terminal" → Ejecuta comando en PowerShell

### 🎯 Intenciones Reconocidas

| Intención | Ejemplos en Español | Ejemplos en Inglés |
|-----------|-------------------|-------------------|
| **Búsqueda** | "Busca datos sobre X", "Encuentra información de Y" | "Search for X", "Find information about Y" |
| **Scraping** | "Haz scraping de sitio.com", "Extrae datos de página.html" | "Scrape website.com", "Extract from page.html" |
| **Conocimiento** | "Qué sabes sobre X?", "Háblame de Y" | "What do you know about X?", "Tell me about Y" |
| **Edición** | "Edita archivo.py", "Modifica el código" | "Edit file.py", "Modify the script" |
| **Terminal** | "Ejecuta comando X", "Corre 'dir' en cmd" | "Run command X", "Execute 'ls' in terminal" |

### 🔧 Comandos Directos (Prefijo `/`)

Para usuarios avanzados, también soporta comandos directos:

- `/crawl URL` - Inicia scraping
- `/kb CONSULTA` - Consulta base de conocimiento
- `/edit ARCHIVO` - Edita archivos
- `/terminal COMANDO` - Ejecuta comandos
- `/help` - Ayuda completa

### 🛡️ Seguridad

El sistema incluye medidas de seguridad para:

- Bloquear comandos peligrosos en terminal
- Restringir edición a tipos de archivo seguros
- Validar comandos antes de ejecutar

---

## 17. Scripts de Mantenimientoportar datos limpios y auditables

---

## 1. Requisitos Previos

| Recurso | Mínimo Recomendado | Notas |
|---------|--------------------|-------|
| Python  | 3.10+ (probado 3.12) | Asegura UTF‑8 por defecto |
| Playwright | Última estable | Necesario salvo modo `--demo` |
| SO | Windows / Linux / macOS | Batch principal pensado para Windows |
| RAM | ≥ 2 GB | Más si activas RL + muchas pestañas |
| Conexión | Estable | Para scraping real (demo funciona offline) |

Instala navegadores de Playwright tras dependencias:

```powershell
python -m playwright install
```

---

## 2. Lanzamiento Rápido (Windows – Recomendado)

### 🚀 Nuevo: Dashboard Profesional

Ejecuta el **nuevo script mejorado** que incluye la interfaz profesional:

```powershell
WebScraperPRO_Enhanced.bat
```

El **Dashboard Profesional** ofrece:

- 🎯 **Interfaz moderna tipo dashboard** con métricas en tiempo real
- 🧠 **Control completo de IA Híbrida** (IA-A + IA-B)
- 📊 **Monitoreo avanzado** por dominio y rendimiento
- ⚙️ **Configuración integrada** de todas las funciones
- 📤 **Exportación múltiple** (CSV, JSON, Markdown, Excel, Word)
- 🔧 **Auto-reparación** y análisis inteligente

### 📱 Script Original (Compatibilidad)

Para el lanzador clásico:

```powershell
WebScraperPRO.bat
```

Ambos scripts ofrecen acceso a las siguientes operaciones:

1. **🚀 Dashboard Profesional (NUEVO):** Interfaz moderna con control total y chat IA bilingüe
2. **📱 Interfaz TUI Clásica:** La interfaz original para usuarios familiarizados
3. **🕷️ Crawling Directo:** Scraping inmediato desde línea de comandos
4. **🎮 Modo Demo:** Demostración sin dependencias de navegador
5. **📊 Brain Snapshot:** Estado completo del sistema de IA
6. **📤 Exportar Datos:** Múltiples formatos disponibles
7. **🔧 Configuración:** Ajustes avanzados del sistema
8. **❓ Ayuda:** Documentación integrada
9. **Salir:** Cierra el panel de control.

En Linux/macOS usar `./WebScraperPRO.sh` (si existe) o invocar manualmente comandos equivalentes.

---

## 3. Instalación Manual (Alternativa)

```powershell
python -m pip install -r requirements.txt
python -m playwright install
```

Probar modo demo (no requiere browsers instalados si contenido local):

```powershell
python -m src.main --demo
```

Iniciar TUI:

```powershell
python -m src.main --tui
```

Crawler directo (URLs iniciales):

```powershell
python -m src.main --crawl https://books.toscrape.com/
```

Exportar resultados:

```powershell
python -m src.main --export-csv export.csv
python -m src.main --export-json export.json
```

Snapshot del cerebro híbrido (si habilitado):

```powershell
python -m src.main --brain-snapshot
```

Consultar la base de conocimiento del cerebro:

```powershell
python -m src.main --query-kb "tu pregunta"
```

Generar reporte de auto-reparación:

```powershell
python -m src.main --repair-report
```

Ver ayuda:

```powershell
python -m src.main --help
```

---

## 4. Arquitectura General

```text
┌─────────────┐   CLI/TUI   ┌───────────────┐
│  Usuario    │────────────▶│   main.py     │
└─────────────┘             └──────┬────────┘
                                    │
                              Orquestación
                                    │
                             ┌──────▼────────┐
                             │ Orchestrator  │
                             └───┬─────┬─────┘
         Inteligencia              │     │  Persistencia
   ┌──────────────┐               │     │
   │ HybridBrain  │◀──────────┐   │     │   ┌──────────────┐
   └──────────────┘           │   │     └──▶│  Database     │
   ┌──────────────┐           │   │         │ (SQLite)      │
   │ LLM Extractor│──────────▶│   │         └──────────────┘
   └──────────────┘           │   │
   ┌──────────────┐   RL      │   │ Workers
   │ RL Agent     │──────────▶│   │  (Playwright + Scraper)
   └──────────────┘           │   │
                              ▼   ▼
                          AdvancedScraper
```

### Estructura del Proyecto

```text
PythonWebScraper/
├── src/                    # Código fuente principal
├── tests/                  # Suite de pruebas
├── docs/                   # Documentación técnica y desarrollo
├── scripts/                # Scripts de utilidad y herramientas
├── data/                   # Datos, bases de datos y archivos de ejemplo
├── exports/                # Archivos exportados (CSV, JSON, MD)
├── logs/                   # Archivos de log y sincronización
├── config/                 # Configuraciones del proyecto
├── backups/                # Respaldos y parches
├── tools/                  # Herramientas de mantenimiento
├── WebScraperPRO.bat      # Punto de entrada principal (Windows)
├── WebScraperPRO.sh       # Punto de entrada principal (Linux/macOS)
├── README.md              # Esta documentación
└── requirements.txt       # Dependencias de producción
```

Componentes Clave:

- `Orchestrator`: Concurre, prioriza, reintenta, coordina IA y RL.
- `AdvancedScraper`: Abstracción por página (adaptador navegador + LLM + parsing + hashing + links).
- `HybridBrain`: Fusión de métricas históricas + aprendizaje autónomo.
- `LLMExtractor`: Limpieza/normalización y extracción estructurada zero-shot.
- `RLAgent` (opcional): Ajusta dinámica de backoff / heurísticas.
- `DatabaseManager`: Persistencia (resultados, cookies, esquemas, APIs descubiertas).

---

## 5. Flujo Operativo Detallado

1. URLs iniciales se insertan en cola de prioridad.
2. Precalificación opcional vía HEAD (tipo, tamaño, redirecciones).
3. Workers toman URL → abren página (Playwright) con fingerprint + stealth.
4. Se gestionan cookies (carga / persistencia por dominio) y user-agent.
5. Listener de respuestas captura APIs JSON (xhr/fetch) y las hashea para deduplicación.
6. Se obtiene HTML, se aplica Readability + limpieza LLM.
7. Validación de calidad (longitud mínima, frases prohibidas, duplicados).
8. Extracción estructurada (si existe esquema dinámico pydantic por dominio).
9. Screenshot (si disponible) y perceptual hash (phash) para detectar cambios visuales.
10. Registro en DB y actualización de métricas de dominio.
11. Actualización de cerebro / inteligencia (estatísticas multi-dominio + patrones).
12. Encolado de nuevos enlaces internos visibles filtrados (evita repetitivos / trampas).
13. RL (si activo) recibe estado → acción → posterior aprendizaje con recompensa.
14. Sincronizaciones periódicas en `IA_SYNC.md` (controladas por `IA_SYNC_EVERY`).

---

## 6. Inteligencia: Cómo Hacerlo Más “Inteligente”

| Capacidad | Cómo Activar | Mejora que Aporta |
|-----------|--------------|--------------------|
| HybridBrain | Variable de entorno `HYBRID_BRAIN=1` al lanzar (batch ya lo puede exportar) | Fusión de estadísticas + aprendizaje incremental |
| Ajustar Frecuencia Sync | `IA_SYNC_EVERY=50` (ejemplo) | Menos E/S en disco o mayor granularidad histórica |
| LLM Limpieza avanzada | Proveer `LLM_API_KEY` y `LLM_MODEL` | Texto más puro y extracción robusta |
| Extracción estructurada | Guardar esquema dinámico en DB (ver sección 11) | Datos tabulares listos sin regex/selectors |
| RL Agent | Lanzar con `--use-rl` | Optimización adaptativa de estrategias |
| Filtrado heurístico | Ajustar thresholds en `settings.py` | Menos ruido (páginas vacías/baja calidad) |
| Prioridad de dominios | Brain aprende tasas de éxito | Mejora cobertura útil primero |

### 6.1 Activar HybridBrain

```powershell
$env:HYBRID_BRAIN="1"
WebScraperPRO.bat
```

o directo:

```powershell
HYBRID_BRAIN=1 python -m src.main --crawl https://books.toscrape.com/
```

### 6.2 Alimentar el Cerebro Más Rápido

- Aumenta `CONCURRENCY` si tu máquina lo soporta.
- Proporciona diversas URLs iniciales para exponer más patrones.
- Usa `--demo` solo para smoke tests: no entrena realmente.

### 6.3 Métricas de Inteligencia

Llama a `--brain-snapshot` para JSON con:

```jsonc
{
  "simple_brain": {...},
  "autonomous_brain": {
    "domains_learned": 12,
    "avg_success_rate": 0.54,
    "patterns_identified": 5
  }
}
```

---

## 7. Configuración Centralizada

Orden de carga (prioridad alta→baja):

1. Variables de entorno
2. `.env`
3. Defaults en `settings.py`

### 7.1 Variables Comunes

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `CONCURRENCY` | Workers simultáneos | `8` |
| `LLM_API_KEY` | Clave proveedor LLM | `sk-...` |
| `LLM_MODEL` | Modelo remoto | `gpt-4o-mini` |
| `ROBOTS_ENABLED` | Respetar robots.txt | `true` |
| `HYBRID_BRAIN` | Habilita cerebro híbrido | `1` |
| `IA_SYNC_EVERY` | Intervalo sync IA | `25` |
| `OFFLINE_MODE` | Fuerza modo sin LLM remoto | `1` |
| `DB_PATH` | Ruta DB sqlite | `data/scraper_database.db` |
| `MIN_CONTENT_LENGTH` | Longitud mínima texto útil | `400` |

### 7.2 Ejemplo `.env`

```env
CONCURRENCY=6
HYBRID_BRAIN=1
IA_SYNC_EVERY=40
DB_PATH=data/scraper_database.db
OFFLINE_MODE=1
```

---

## 8. Adaptadores y Extensibilidad

### 8.1 BrowserAdapter

Interfaz: `navigate_to_url`, `get_content`, `screenshot`, cookies, listeners de respuesta. Implementaciones:

- `PlaywrightAdapter`
- `MockBrowserAdapter` (tests / offline)

### 8.2 LLMAdapter

Interfaz: `clean_text`, `extract_structured_data`, `summarize_content`. Implementaciones:

- `OpenAIAdapter`
- `OfflineLLMAdapter`
- `MockLLMAdapter`

Puedes añadir proveedores nuevos creando un adaptador que implemente la interfaz y pasando `LLMExtractor(adapter=nuevo)`.

---

## 9. ScrapeResult (Modelo de Datos)

Campos principales (resumen):

- `url`, `title`, `content_text`, `content_html`
- `links` (internos visibles procesados)
- `visual_hash` (o `"unavailable"`)
- `content_hash`
- `content_type` (heurístico: PRODUCT / BLOG_POST / ARTICLE / GENERAL / UNKNOWN)
- `extracted_data` (dict estructurado si esquema aplicado)
- `http_status_code`
- `crawl_duration`, `response_time` (timings)
- `llm_summary` (si fue generado)

---

## 10. Base de Datos y Persistencia

SQLite (archivo por defecto: `data/scraper_database.db`). Contiene (nomenclatura aproximada):

- `results` – páginas procesadas
- `cookies` – cookies por dominio
- `api_discoveries` – endpoints JSON capturados (hash + URL)
- `extraction_schemas` – definiciones dinámicas (JSON → modelado pydantic)

Exportaciones:

```powershell
python -m src.main --export-csv datos.csv
python -m src.main --export-json datos.json
```

---

## 11. Esquemas de Extracción Dinámica (LLM Zero‑Shot)

1. Definir diccionario simple de campos: `{ "price": "str", "rating": "float" }`.
2. Guardarlo vía `DatabaseManager.save_llm_extraction_schema(domain, json.dumps(schema_dict))`.
3. Próximos scrapes de ese dominio crean un modelo dinámico y el LLM extrae datos.

Ventajas: No dependes de selectores CSS frágiles. Cambios de HTML menores no rompen la extracción.

---

## 12. Reintentos y Backoff

- Reintentos hasta `MAX_RETRIES` (config).
- Backoff exponencial ajustado por RL (si habilitado) o ajustes heurísticos.
- Estados posibles: `SUCCESS`, `FAILED`, `RETRY`, `LOW_QUALITY`, `EMPTY`.

---

## 13. RL (Aprendizaje por Refuerzo)

Activar:

```powershell
python -m src.main --crawl https://books.toscrape.com/ --use-rl
```

Estado usado: ratios de fallo / baja calidad + factor de backoff actual.
Recompensas:

- +1 éxito
- -0.5 baja calidad / vacío
- -1 fallo

Resultado: Ajuste dinámico de `current_backoff_factor`.

---

## 14. Mecanismos Anti-Trampa y Calidad

- Detección de rutas repetitivas (evita loops).
- Validación de longitud mínima.
- Filtros de frases error (404, maintenance, etc.).
- Hashing de contenido para duplicados.
- phash para detectar cambios visuales futuro (comparación puede ampliarse).

---

## 15. Inteligencia Híbrida (HybridBrain)

Combina:

- Métricas simples (tasa éxito, dominios, eventos)
- Patrones de contenido (frecuencia, tipo)
- Insights incrementalmente derivados

Snapshot obtiene:

```powershell
python -m src.main --brain-snapshot > brain.json
```

Recomendado activarlo siempre en producción (`HYBRID_BRAIN=1`).

---

## 16. TUI (Interfaz Textual)

La interfaz textual (basada en Textual) proporciona observabilidad en tiempo real y control operativo sin abrir múltiples terminales. Está pensada para reflejar la “inteligencia” del scraper de forma clara y accionable.

Características clave:

- Banner de Inteligencia (arriba): estado Robots, Ética, Offline, RL, tasa de éxito acumulada; indicadores de anomalía (fallos ≥40%, backoff >2x, PAUSADO).
- Pestañas de Control / Métricas: vista Crawl (inicio: URL, concurrencia, flags) y vista Estadísticas (global, dominio, Brain, Inteligencia acumulada).
- Métricas Globales (LiveStats): procesadas, éxitos, fallos, reintentos, cola y % con color (verde/amarillo/rojo).
- Métricas por Dominio: backoff dinámico, scrapeados, baja calidad, vacíos, fallos (colores según ratios).
- Brain Adaptativo: visitas, tasas éxito/error, link yield, prioridad derivada, eventos recientes.
- Inteligencia Autónoma: dominios aprendidos, sesiones, éxito promedio, patrones, estrategias optimizadas, último aprendizaje.
- Alertas Críticas: mensajes coloreados para incidencias de extracción, saturación y anomalías.
- Progreso & Etapas: barra de progreso y etapa (Idle / Queueing / Crawling / Finalizing / Completed).
- Barra de Estado: totales, tasa de éxito, throughput (TPS) y tiempo transcurrido (mm:ss).
- Notificaciones Toast: feedback de inicio, pausa, export, errores sin bloquear.
- Exportación Markdown Manual: botón “Exportar MD” o `x` genera `exports/manual_export.md`.
- Preferencias Persistentes: autoscroll y visibilidad del log guardadas en `config/ui_prefs.json`.
- Pausa de UI: bufferiza métricas sin perder datos; refresco al reanudar.
- Ocultar Panel de Log: maximiza espacio para análisis profundo de métricas.

Atajos de teclado (Keybindings):

| Tecla | Acción | Descripción |
|-------|--------|-------------|
| s | start | Inicia crawling |
| t | stop | Detiene crawling (cancela worker) |
| p | pause_resume | Pausa/Reanuda refresco UI (buffer) |
| **F9** | **toggle_chat** | **🆕 Muestra/oculta chat IA bilingüe** |
| q | quit | Salir de la TUI |
| r | toggle_robots | Activa/desactiva respeto robots.txt |
| e | toggle_ethics | Activa/desactiva comprobaciones de ética |
| o | toggle_offline | Cambia modo Offline (sin LLM remoto) |
| d | toggle_dark | Tema oscuro (Textual) adicional |
| l | toggle_log_panel | Oculta/Muestra panel de log |
| x | export_markdown | Exporta reporte Markdown manual |
| a | toggle_autoscroll | Autoscroll del log ON/OFF |
| c | clear_log | Limpia el log principal |
| / | focus_url | Foco rápido en campo URL |
| ? | help | Overlay de ayuda |
| Enter (en URL) | start | Atajo rápido para lanzar |
| Esc (overlay) | cerrar | Cierra overlays (ayuda) |

Color Semántico:

- Verde: estado saludable / éxito ≥ 80% / backoff bajo.
- Amarillo: condiciones intermedias / atención recomendada.
- Rojo: anomalía, alta tasa de fallo, métrica degradada.

Anomalías Detectadas actualmente:

- Tasa de fallo global ≥ 40% → Banner muestra “ALTA Falla”.
- Backoff máximo de dominio > 2x → Banner muestra indicador ⏳.
- Estado de pausa activo → “PAUSADO” resaltado.

Exportación Automática vs Manual:

- Automática: controlada por `AUTO_EXPORT_MD=1` (post-run en modo runner tradicional).
- Manual: desde TUI con botón o atajo `x`. Ideal para snapshots intermedios.

Ejecución:

```powershell
python -m src.main --tui
```

Sugerencias de Operación:

- Iniciar con un solo dominio para validar extracción y luego ampliar.
- Observar `Backoff` y `Fallos` por dominio para ajustar límites antes de escalar.
- Usar pausa (`p`) cuando se desee inspeccionar tablas sin parpadeo constante.
- Exportar un Markdown intermedio para auditorías o reportes de progreso.

Roadmap UI (futuro potencial):

- Filtros interactivos por dominio / tasa de error.
- Export JSON directo desde la TUI.
- Visualización de grafo de enlaces (ASCII o sparkline).
- Modo “focus” a un dominio.

---

## 17. Scripts de Mantenimiento

`tools/update_policy.py`:

```powershell
python tools/update_policy.py --domain example.com --robots-output robots_example.txt
```

Opciones:

- `--update-agents`
- `--update-policy`

Salida con WARNING controlada si robots no disponible (tests validan esto).

---

## 18. Backups y Restauración

Directorio `backups/` contiene snapshots / parches / guías:

- `RESTORE_GUIDE.md`
- `cleanup_backups.ps1`

Buenas prácticas:

- Mantener snapshots limpios (el script de cleanup ayuda).
- No versionar datos voluminosos innecesarios.

---

## 19. Pruebas y Calidad

Ejecutar tests:

```powershell
pytest -q
```

Tipos:

- Unitarios: adaptadores, extracción, métricas.
- Integración: orquestador + scraping simulado.
- Skips actuales documentan lógica aún por implementar (retry advanced / robots strict).

Antes de commit (sugerido):

```powershell
pytest -q
python -m pip install -r requirements-dev.txt
flake8 src
```

---

## 20. Estrategias para “Hacerlo Más Inteligente” (Checklist Accionable)

| Objetivo | Acción | Resultado |
|----------|--------|-----------|
| Mejor limpieza | Añadir `LLM_API_KEY` | Texto semántico más estable |
| Más patrones | Aumentar diversidad de dominios | Mejor priorización futura |
| Menos fallos | Analizar `domain_metrics` y bloquear dominios ruidosos | Ahorro de recursos |
| Capturar APIs | Revisar tabla APIs y derivar endpoints útiles | Extensión de scraping de datos JSON |
| Extracción tabular | Definir esquemas dinámicos | CSV listo para BI |
| Acelerar entrenamiento RL | Lanzar varias sesiones cortas | Ajuste más rápido de backoff |
| Persistencia histórica | Automatizar snapshots `brain-snapshot` (cron) | Línea de tiempo de aprendizaje |
| Evolución | Ajustar thresholds en `settings.py` tras observar métricas | Reducción de falsos positivos |

---

## 21. Seguridad, Ética y Cumplimiento

- Respetar términos de uso de los sitios.
- Evitar scraping de datos personales sensibles.
- Activar siempre `ROBOTS_ENABLED=true` salvo pruebas internas.
- Registrar en logs decisiones sensibles (ya soportado parcialmente).
- Limitar concurrencia contra dominios pequeños para no sobrecargar.

---

## 22. Resolución de Problemas (Troubleshooting)

| Problema | Causa Común | Solución |
|----------|-------------|----------|
| `playwright._impl... not found` | No instalaste browsers | `python -m playwright install` |
| Contenido muy corto | Página dinámica/lazy | Aumenta espera; implementar scroll (futuro) |
| Muchos `FAILED` | Bloqueo anti-bot | Disminuye velocidad / activa stealth / rota UAs |
| Duplicados frecuentes | Páginas casi idénticas | Ajusta hashing o filtra parámetros query |
| LLM no limpia bien | Modo offline | Proveer API key + modelo adecuado |
| RL no aprende | Sesión corta | Ejecuta más iteraciones / más dominios |

---

## 23. Roadmap (Extracto de `MEJORAS.md`)

Ideas futuras:

- Scroll infinito y carga perezosa.
- Detección visual diferencial (comparar phash base vs actual).
- Auto-generación de esquemas a partir de clustering semántico.
- Persistencia en motor analítico (DuckDB / Parquet) opcional.

---

## 24. Comandos Comunes (Resumen)

```powershell
# Demo rápida
python -m src.main --demo
# Crawler básico
python -m src.main --crawl https://books.toscrape.com/
# Crawler con RL + HybridBrain
HYBRID_BRAIN=1 python -m src.main --crawl https://books.toscrape.com/ --use-rl
# TUI
python -m src.main --tui
# Exportar
python -m src.main --export-csv out.csv
python -m src.main --export-json out.json
# Snapshot inteligencia
python -m src.main --brain-snapshot
```

---

## 25. Estándares de Código / Contribución

- Tipado consistente (anotaciones obligatorias en nuevas funciones públicas).
- Evitar lógica compleja en línea → extraer helpers privados.
- Manejo de excepciones granular (sin capturas globales salvo en bordes).
- No introducir dependencias nuevas sin justificar impacto.
- Mantener adaptadores desacoplados del resto del núcleo.

---

## 26. Integración con CI/CD (Sugerido)

Pasos recomendados pipeline:

1. Instalar deps
2. Ejecutar tests
3. Generar export de ejemplo (sanity)
4. Producir snapshot brain para auditoría

---

## 27. Métricas Clave a Observar

| Métrica | Fuente | Uso |
|---------|--------|-----|
| `avg_success_rate` | HybridBrain | Salud global |
| `low_quality_ratio` | domain_metrics | Ajustar backoff |
| `patterns_identified` | Autonomous brain | Cobertura semántica |
| `queue_size` | Orchestrator stats | Saturación / tuning concurrency |
| `response_time` | ScrapeResult | Límite vs timeouts |

---

## 28. Extensiones Futuras (Puntos de Inyección)

| Área | Estrategia |
|------|-----------|
| Normalización HTML | Hook antes de Readability |
| Detección duplicados | Cambiar hash → simhash / fuzzy |
| Persistencia | Implementar repositorio alterno (DuckDB) |
| Prioridad URLs | Sustituir `_calculate_priority` por modelo ML avanzado |
| Clasificación contenido | Añadir clasificador temático ML |

---

## 29. Licenciamiento y Uso

Revisa políticas internas antes de producción. No almacenar claves sensibles en repositorio. Añadir archivo LICENSE si se libera públicamente.

---

## 30. Resumen Final

Este sistema ya soporta scraping concurrente, limpieza inteligente, extracción dinámica, cerebro híbrido, RL opcional, exportaciones y una arquitectura modular basada en adaptadores. Para “hacerlo más inteligente”: habilita HybridBrain, provee un LLM real, define esquemas dinámicos y ejecuta sesiones amplias y variadas.

---

¿Necesitas un manual operativo separado o guías de escalado? Abre un issue / extensión de documentación.

<!-- FIN README DETALLADO -->
