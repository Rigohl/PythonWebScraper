# Contributing Guidelines (Draft)

## 1. Branching Strategy

| Tipo | Prefijo | Ejemplo |
|------|---------|---------|
| Feature | `feat/` | feat/audit-support |
| Fix | `fix/` | fix/dedup-race |
| Refactor | `refactor/` | refactor/orchestrator-split |
| Docs | `docs/` | docs/architecture-links |
| Chore | `chore/` | chore/linters-upgrade |
| Test | `test/` | test/proxy-fallback |

Regla: una unidad lógica por branch; evitar mezclar refactor + feature.

## 2. Commit Convention

Formato: `tipo(scope opcional): descripción breve`.

Tipos permitidos: feat, fix, refactor, perf, test, docs, chore, ci, build, style, revert.

Ejemplos:

- `feat(orchestrator): añade priorización ML básica`
- `fix(database): corrige cálculo jaccard vacío`
- `test(dedupe): agrega caso hash duplicado`

Criterios:

- Mensaje ≤ 72 chars primera línea.
- Descripción extendida opcional tras línea en blanco.
- Referenciar issue con `Refs #ID` o `Closes #ID` cuando aplique.

## 3. Pull Request Checklist

Marcar antes de pedir review:

- [ ] Sigue formato commits convencional.
- [ ] Sólo una intención principal (scope claro).
- [ ] Tests nuevos / ajustados cubren cambios.
- [ ] `pytest` pasa localmente (`-q`).
- [ ] Linters y formatters aplicados (black, isort, flake8) sin errores.
- [ ] Sin secretos, claves o tokens en diff.
- [ ] Documentación/CHANGELOG actualizado si aplica.
- [ ] Tamaño razonable (< ~500 LOC modificadas netas) o justificación incluida.

## 4. Definition of Done (DoD)

- Funciona según casos de uso descritos.
- Sin regresiones en test suite completa.
- Métricas / logging mínimo añadido si introduce ruta crítica nueva.
- Manejo de errores explícito (no swallow silencioso).
- Configuración a través de settings/env (no constantes mágicas ocultas).
- Documentado (código y/o docs) lo suficiente para mantenimiento.

## 5. Code Style & Quality

- Ejecutar `black .`, `isort .`, luego `flake8` antes de commit.
- Evitar funciones > 60 líneas (considerar extraer helpers).
- Complejidad ciclomática sugerida < 12 por función; si excede justificar o refactor.
- Preferir `async` coherente en capa I/O; no mezclar sync waits en secciones concurrentes.
- No colocar lógica en nivel de módulo que ejecute efectos secundarios en import.

## 6. Testing Guidelines

- Usar pruebas unitarias para lógica pura (hashing, dedupe, prioridad).
- Tests de integración para flujo scraper+orchestrator con fixtures Playwright mockeadas cuando sea posible.
- Nombrar archivos `test_*.py` y funciones `test_descripcion`.
- Evitar dependencia de red externa: simular respuestas httpx / Playwright.
- Añadir caso negativo por cada ruta de error significativa.

## 7. Seguridad & Ética

- No registrar contenido completo potencialmente sensible (limitar a hashes / metadatos).
- Validar URLs (evitar `file://`, `javascript:`) antes de solicitar.
- Respetar toggles `ROBOTS_ENABLED`, `ETHICS_CHECKS_ENABLED` en nueva lógica.

## 8. Observabilidad

- Para nuevas métricas, registrar en `docs/METRICS_SPEC.md` si se introduce métrica distinta.
- Logs deben incluir `context` clave cuando ayude a correlación (dominio, url_id, task_id).

## 9. Performance

- Evitar O(N^2) sobre colecciones crecientes sin umbrales o batch.
- Añadir índice DB si nueva query filtra por columna no indexada y se espera crecimiento.

## 10. Review Process

1. Autor abre PR en draft si aún recopila datos.
2. Revisores priorizan: seguridad > correctness > mantenibilidad > performance micro.
3. Comentarios deben proponer alternativa concreta si marcan un problema.
4. Al aprobar: squash merge recomendado salvo que se preserve historia intencional.

## 11. Versionado / Releases (Futuro)

- Adoptar SemVer una vez exista artefacto distribuible.
- CHANGELOG.md (pendiente) para primer release estable.

## 12. Backport / Hotfix (Cuando aplique)

- Crear branch `hotfix/<breve>` desde tag release.
- Merge a main + cherry-pick a rama de desarrollo activa si difiere.

---
Fin del borrador. Ajustar tras primera ronda de adopción.
