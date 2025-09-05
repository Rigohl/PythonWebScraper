# MEJORAS Y ROADMAP UNIFICADO

Fecha: 2025-09-05
Origen de esta síntesis: Observaciones internas (sección 2.x problemas), documento previo `docs/MEJORAS.md`, análisis de arquitectura actual y oportunidades de expansión.

---

## 1. Vista Ejecutiva (TL;DR)

- Problemas críticos a atender ya: Excepciones genéricas (2.3), duplicación config (`config.py` vs `settings.py`), persistencia dispersa de estado inteligente.
- Complejidad de "Brains": Mantener pero medir y simplificar interfaz pública antes de refactor profundo.
- Quick Wins (≤1 día cada uno): Unificar settings, logging estructurado decisiones, inventario de persistencia, strict mode excepciones, métricas básicas centralizadas.
- Próximas capacidades de alto valor: Monitoreo de cambios, Asistente de síntesis, RPA básico guiado por estrategias, Estrategia declarativa, Dashboard métrico.

---

## 2. Problemas Identificados (Resumen y Acción)

| ID | Tema | Severidad | Riesgo Principal | Acción Recomendada | Métrica de Éxito |
|----|------|-----------|------------------|--------------------|------------------|
| 2.1 | Complejidad Brains | Estratégica | Dificultad mantenimiento | Medir + façade funcional | 3 métricas por brain visibles |
| 2.2 | Config duplicada | Alta | Valores inconsistentes | Unificar en `settings.py` | 0 referencias nuevas a `config.py` |
| 2.3 | `except Exception` amplio | Alta | Oculta fallos críticos | Reemplazo incremental + strict mode CI | Reducción >70% capturas genéricas |
| 2.4 | Persistencia heterogénea | Media-Alta | Inconsistencias/backup difícil | Inventario + capa repositorio | 1 sola tabla índice fuentes estado |
| 2.5 | Documentación desigual | Media | Curva de entrada alta | Contratos funcionales por módulo | 100% módulos core con contrato |
| 2.6 | Tests conceptuales | Media | Señal débil | Sustituir por tests de comportamiento | Cobertura comportamental crítica >=90% |

Acción inmediata recomendada: Ejecutar lote de “Saneamiento Núcleo” (ver sección 4.1).

---

## 3. Estrategia para la Capa de Inteligencia (Brains)

### 3.1 Re-enfoque

Re-etiquetar internamente como "Motor Cognitivo Modular". Priorizar funciones: selección estrategia, adaptación de parámetros, detección anomalías, recuperación.

### 3.2 Métricas Mínimas por Brain

| Brain | Métricas | Objetivo |
|-------|----------|----------|
| HybridBrain | strategy_switch_count, recovery_success_rate, anomaly_detection_count | Visibilidad global |
| Autonomous / RLAgent | episodes, reward_avg, adjusted_params_count | Eficiencia adaptativa |
| KnowledgeStore | queries_per_run, cache_hit_ratio, schema_updates | Valor semántico |
| Emotional / State Adapt | urgency_factor_avg, risk_bias_shift, regulation_events | Justificación adaptaciones |

### 3.3 Instrumentación

- Añadir logger estructurado: `log.debug("decision", context=..., decision=..., metrics=...)`.
- Feature flags: `BRAIN_HYBRID_ENABLED`, `BRAIN_RL_ENABLED`.
- Modo auditoría: guarda trazas crudas en `artifacts/brain_traces/`.

### 3.4 Refactor Futuro (Condicionado a Métricas)

Si tras 2 sprints algunas capas no mueven indicadores → fusionar o marcar experimental.

---

## 4. Plan de Acción Operativo

### 4.1 Lote "Saneamiento Núcleo" (Semana 1)

1. Unificar configuración.
2. Inventariar `except Exception` y clasificar.
3. Añadir strict mode (`STRICT_ERRORS=1`).
4. Crear módulo `metrics_persistence` estable (si no consolidado) con registro clave-valor temporal.
5. Instrumentar decisiones principales (estrategia / backoff / cambio de modelo).

### 4.2 Lote "Observabilidad" (Semana 2)

