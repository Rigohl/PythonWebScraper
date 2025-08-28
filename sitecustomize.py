"""
Auto-policy bootstrap sin tocar tu código. Desactiva con: set SCRAPER_AUTOPOLICY=0
"""
import os, atexit
if str(os.getenv("SCRAPER_AUTOPOLICY","1")).lower() in ("0","false","no"):
    raise SystemExit(0)
try:
    import requests
except Exception:
    requests = None
try:
    from src._autopolicy import build_runtime, fetch
except Exception:
    raise SystemExit(0)
POL, LIM, RET, MET = build_runtime()
if requests:
    _orig_get = requests.get
    def _patched_get(url, *args, **kwargs):
        resp = fetch(url, LIM, RET, MET, headers=kwargs.get("headers"))
        if resp is None: return _orig_get(url, *args, **kwargs)
        return resp
    requests.get = _patched_get
@atexit.register
def _flush_metrics():
    try: MET.write_summary()
    except Exception: pass