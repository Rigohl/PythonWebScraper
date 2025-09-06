# 🚀 RECOMENDACIONES DE REFACTOR CRÍTICO
**Arquitecto (IA 1)** - Fecha: 2025-09-06

## 🎯 OBJETIVO
Resolver los problemas críticos de arquitectura identificados para lograr escalabilidad y mantenibilidad.

---

## 🔥 PRIORIDAD CRÍTICA: GOD CLASS REFACTOR

### Problema: ScrapingOrchestrator (562 líneas)
**Violación**: Principio de Responsabilidad Única (SRP)

### Solución: Extraer 3 Servicios Especializados

#### 1. QueueManager (`src/orchestrator/queue_manager.py`)
```python
class QueueManager:
    """Gestión especializada de colas de trabajo y workers"""

    def __init__(self, max_workers: int, queue_timeout: int):
        self.workers = []
        self.task_queue = asyncio.Queue()
        self.active_tasks = set()

    async def submit_task(self, task: ScrapingTask) -> None:
        """Submit task to queue with priority handling"""
        await self.task_queue.put(task)
        self._adjust_worker_pool()

    async def get_next_task(self) -> ScrapingTask:
        """Get next task with backoff consideration"""
        return await self.task_queue.get()

    def _adjust_worker_pool(self) -> None:
        """Dynamic worker pool adjustment based on load"""
        # Implementation
```

#### 2. DomainMonitor (`src/orchestrator/domain_monitor.py`)
```python
class DomainMonitor:
    """Monitoreo y métricas especializadas por dominio"""

    def __init__(self):
        self.domain_metrics = defaultdict(DomainStats)
        self.alert_thresholds = {}

    def update_metrics(self, domain: str, result: ScrapeResult) -> None:
        """Update domain metrics with new result"""
        metrics = self.domain_metrics[domain]
        metrics.update(result)

        if self._should_alert(domain, metrics):
            self._trigger_alert(domain, metrics)

    def get_domain_stats(self, domain: str) -> DomainStats:
        """Get comprehensive domain statistics"""
        return self.domain_metrics.get(domain, DomainStats())

    def _should_alert(self, domain: str, metrics: DomainStats) -> bool:
        """Determine if domain needs alerting"""
        # Implementation
```

#### 3. RLCoordinator (`src/orchestrator/rl_coordinator.py`)
```python
class RLCoordinator:
    """Coordinación especializada de reinforcement learning"""

    def __init__(self, rl_agent: RLAgent):
        self.rl_agent = rl_agent
        self.learning_buffer = []

    async def process_result(self, result: ScrapeResult) -> None:
        """Process scraping result for RL learning"""
        reward = self._calculate_reward(result)
        await self.rl_agent.learn(result.domain, reward)

        # Update backoff based on RL decision
        new_backoff = await self.rl_agent.get_backoff_factor(result.domain)
        await self._update_domain_backoff(result.domain, new_backoff)

    def _calculate_reward(self, result: ScrapeResult) -> float:
        """Calculate RL reward based on result"""
        # Implementation
```

### ScrapingOrchestrator Refactorizado
```python
class ScrapingOrchestrator:
    """Coordinator principal - ahora solo orquesta, no implementa"""

    def __init__(self, settings: Settings):
        self.queue_manager = QueueManager(settings.CONCURRENCY)
        self.domain_monitor = DomainMonitor()
        self.rl_coordinator = RLCoordinator(RLAgent())

        # Delegation pattern - coordinar, no implementar
        self._setup_coordination()

    async def run_crawler(self, start_urls: list[str]) -> None:
        """Main orchestration method"""
        # Coordinate between services
        tasks = await self.queue_manager.submit_initial_tasks(start_urls)

        async with asyncio.TaskGroup() as tg:
            for task in tasks:
                tg.create_task(self._process_task(task))

    async def _process_task(self, task: ScrapingTask) -> None:
        """Process individual task through services"""
        result = await self.scraper.scrape(task.url)

        # Update all monitoring services
        await self.rl_coordinator.process_result(result)
        self.domain_monitor.update_metrics(task.domain, result)

        # Queue next tasks
        new_tasks = self._extract_new_tasks(result)
        await self.queue_manager.submit_tasks(new_tasks)
```

