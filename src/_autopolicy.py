from __future__ import annotations
import json, os, time, threading, socket
from pathlib import Path
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

_DEFAULT_POLICY = {
    "default": {"concurrency": 4, "request_delay_ms": 300, "timeout_s": 30, "max_retries": 3, "respect_robots": False},
    "per_host": {},
    "thresholds": {"success_min": 0.90, "rate_limit_max": 0.05, "server_error_max": 0.03}
}
_POLICY_PATHS = [Path(".github/scraper-policy.json"), Path("scraper-policy.json")]

def load_policy()->dict:
    p=None
    for path in _POLICY_PATHS:
        if path.exists():
            p=json.loads(path.read_text(encoding="utf-8")); break
    if p is None:
        p=json.loads(json.dumps(_DEFAULT_POLICY))
    d=p.setdefault("default",{})
    d["concurrency"]=int(os.getenv("SCRAPER_CONCURRENCY",d.get("concurrency",4)))
    d["request_delay_ms"]=int(os.getenv("SCRAPER_DELAY_MS",d.get("request_delay_ms",300)))
    d["timeout_s"]=float(os.getenv("SCRAPER_TIMEOUT_S",d.get("timeout_s",30)))
    d["max_retries"]=int(os.getenv("SCRAPER_MAX_RETRIES",d.get("max_retries",3)))
    d["respect_robots"]=str(os.getenv("SCRAPER_RESPECT_ROBOTS",d.get("respect_robots",False))).lower() in ("1","true","yes")
    p["per_host"]=p.get("per_host",{})
    return p

class RateLimiter:
    def __init__(self,policy:dict):
        self.policy=policy
        self._lock=threading.Lock()
        self._last_at={}
    def _delay_ms_for(self,host:str)->int:
        ph=self.policy.get("per_host",{}).get(host,{})
        return int(ph.get("request_delay_ms", self.policy["default"]["request_delay_ms"]))
    def wait(self,host:str):
        dm=self._delay_ms_for(host)
        if dm<=0: return
        with self._lock:
            now=time.perf_counter()
            last=self._last_at.get(host,0.0)
            need=last+(dm/1000.0)-now
            if need>0: time.sleep(need)
            self._last_at[host]=time.perf_counter()

class Retrier:
    def __init__(self,policy:dict):
        self.max_retries=int(policy["default"]["max_retries"])
        self.timeout_s=float(policy["default"]["timeout_s"])
    def backoff(self,attempt:int)->float:
        import random
        return min(8.0,0.25*(2**attempt))*(0.75+0.5*random.random())

try:
    import requests
    _HAVE_REQUESTS=True
except Exception:
    import urllib.request, urllib.error
    _HAVE_REQUESTS=False

def _hostname(u:str)->str:
    try:
        h=urlparse(u).hostname or ""
        return h or socket.gethostbyname(u)
    except Exception:
        return "unknown"

class MetricsLogger:
    def __init__(self, base: str | Path | None=None):
        self.logdir=(Path(base or ".")/"logs"); self.logdir.mkdir(parents=True, exist_ok=True)
        self._rows=[]; self._lock=threading.Lock()
    def log(self, url, host, status, elapsed_s, attempt, size, error=None):
        row={"ts":time.time(),"url":url,"host":host,"status":int(status or 0),"elapsed_s":float(elapsed_s),"attempt":int(attempt),"size":int(size),"ok":bool(200<=(status or 0)<300 and not error),"error":error or ""}
        with self._lock: self._rows.append(row)
        with (self.logdir/"metrics.jsonl").open("a", encoding="utf-8") as f:
            import json; f.write(json.dumps(row, ensure_ascii=False)+"\n")
    def summary(self)->dict:
        rows=list(self._rows)
        if not rows: return {"n_samples":0,"success_rate":1.0,"rate_limit_rate":0.0,"server_error_rate":0.0,"latency_p50_s":0.0,"latency_p95_s":0.0}
        n=len(rows); sts=[r["status"] for r in rows]; lats=sorted([float(r["elapsed_s"]) for r in rows])
        succ=sum(1 for r in rows if r["ok"])/n; rate429=sts.count(429)/n; rate5xx=sum(1 for s in sts if s>=500)/n
        def pct(p):
            if not lats: return 0.0
            k=max(0,min(len(lats)-1,int(p*len(lats))-1)); return float(lats[k])
        return {"timestamp":int(time.time()),"n_samples":n,"success_rate":round(succ,3),"rate_limit_rate":round(rate429,3),"server_error_rate":round(rate5xx,3),"latency_p50_s":round(pct(0.50),3),"latency_p95_s":round(pct(0.95),3)}
    def write_summary(self):
        import json; art=Path("artifacts"); art.mkdir(exist_ok=True)
        (art/"metrics.json").write_text(json.dumps(self.summary(), indent=2), encoding="utf-8")

def fetch(url:str, limiter:RateLimiter, retrier:Retrier, metrics:MetricsLogger|None=None, headers:dict|None=None):
    import time
    host=_hostname(url); headers=headers or {"User-Agent":"PythonWebScraper/auto-policy"}
    for attempt in range(retrier.max_retries+1):
        t0=time.perf_counter(); limiter.wait(host); status=None; size=0; err=None
        try:
            if _HAVE_REQUESTS:
                resp=requests.get(url, headers=headers, timeout=retrier.timeout_s)
                status=resp.status_code; size=len(resp.content or b"")
                if 200<=status<300:
                    dt=time.perf_counter()-t0; metrics and metrics.log(url,host,status,dt,attempt,size); return resp
                raise RuntimeError(f"bad status {status}")
            else:
                import urllib.request
                req=urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=retrier.timeout_s) as r:
                    status=getattr(r,"status",200); content=r.read(); size=len(content or b"")
                    if 200<=status<300:
                        dt=time.perf_counter()-t0; metrics and metrics.log(url,host,status,dt,attempt,size); return content
                    raise RuntimeError(f"bad status {status}")
        except Exception as e:
            dt=time.perf_counter()-t0; err=str(e); metrics and metrics.log(url,host,status or 0,dt,attempt,size,error=err)
            retryable=(status in (429,500,502,503,504)) or ("timed out" in (err or "").lower())
            if attempt<retrier.max_retries and retryable:
                time.sleep(Retrier({"default":{"max_retries":0,"timeout_s":0}}).backoff(attempt)); continue
            return None

def build_runtime():
    pol=load_policy(); return pol, RateLimiter(pol), Retrier(pol), MetricsLogger()

def map_concurrent(items, fn, max_workers:int):
    out=[]
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs={ex.submit(fn,i):i for i in items}
        for f in as_completed(futs): out.append(f.result())
    return out