1. Tabla SQLite `metrics_timeseries (ts, key, value, context_json)`.
2. Script `scripts/report_metrics.py` export → CSV/JSON.
3. En TUI: panel compacto (top 5 métricas).
4. Export diario programado a `exports/`.

### 4.3 Lote "Persistencia Unificada" (Semana 3)

1. Inventario: JSON brains, DBs (`*.db`).
2. Definir categorías: estado_volátil, aprendizaje, histórico, modelos.
3. Crear repositorio adaptador (e.g. `src/intelligence/database_brain_adapter.py`) con interfaz: `load_state(name)`, `save_state(name, data)`.
4. Migrar uno piloto (KnowledgeStore) → patrón.

### 4.4 Lote "Brains Medibles" (Semana 4)

1. Exponer façade `CognitiveEngine`.
2. Reemplazar llamadas directas dispersas a sub-brains.
3. Añadir test A/B: con vs sin RL ajustando latencia media.

---

## 5. Roadmap Funcional Expandido

| Fase | Función | Descripción | Dependencias | KPI |
|------|---------|-------------|--------------|-----|
| F1 | Monitoreo Cambios Web | Dif > DOM/Texto + alerta | Persistencia + métricas | mean_detection_latency |
| F1 | Dashboard Métrico | Consola/TUI + export | metrics_timeseries | update_interval_s |
| F2 | Asistente Síntesis | Consulta + resumen multi-fuente | LLMExtractor, KnowledgeStore | time_to_summary |
| F2 | RPA Básico | Flujos multi-paso formularios | Playwright core | task_success_rate |
| F3 | Estrategia Declarativa | YAML reglas adaptación | Brains métricas | rule_eval_latency |
| F3 | Auto-Reparación Selectores | LLM diff HTML viejo/nuevo | Histórico HTML | repair_success_rate |
| F4 | Visión Navegación | Captura pantalla → acción | Infra visión | nav_success_rate |
| F4 | Gestión Costos Inteligente | Budget tokens/proxies adapt | Métricas LLM | cost_savings_pct |

---

## 6. Mejoras / Extensiones Potenciales (Investigación y Comunidad)

Fuentes consideradas: experiencias comunes en foros scraping, papers resiliencia, discusiones open-source.

### 6.1 Resiliencia y Anti-Detección

- Adaptive fingerprint rotation (paquetes de perfiles precalculados).
- DNS over HTTPS fallback.
- Heurística de cooldown por dominio ante 4xx repetidos.

### 6.2 Calidad de Datos

- Validación semántica LLM post-extracción (reglas configurables).
- Dedupe semántico (SimHash / MinHash) para evitar reprocesar variantes.
- Contratos de esquema por dominio (pydantic) con versión.

### 6.3 Rendimiento y Escala

- Scheduler basado en prioridad y frescura (aging + score).
- Prefetch de enlaces candidatos (cola secundaria).
- Segmentación adaptativa de lotes (dynamic batch sizing por dominio).

### 6.4 Observabilidad / MLOps Ligero

- Export Prometheus endpoint opcional.
- Perfilado periódico (cProfile) guardado comprimido.
- Etiquetado de sesiones (run_id) correlando logs, métricas y resultados.

### 6.5 Inteligencia Extendida

- Aprendizaje activo: priorizar URLs con mayor incertidumbre de extracción.
- Auto-labeling asistido para mejorar clasificador de frontera.
- Fine-tuning ligero local de embeddings para dominios altos en tráfico.

### 6.6 UX / Integración

- CLI interactiva para ejecutar “playbooks” (YAML → acciones).
- Plantillas de exportación (Markdown/Excel) parametrizadas.
- Modo Headless vs Headful inteligente (cambia si hay bloqueos).

### 6.7 Seguridad / Cumplimiento

- Rate limiting ético configurable.
- Lista blanca/negra de dominios centralizada.
- Auditoría de scraping: registro de consentimiento o permisos cuando aplica.

---

## 7. Checklist de Ejecución Inicial

- [ ] Unificar configuración.
- [ ] Inventario `except Exception` + clasificación.
- [ ] Implementar strict mode CI.
- [ ] Métricas mínimas registradas.
- [ ] Panel métrico inicial (script + TUI placeholder).
- [ ] Inventario persistencia + plan migración.