---

## ⚡ PRIORIDAD CRÍTICA: OPTIMIZACIÓN O(N²)

### Problema: Deduplicación Fuzzy
**Ubicación**: `src/database.py::DatabaseManager.save_result()`

### Solución: MinHash LSH + Índices

#### 1. Nuevo Módulo: DeduplicationEngine
```python
class DeduplicationEngine:
    """Motor de deduplicación optimizado O(log N)"""

    def __init__(self, db_path: str):
        self.db = sqlite3.connect(db_path)
        self._create_minhash_index()

    def _create_minhash_index(self) -> None:
        """Create MinHash LSH index for fast similarity search"""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS minhash_signatures (
                id INTEGER PRIMARY KEY,
                content_hash TEXT UNIQUE,
                minhash BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Create LSH index structure
        self._setup_lsh_buckets()

    async def is_duplicate(self, content: str) -> bool:
        """Check if content is duplicate using MinHash LSH"""
        minhash = self._calculate_minhash(content)
        candidates = self._query_lsh_candidates(minhash)

        # Verify candidates with exact similarity
        for candidate in candidates:
            if self._calculate_similarity(content, candidate) > THRESHOLD:
                return True
        return False

    def _calculate_minhash(self, content: str) -> bytes:
        """Calculate MinHash signature for content"""
        # Implementation using datasketch or similar
        pass
```

#### 2. Optimización de DatabaseManager
```python
class DatabaseManager:
    """Database manager con deduplicación optimizada"""

    def __init__(self, db_path: str):
        self.db = sqlite3.connect(db_path)
        self.dedup_engine = DeduplicationEngine(db_path)
        self._create_optimized_indexes()

    def _create_optimized_indexes(self) -> None:
        """Create database indexes for fast queries"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_domain_status ON results(domain, status)",
            "CREATE INDEX IF NOT EXISTS idx_created_at ON results(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_content_hash ON results(content_hash)",
        ]
        for index in indexes:
            self.db.execute(index)

    async def save_result(self, result: ScrapeResult) -> None:
        """Save result with optimized deduplication"""
        # Fast MinHash LSH check first
        if await self.dedup_engine.is_duplicate(result.content):
            await self._mark_as_duplicate(result)
            return

        # Save new result
        await self._insert_result(result)

        # Update MinHash index
        await self.dedup_engine.add_to_index(result.content)
```

---

## 🔄 PRIORIDAD MEDIA: ELIMINACIÓN DE DUPLICACIÓN

### 1. Patrón Error Handler Consolidado
```python
# src/utils/error_handler.py
class ErrorHandler:
    """Consolidated error handling patterns"""

    @staticmethod
    async def handle_scraping_error(error: Exception, context: dict) -> None:
        """Standardized scraping error handling"""
        logger.error(f"Scraping error in {context.get('domain')}: {error}")

        if context.get('alert_callback'):
            await context['alert_callback'](
                f"Error in {context.get('domain')}: {str(error)}"
            )

    @staticmethod
    def handle_validation_error(error: ValidationError, field: str) -> str:
        """Standardized validation error formatting"""
        return f"Validation error in {field}: {error.message}"
```

### 2. URL Validator Consolidado
```python
# src/utils/url_validator.py
class URLValidator:
    """Consolidated URL validation logic"""

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validate URL format and scheme"""
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False

    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize URL for consistent processing"""
        # Remove fragments, normalize scheme, etc.
        pass
```

