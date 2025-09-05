"""Utilidades para medir métricas de persistencia.

Estas funciones permiten capturar:
- Latencia promedio de inserciones de resultados (save_result)
- Conteo de filas por status (SUCCESS, DUPLICATE, FAILED, RETRY)

Se usan sólo en diagnósticos / reporting interno (IA-B) y no forman parte
de la API pública estable; evitar dependencias pesadas.
"""
from __future__ import annotations

import time
from statistics import mean
from typing import Dict, Iterable, List

from .database import DatabaseManager


def measure_insert_latency(db: DatabaseManager, results: Iterable) -> float:
    """Medir latencia promedio de inserción de objetos ScrapeResult.

    Parámetros
    ----------
    db: DatabaseManager
        Instancia de base de datos.
    results: Iterable[ScrapeResult]
        Resultados a insertar (se consumen una vez).
    """
    durations: List[float] = []
    for r in results:
        start = time.perf_counter()
        db.save_result(r)
        durations.append(time.perf_counter() - start)
    return round(mean(durations) * 1000, 2) if durations else 0.0


def status_counters(db: DatabaseManager) -> Dict[str, int]:
    """Obtener conteo de filas por status.

    Retorna un diccionario {status: count}.
    """
    counts: Dict[str, int] = {}
    try:
        for row in db.table.all():  # tipo: ignore[attr-defined]
            st = row.get("status") or "UNKNOWN"
            counts[st] = counts.get(st, 0) + 1
    except Exception:
        pass
    return counts