---

## 8. Contratos Funcionales (Formato a Aplicar)

```text
Módulo: Nombre
Propósito: (1 frase)
Input Clave: ...
Output Clave: ...
Decisiones: lista breve
Métricas Asociadas: ...
Flags Relacionadas: ...
```

Aplicar a: orchestrator, scraper, hybrid_brain, rl_agent, knowledge_store, frontier_classifier.

---

## 9. Política de Introducción de Nuevos Módulos

1. Declarar KPI y métrica de influencia.
2. Añadir feature flag desactivado por defecto hasta validación.
3. Añadir test de humo + 1 test comportamiento.
4. Revisión de costo (tokens, CPU, latencia).
5. Registrar impacto después de 3 ejecuciones comparativas.

---

## 10. Métricas Clave (Definiciones)

| Métrica | Definición | Fuente | Frecuencia |
|---------|------------|--------|-----------|
| success_rate | URLs con extracción válida / total | orchestrator | por run |
| block_rate | Respuestas 403/429 / total | scraper | 5 min |
| strategy_switch_count | Cambios de estrategia | brains | por run |
| recovery_success_rate | Recuperaciones tras fallo crítico | brains | por run |
| extraction_latency_avg | Tiempo medio extracción | scraper | 5 min |
| llm_token_cost_total | Tokens consumidos LLM | llm_extractor | por run |
| anomaly_detection_count | Eventos señalados | brains | por run |
| repair_attempts | Intentos auto-reparación | self_repair | por run |
| repair_success_rate | Intentos exitosos / intentos | self_repair | por run |

---

## 11. Riesgos y Mitigación

| Riesgo | Escenario | Mitigación |
|--------|----------|------------|
| Deriva complejidad | Aumentan clases sin KPI | Política módulo + flags |
| Errores silenciados | Amplios `except` | Strict mode + logging |
| Coste LLM impredecible | Uso explosivo | Budget tokens + degradación modelo |
| Inconsistencia datos | Múltiples formatos | Repositorio persistencia unificado |
| Escalamiento prematuro | Añadir visión antes base | Gates por fase |

---

## 12. Próximo Sprint (Propuesta)

Objetivo: Base estable e instrumentada.

Historias:

- Unificación configuración (Done cuando: `config.py` reexporta o deprecado + tests pasan).
- Remediación 70% `except Exception` críticos.
- Registro 5 métricas clave en SQLite + export JSON.
- Panel TUI muestra 3 métricas.
- Inventario persistencia firmado.

---

## 13. Notas de Implementación

- No mover lógicas sin métrica previa (medir antes/después).
- Evitar introducir terminología biológica nueva (usar nombres funcionales).
- Priorizar cambios que reducen incertidumbre operacional.

---

## 14. Apéndice: Evolución Histórica (Resumen)

(Contenido histórico completo permanece en `docs/MEJORAS.md`; este archivo actúa como capa ejecutiva y operativa consolidada.)

---

## 15. Expansión Más Allá del Scraping (Nuevas Capacidades Propuestas)

### 15.1 Agente RPA Semántico

- **Objetivo:** Ejecutar flujos multi‑paso (login, formularios, descargas) con planificación declarativa.
- **Core Idea:** Archivo YAML de tareas → traductor a acciones Playwright con validación post‑estado.
- **MVP:** Soporte para: `navigate`, `click`, `fill`, `wait-for-text`, `download`.
- **Evolución:** Integrar LLM para sugerir selector alternativo si el principal falla (auto-healing de acciones).
- **KPI:** task_success_rate, fallback_rate.

### 15.2 Motor de Consulta Semántica sobre Corpus Extraído

- **Funcionalidad:** Indexación vectorial (ej. FAISS / SQLite-VSS) de contenido extraído + metadata (dominio, timestamp).
- **Casos:** Preguntas naturales: “dame cambios de precios de la marca X en 30 días”.
- **Add-on:** Respuestas citadas (citas con URL) + scoring de confianza.
- **KPI:** semantic_answer_latency, citation_coverage.

### 15.3 Knowledge Graph Dinámico