### 3. Settings Access Helper
```python
# src/utils/settings_helper.py
class SettingsHelper:
    """Consolidated settings access patterns"""

    @staticmethod
    def get_flag(flag_name: str, default: bool = False) -> bool:
        """Safe settings flag access"""
        return getattr(settings, flag_name, default)

    @staticmethod
    def get_config(config_name: str, default: Any = None) -> Any:
        """Safe settings config access"""
        return getattr(settings, config_name, default)
```

---

## 📊 PRIORIDAD MEDIA: SISTEMA DE MÉTRICAS

### Implementación según METRICS_SPEC.md
```python
# src/metrics/metrics_collector.py
class MetricsCollector:
    """Metrics collection according to METRICS_SPEC.md"""

    def __init__(self):
        self.crawler_pages_total = Counter()
        self.crawler_active_queue = Gauge()
        self.crawler_backoff_factor = Gauge()
        self.crawler_content_length = Histogram()
        self.crawler_fetch_latency_seconds = Histogram()

    async def record_page_processed(self, domain: str, status: str) -> None:
        """Record page processing metrics"""
        self.crawler_pages_total.labels(domain=domain, status=status).inc()

    async def update_queue_size(self, domain: str, size: int) -> None:
        """Update active queue size"""
        self.crawler_active_queue.labels(domain=domain).set(size)

    async def record_fetch_latency(self, domain: str, latency: float) -> None:
        """Record fetch latency"""
        self.crawler_fetch_latency_seconds.labels(domain=domain).observe(latency)
```

---

## 🧪 PRIORIDAD BAJA: TESTS DE INTEGRACIÓN

### Test Architecture Refactor
```python
# tests/integration/test_orchestrator_integration.py
class TestOrchestratorIntegration:
    """Integration tests for refactored orchestrator"""

    async def test_full_crawling_pipeline(self):
        """Test complete crawling pipeline with all services"""
        orchestrator = ScrapingOrchestrator(settings)

        # Test with mock services
        results = await orchestrator.run_crawler(TEST_URLS)

        assert len(results) > 0
        assert all(isinstance(r, ScrapeResult) for r in results)

    async def test_service_coordination(self):
        """Test coordination between QueueManager, DomainMonitor, RLCoordinator"""
        # Test that services communicate properly
        pass
```

---

## 📈 MÉTRICAS DE SEGUIMIENTO

### KPIs de Refactor
- **Tamaño de clases**: Reducir de 562 → <300 líneas
- **Complejidad ciclomática**: Reducir promedio de 15 → <10
- **Performance**: Mejorar latencia deduplicación >90%
- **Cobertura tests**: Aumentar de 70% → 85%
- **Duplicación**: Reducir líneas duplicadas >80%

### Timeline Esperado
- **Semana 1**: Extraer servicios del orchestrator
- **Semana 2**: Implementar deduplicación optimizada
- **Semana 3**: Consolidar patrones duplicados
- **Semana 4**: Tests de integración y validación

---

## 🎯 VALIDACIÓN POST-REFACTOR

### Checklist de Validación
- [ ] Todos los tests pasan (7/8 actuales + nuevos)
- [ ] Performance de deduplicación >90% mejorada
- [ ] Memoria estable con colas grandes
- [ ] CPU usage reducido en algoritmos críticos
- [ ] Código coverage >85%
- [ ] Arquitectura documentada actualizada

### Rollback Plan
- **Branch strategy**: feature/refactor-orchestrator
- **Incremental commits**: Servicios extraídos uno por uno
- **Tests**: Validación en cada paso
- **Monitoring**: Métricas de performance durante refactor

---

## 🚀 PRÓXIMOS PASOS

1. **Crear branches** para cada servicio extraído
2. **Implementar tests** para nuevos servicios
3. **Refactor incremental** con validación en cada paso
4. **Actualizar documentación** de arquitectura
5. **Performance testing** post-refactor

¿Procedemos con la implementación del primer servicio (QueueManager)?