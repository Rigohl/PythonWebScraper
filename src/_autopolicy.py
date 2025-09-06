from __future__ import annotations

import json
import logging
import os
import random
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

DEFAULT_POLICY: Dict[str, Any] = {
    "default": {
        "concurrency": 4,
        "request_delay_ms": 300,
        "timeout_s": 30,
        "max_retries": 3,
        "respect_robots": False,
    },
    "per_host": {},
    "thresholds": {
        "success_min": 0.90,
        "rate_limit_max": 0.05,
        "server_error_max": 0.03,
    },
}
POLICY_PATHS = [
    Path(".github/scraper-policy.json"),
    Path("scraper-policy.json"),
]


def load_policy() -> dict:
    """Carga la política desde un archivo JSON o usa los valores por defecto."""
    policy_data = None
    for path in POLICY_PATHS:
        if path.exists():
            try:
                policy_data = json.loads(path.read_text(encoding="utf-8"))
                logger.info(f"Política cargada desde: {path}")
                break
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error cargando política desde {path}: {e}")

    if policy_data is None:
        policy_data = DEFAULT_POLICY.copy()
        logger.info("Usando política por defecto.")

    default_settings = policy_data.setdefault("default", {})

    default_settings["concurrency"] = int(
        os.getenv("SCRAPER_CONCURRENCY", default_settings.get("concurrency", 4))
    )
    default_settings["request_delay_ms"] = int(
        os.getenv("SCRAPER_DELAY_MS", default_settings.get("request_delay_ms", 300))
    )
    default_settings["timeout_s"] = float(
        os.getenv("SCRAPER_TIMEOUT_S", default_settings.get("timeout_s", 30))
    )
    default_settings["max_retries"] = int(
        os.getenv("SCRAPER_MAX_RETRIES", default_settings.get("max_retries", 3))
    )
    env_val = os.getenv(
        "SCRAPER_RESPECT_ROBOTS", default_settings.get("respect_robots", False)
    )
    default_settings["respect_robots"] = str(env_val).lower() in (
        "1",
        "true",
        "yes",
    )
    policy_data.setdefault("per_host", {})
    return policy_data


class RateLimiter:
    def __init__(self, policy: dict):
        self.policy = policy
        self._lock = threading.Lock()
        self._last_at: Dict[str, float] = {}

    def _delay_ms_for(self, host: str) -> int:
        host_policy = self.policy.get("per_host", {}).get(host, {})
        default_delay = self.policy.get("default", {}).get("request_delay_ms", 0)
        delay = host_policy.get("request_delay_ms", default_delay)
        return int(delay)

    def wait(self, host: str):
        delay_ms = self._delay_ms_for(host)
        if delay_ms <= 0:
            return
        with self._lock:
            now = time.perf_counter()
            last = self._last_at.get(host, 0.0)
            need = (last + (delay_ms / 1000.0)) - now
            if need > 0:
                time.sleep(need)
            self._last_at[host] = time.perf_counter()


class Retrier:
    def __init__(self, policy: dict):
        default_policy = policy.get("default", {})
        self.max_retries = int(default_policy.get("max_retries", 3))
        self.timeout_s = float(default_policy.get("timeout_s", 30))

    def backoff(self, attempt: int) -> float:
        """Calcula el tiempo de espera con backoff exponencial y jitter."""
        base_backoff = 0.25 * (2**attempt)
        jitter = random.uniform(0.75, 1.25)
        return min(8.0, base_backoff) * jitter


try:
    import requests

    _HAVE_REQUESTS = True
except ImportError:
    _HAVE_REQUESTS = False

try:
    import urllib.error
    import urllib.request

    _HAVE_URLLIB = True
except ImportError:
    _HAVE_URLLIB = False


def _hostname(u: str) -> str:
    try:
        hostname = urlparse(u).hostname
        if hostname:
            return hostname
        # Fallback para URLs sin scheme (ej. 'example.com/page')
        return socket.gethostbyname(u.split("/")[0])
    except (socket.gaierror, ValueError):
        return "unknown_host"


