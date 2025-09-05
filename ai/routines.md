# Routines
## Build (backend)
pip install -r requirements.txt || true
ruff check . && ruff format .
pytest -q -x -vv
python backend/main.py
## Frontend
npm i --prefix frontend || true
npm run dev --prefix frontend