- **Descripción:** Generar nodos (Entidad, Atributo, Relación) a partir de extracción estructurada / LLM.
- **Uso:** Navegar relaciones (Producto -> Proveedor -> Variaciones) y detectar anomalías topológicas.
- **Stack sugerido:** rdflib + persistencia en SQLite (triple store ligero) o Neo4j opcional.
- **KPI:** graph_entity_growth_rate, relation_consistency_rate.

### 15.4 Detector de Cambios Visuales y UX

- **Idea:** Capturas periódicas + hash perceptual (imagehash) + diff resaltado.
- **Extensión:** LLM vision (futuro) para explicar “qué cambió”.
- **KPI:** visual_change_detection_latency.

### 15.5 Sistema de Alertas Inteligentes Multicanal

- **Canales:** Email, Slack/Webhook, CLI TUI panel.
- **Reglas:** DSL simple: `if block_rate > 0.25 and domain == "X" then alert("Bloqueo crítico")`.
- **Priorización:** Score = severidad × frecuencia × impacto estimado.
- **KPI:** mean_time_to_alert, false_positive_rate.

### 15.6 Optimización de Costes y Políticas Dinámicas

- **Presupuesto:** Limitar tokens LLM diarios; degradar a modelo barato al superar umbral.
- **Proxy Allocation:** Selección basada en rendimiento reciente (bandit algorithm).
- **KPI:** cost_savings_pct, adaptive_switch_accuracy.

### 15.7 Sandbox de Estrategias (Experiment Hub)

- **Función:** Ejecutar variantes (A/B) de pipelines de scraping/crawling con seeds controlados.
- **Métricas recogidas:** throughput, error_rate, cpu_time, token_usage.
- **Entrega:** Informe comparativo Markdown auto-generado.
- **KPI:** experiment_cycle_time.

### 15.8 Data Contracts y Calidad Continua

- **Formato:** Definir contratos (pydantic) por tipo de entidad: Producto, Artículo, Noticia.
- **Checks:** unicidad, rango numérico, normalización moneda, completitud.
- **Reacción:** Marcar lote como “cuarentena” si viola > X% reglas.
- **KPI:** contract_compliance_rate.

### 15.9 API Pública / SDK Ligero

- **Objetivo:** Exponer endpoints REST para: iniciar job, consultar estado, descargar resultados.
- **Seguridad:** Tokens cortos + rate limiting.
- **KPI:** api_job_start_latency, api_error_rate.

### 15.10 Exportadores Enriquecidos

- **Formatos:** BigQuery loader, Parquet particionado por fecha/dominio, Markdown narrativo.
- **Pipeline:** Normalización -> validación -> enriquecimiento -> export.
- **KPI:** export_success_rate.

### 15.11 Módulo de Privacidad y Ética

- **Controles:** Lista dominios restringidos, filtros de PII (regex + heurísticas LLM).
- **Logs:** Justificación de scraping (propósito declarado) + fecha.
- **KPI:** pii_leak_incidents (objetivo = 0).

### 15.12 Integración con Mensajería de Eventos

- **Broker Opcional:** Redis Streams / NATS / Kafka mini.
- **Uso:** Emisión de eventos: `page.scraped`, `strategy.changed`, `anomaly.detected`.
- **Beneficio:** Desacoplar post-procesos (enriquecimiento, export, análisis ML).
- **KPI:** event_processing_lag.

### 15.13 Agentes Colaborativos (Multi-Agente Ligero)

- **Roles:** Crawler, Extractor, Validador, Curador, Archivador.
- **Orquestación:** Cola compartida + estado en DB.
- **Meta:** Escalar verticalmente funciones sin monolito cognitivo.
- **KPI:** handoff_failure_rate.

### 15.14 Auto-Generación de Playbooks

- **Fuente:** Logs de sesiones exitosas → sintetizar YAML reproducible.
- **LLM Uso:** Resumir secuencias repetidas en un patrón exportable.
- **KPI:** playbook_reuse_rate.

### 15.15 Modo “Continuous Discovery”

- **Función:** Mientras no hay jobs, explorar dominios “semilla” para descubrir nuevas estructuras y pre‑calentar modelos.
- **Criterio de Parada:** Umbral de novedad semántica bajo.
- **KPI:** discovery_novelty_index.

