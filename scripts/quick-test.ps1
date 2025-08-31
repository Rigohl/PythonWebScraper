$ErrorActionPreference = "Stop"
Write-Host "→ Quick test: instalar requests (si no existe) y hacer GET a httpbin..." -ForegroundColor Cyan
try { python - <<'PY'
try:
    import requests
except:
    import sys, subprocess
    subprocess.check_call([sys.executable,"-m","pip","install","--upgrade","pip"])
    subprocess.check_call([sys.executable,"-m","pip","install","requests"])
import time, json, pathlib, os, requests
t0=time.perf_counter()
r=requests.get("https://httpbin.org/get", timeout=10)
lat=time.perf_counter()-t0
os.makedirs("logs", exist_ok=True)
row={"ts":time.time(),"url":"https://httpbin.org/get","host":"httpbin.org","status":r.status_code,
     "elapsed_s":round(lat,3),"attempt":0,"size":len(r.content or b""),"ok":200<=r.status_code<300,"error":""}
pathlib.Path("logs/metrics.jsonl").write_text(json.dumps(row)+"\n", encoding="utf-8")
art = pathlib.Path("artifacts"); art.mkdir(exist_ok=True)
art.joinpath("metrics.json").write_text(json.dumps({"n_samples":1,"success_rate":1.0,"rate_limit_rate":0.0,"server_error_rate":0.0,"latency_p50_s":row["elapsed_s"],"latency_p95_s":row["elapsed_s"]}, indent=2), encoding="utf-8")
print("OK: status", r.status_code, "lat", round(lat,3), "s")
PY
} catch {
  Write-Host "⚠ Quick test falló: $_" -ForegroundColor Yellow; exit 1
}
Write-Host "✔ Logs:     $(Join-Path (Get-Location) 'logs\metrics.jsonl')" -ForegroundColor Green
Write-Host "✔ Métricas: $(Join-Path (Get-Location) 'artifacts\metrics.json')" -ForegroundColor Green