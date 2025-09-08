Mini app backend

Run locally:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Notes:
- Set `GM_API_ENDPOINT` and `GOOGLE_OAUTH_TOKEN` in the environment before running.
- This is a minimal example for demo/testing only.