### 15.16 Panel Web Liviano (Opcional)

- **Stack:** FastAPI + Tailwind minimal.
- **Vistas:** Jobs, Métricas tiempo real (websocket), Alertas, Brain traces.
- **KPI:** user_interaction_frequency.

### 15.17 Archivado y Versionado de HTML / Snapshots

- **Almacenamiento:** Comprimir HTML + metadata + hash contenido.
- **Uso:** Diff histórico, reproducibilidad de extracción y auditoría legal.
- **KPI:** retrievability_rate.

### 15.18 Generador de Datasets Sintéticos

- **Objetivo:** Crear HTMLs simulados para robustecer selectores y entrenar clasificadores frontera.
- **Técnicas:** Templates parametrizados + mutadores (shuffle clases, renombrar atributos).
- **KPI:** selector_generalization_gain.

### 15.19 Integración de Embeddings Locales

- **Motivo:** Reducir coste y latencia LLM externos en búsquedas semánticas.
- **Modelos:** Instructor-large, all-mpnet-base-v2 (evaluar footprint).
- **KPI:** embedding_latency_ms, recall_at_10.

### 15.20 Ciclo de Mejora Continua Formalizado

- **Loop:** Observación → Métrica → Hipótesis → Experimento A/B → Decisión → Registro.
- **Artefacto:** `experiments/EXP_<id>.md` autogenerado.
- **KPI:** hypothesis_validation_rate.

### 15.21 Priorización de Implementación (Resumen)

| Prioridad | Capacidad | Justificación | Dependencias |
|-----------|-----------|--------------|--------------|
| Alta | RPA Semántico (15.1) | Amplía casos de uso inmediatamente | Playwright estable |
| Alta | Alertas Inteligentes (15.5) | Reduce MTTR incidentes | Métricas base |
| Alta | Data Contracts (15.8) | Aumenta confianza en datos | Pydantic/base schemas |
| Media | Sandbox Estrategias (15.7) | Mejora experimentación | Métricas + seeds |
| Media | Index Semántico (15.2) | Añade valor exploratorio | Persistencia limpia |
| Media | Cost Optimization (15.6) | Controla gasto LLM | Métricas tokens |
| Media | Auto-Reparación Selectores (Roadmap F3) | Reduce intervención manual | HTML snapshots |
| Baja | Panel Web (15.16) | UX mejorada pero no core | API interna |
| Baja | Multi-Agente (15.13) | Complejidad añadida | Eventos + colas |

### 15.22 Métricas Nuevas Sugeridas

| Métrica | Tipo | Descripción |
|---------|------|-------------|
| task_success_rate | RPA | Tareas completadas / intentos |
| fallback_rate | RPA | Acciones con selector alternativo |
| semantic_answer_latency | QA | Latencia respuesta semántica |
| citation_coverage | QA | % respuestas con citas válidas |
| graph_entity_growth_rate | KG | Variación entidades/día |
| contract_compliance_rate | Calidad | Registros válidos / totales |
| event_processing_lag | Eventos | Diferencia (ms) emisión vs consumo |
| cost_savings_pct | Costos | Ahorro respecto baseline |
| handoff_failure_rate | Multi-agente | Fallos en traspaso rol |
| discovery_novelty_index | Exploración | % nuevas estructuras detectadas |

### 15.23 Requerimientos Técnicos Transversales

- Normalizar capa de eventos antes de multi-agente.
- Definir convención nombres métricas (`snake_case`).
- Establecer política retención snapshots HTML.
- Cache LLM local (opcional) antes de expandir QA.
- Script de benchmark reproducible (semillas + dataset fijo).

### 15.24 Riesgos de Expansión

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| Scope creep | Dilución foco | Roadmap cerrado trimestral |
| Coste LLM | Elevado gasto | Budget + degradación progresiva |
| Complejidad RPA | Flujos frágiles | DSL declarativa + reintentos idempotentes |
| Latencia vector search | Respuestas lentas | Pre-index incremental + caching |
| Gestión snapshots | Uso disco | Compresión + TTL |

---

Fin del documento.
