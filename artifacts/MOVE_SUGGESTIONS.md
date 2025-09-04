Sugerencias de reubicación de archivos en la carpeta raíz

Objetivo: reducir el desorden en la raíz del repositorio moviendo archivos que son auxiliares o artefactos a carpetas dedicadas.

Observaciones actuales (root):

- Archivos/dirs observados en el root: `.github/`, `.env.example`, `.git/`, `.gitattributes`, `.gitignore`, `.idx/`, `.pytest_cache/`, `.scraper/`, `.venv/`, `.vscode/`, `AGENT_PROMPTS.md`, `artifacts/`, `AUDIT_COMPLETION_SUMMARY.md`, `backups/`, `config/`, `data/`, `docs/`, `exports/`, `GEMINI.md`, `logs/`, `MEJORAS.md`, `perfect_combination.patch`, `PLAN_DE_ACCION.MD`, `prompts.md`, `README.md`, `REFACTOR_PLAN.md`, `requirements-dev.txt`, `requirements.txt`, `screenshots/`, `scripts/`, `src/`, `tests/`, `test_manual.db`, `test_manual.db-shm`, `test_manual.db-wal`, `test_metrics.json`, `test_temp.db`, `tools/`, `toscrape_com_book.html`, `venv/`, `venv_validation/`, `WebScraperPRO.bat`, `WebScraperPRO.sh`, `__init__.py`, `__pycache__/`.

Recomendaciones para mover (seguros y de bajo riesgo):

- Mover archivos de documentación y notas a `docs/` o `docs/extras/`:
  - `AGENT_PROMPTS.md`, `GEMINI.md`, `MEJORAS.md`, `PROMPTS.md` (si aplica).
  - `PLAN_DE_ACCION.MD` podría ir a `docs/` o `backups/` según su naturaleza.

- Archivos de scripts y wrappers:
  - `WebScraperPRO.bat`, `WebScraperPRO.sh` ya existen en root pero pueden moverse a `scripts/` (ya hay `scripts/`) para centralizar.

- Artefactos de datos y bases de prueba:
  - `test_manual.db`, `test_manual.db-*`, `test_temp.db`, `test_metrics.json` → mover a `tests/data/` o `backups/` si son snapshots.

- Parches y snapshots:
  - `perfect_combination.patch` → `backups/patches/` o `patches/`.

- Archivos de configuración del editor/IDE: (`.vscode/`) suelen permanecer en root; si no se usan pueden borrarse.

Elementos que yo evitaría mover sin revisión adicional:

- `requirements*.txt`, `README.md`, `REFACTOR_PLAN.md`, `__init__.py`, `src/`, `tests/`, `config/` — deben permanecer en root o su ubicación actual.
- `.venv/` y `venv/`: típicamente deberían ser ignorados y no versionados; si están en repo, se recomienda eliminarlos del control de versiones y regenerarlos con `ensure_env`.

Notas de precaución:

- Antes de mover cualquier archivo, ejecutar una búsqueda global de referencias (imports, rutas, scripts) para evitar romper rutas relativas.
- Actualizar scripts invocadores, `README.md` y cualquier CI que espere archivos en su ubicación original.

Si quieres, puedo:

- Preparar un PR que mueva selectivamente los elementos arriba mencionados (por ejemplo mover `WebScraperPRO.*` a `scripts/` y snapshots DB a `tests/data/`) y actualizar referencias.
- Ejecutar búsquedas cross-references para cada candidato y producir un informe detallado.

Indica si deseas que haga un movimiento piloto (ej. mover `WebScraperPRO.*` y actualizar `README.md`).