class MetricsLogger:
    def __init__(self, base: Optional[Path] = None):
        self.logdir = (base or Path(".")) / "logs"
        self.logdir.mkdir(parents=True, exist_ok=True)
        self._rows: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def log(
        self,
        url: str,
        host: str,
        status: Optional[int],
        elapsed_s: float,
        attempt: int,
        size: int,
        error: Optional[str] = None,
    ):
        row = {
            "ts": time.time(),
            "url": url,
            "host": host,
            "status": int(status or 0),
            "elapsed_s": float(elapsed_s),
            "attempt": int(attempt),
            "size": int(size),
            "ok": bool(200 <= (status or 0) < 300 and not error),
            "error": error or "",
        }
        with self._lock:
            self._rows.append(row)
        try:
            with (self.logdir / "metrics.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        except IOError as e:
            logger.error(f"No se pudo escribir en el log de métricas: {e}")

    def summary(self) -> dict:
        rows = list(self._rows)
        if not rows:
            return {
                "n_samples": 0,
                "success_rate": 1.0,
                "rate_limit_rate": 0.0,
                "server_error_rate": 0.0,
                "latency_p50_s": 0.0,
                "latency_p95_s": 0.0,
            }
        num_rows = len(rows)
        statuses = [r["status"] for r in rows]
        latencies = sorted([float(r["elapsed_s"]) for r in rows])
        success_rate = sum(1 for r in rows if r["ok"]) / num_rows
        rate_limit_rate = statuses.count(429) / num_rows
        server_error_rate = sum(1 for s in statuses if s >= 500) / num_rows

        def percentile(p: float) -> float:
            if not latencies:
                return 0.0
            index = max(0, min(len(latencies) - 1, int(p * len(latencies)) - 1))
            return float(latencies[index])

        return {
            "timestamp": int(time.time()),
            "n_samples": num_rows,
            "success_rate": round(success_rate, 3),
            "rate_limit_rate": round(rate_limit_rate, 3),
            "server_error_rate": round(server_error_rate, 3),
            "latency_p50_s": round(percentile(0.50), 3),
            "latency_p95_s": round(percentile(0.95), 3),
        }

    def write_summary(self):
        """Escribe un resumen de las métricas a un archivo JSON."""
        art = Path("artifacts")
        art.mkdir(exist_ok=True)
        summary_data = self.summary()
        try:
            (art / "metrics.json").write_text(
                json.dumps(summary_data, indent=2), encoding="utf-8"
            )
            logger.info(f"Resumen de métricas guardado en {art / 'metrics.json'}")
        except IOError as e:
            logger.error(f"No se pudo guardar el resumen de métricas: {e}")


def fetch(
    url: str,
    limiter: RateLimiter,
    retrier: Retrier,
    metrics: Optional[MetricsLogger] = None,
    headers: Optional[Dict[str, str]] = None,
):
    """Realiza una petición HTTP con reintentos y limitación de tasa."""
    host = _hostname(url)
    final_headers = headers or {"User-Agent": "PythonWebScraper/auto-policy"}
    for attempt in range(retrier.max_retries + 1):
        t0 = time.perf_counter()
        limiter.wait(host)
        status, content_len, error_msg = None, 0, None
        try:
            if _HAVE_REQUESTS:
                resp = requests.get(
                    url, headers=final_headers, timeout=retrier.timeout_s
                )
                status = resp.status_code
                content_len = len(resp.content or b"")
                if 200 <= status < 300:
                    if metrics:
                        metrics.log(
                            url,
                            host,
                            status,
                            time.perf_counter() - t0,
                            attempt,
                            content_len,
                        )
                    return resp
                raise ConnectionError(f"Bad status code: {status}")
            elif _HAVE_URLLIB:
                req = urllib.request.Request(url, headers=final_headers)
                with urllib.request.urlopen(req, timeout=retrier.timeout_s) as r:
                    status = getattr(r, "status", 200)
                    content = r.read()
                    content_len = len(content or b"")
                    if 200 <= status < 300:
                        if metrics:
                            metrics.log(
                                url,
                                host,
                                status,
                                time.perf_counter() - t0,
                                attempt,
                                content_len,
                            )
                        return content
                    raise ConnectionError(f"Bad status code: {status}")
            else:
                logger.error("No HTTP client available.")
                return None
        except (
            requests.RequestException,
            urllib.error.URLError,
            socket.timeout,
        ) as e:
            error_msg = str(e)
            dt = time.perf_counter() - t0
            if metrics:
                metrics.log(
                    url,
                    host,
                    status or 0,
                    dt,
                    attempt,
                    content_len,
                    error=error_msg,
                )
            retryable = (status in (429, 500, 502, 503, 504)) or (
                "timed out" in (error_msg or "").lower()
            )
            if attempt < retrier.max_retries and retryable:
                logger.warning(
                    f"Reintentando {url} (intento {attempt + 1})... "
                    f"Error: {error_msg}"
                )
                time.sleep(retrier.backoff(attempt))
                continue
            logger.error(f"Fallo al obtener {url} tras {attempt + 1} intentos.")
            return None


def build_runtime():
    """Construye y devuelve los componentes del runtime."""
    pol = load_policy()
    return pol, RateLimiter(pol), Retrier(pol), MetricsLogger()


def map_concurrent(items: List[Any], fn: Callable, max_workers: int) -> List[Any]:
    """Ejecuta una función sobre una lista de ítems de forma concurrente."""
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        future_to_item = {ex.submit(fn, item): item for item in items}
        for future in as_completed(future_to_item):
            try:
                results.append(future.result())
            except Exception as e:
                item = future_to_item[future]
                logger.error(f"Error procesando el ítem {item}: {e}")
    return results
