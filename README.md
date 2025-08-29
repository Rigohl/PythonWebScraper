# Web Scraper PRO

Un crawler y archivador web inteligente, diseñado para ser adaptable, resiliente y fácil de usar.

## Prerrequisitos

- Python 3.10 o superior.

## ¿Cómo Empezar?

1.  **Instalar Dependencias:**
    Ejecuta el script correspondiente a tu sistema operativo para crear el entorno virtual e instalar todas las librerías necesarias.

    -   **En Windows:**
        ```powershell
        .\1-Install-Dependencies.bat
        ```
    -   **En macOS / Linux:**
        ```bash
        bash src/1-install-dependencies.sh
        ```

2.  **Lanzar la Aplicación (TUI):**
    Una vez instaladas las dependencias, ejecuta el scraper a través de su interfaz gráfica de usuario (TUI).

    -   **En Windows:**
        ```powershell
        .\2-Launch-Scraper.bat
        ```
    -   **En macOS / Linux:** (Necesitarás crear un script `2-launch-scraper.sh` o ejecutar el comando directamente)

3.  **(Opcional) Ejecución por Línea de Comandos (CLI):**
    Para automatización, también puedes ejecutarlo directamente con el intérprete de Python del entorno virtual.

    ```bash
    # Iniciar un crawling desde la CLI
    .\.venv\Scripts\python.exe src/main.py --crawl http://toscrape.com/
    ```

    Para ver todas las opciones, usa `.\.venv\Scripts\python.exe src\main.py --help`.

---

## Configuración

El proyecto utiliza `pydantic-settings` para gestionar la configuración, lo que permite una gran flexibilidad. La configuración se carga desde las siguientes fuentes, en orden de prioridad:

1. **Variables de entorno del sistema.**
2. **Un archivo `.env`** en la raíz del proyecto.
3. **Valores por defecto** definidos en `src/settings.py`.

Para personalizar tu configuración, simplemente copia el archivo `.env.example` a `.env` y modifica los valores.

```bash
# Ejemplo de contenido para tu archivo .env
CONCURRENCY=10
LLM_API_KEY="sk-xxxxxxxxxxxxxxxxxxxx"
DB_PATH="data/mi_base_de_datos.db"

+# --- Script para resolver conflictos de merge automáticamente ---

echo "[PASO 1/4] Preparando la versión correcta de .github/workflows/data-quality.yml..."
cat <<'EOF' > .github/workflows/data-quality.yml
name: Data Quality
on:
  schedule: [ { cron: "45 4 * * *" } ]
  workflow_dispatch:
jobs:
  dq:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install pandas
      - name: Run basic DQ over CSVs in data/
        id: dq
        run: |
          python - <<'PY'
import json, glob, os, pandas as pd, pathlib, sys
files = glob.glob("data/*.csv") + glob.glob("artifacts/*.csv")
summary = []; breaches=[]
if not files:
  print("No CSVs found, skipping DQ.")
else:
  for f in files:
    try:
      df = pd.read_csv(f)
      n = len(df)
      null_rate = float(df.isna().sum().sum())/(df.size or 1)
      # Heurística: si hay columna 'id' medir duplicados
      dup_rate = float(df.duplicated(subset=[c for c in df.columns if c.lower()=="id"]).sum())/n if n and any(c.lower()=="id" for c in df.columns) else 0.0
      rec = {"file": f, "rows": int(n), "cols": int(df.shape[1]), "null_rate": round(null_rate,4), "dup_id_rate": round(dup_rate,4)}
      summary.append(rec)
      if rec["null_rate"] > 0.2: breaches.append(f"{f}: null_rate {rec['null_rate']}>0.2")
      if rec["dup_id_rate"] > 0.05: breaches.append(f"{f}: dup_id_rate {rec['dup_id_rate']}>0.05")
    except Exception as e:
      breaches.append(f"{f}: error {e}")
pathlib.Path("artifacts").mkdir(exist_ok=True)
open("artifacts/dq_summary.json","w").write(json.dumps({"summary":summary, "breaches":breaches}, indent=2))
print(json.dumps({"summary":summary, "breaches":breaches}, indent=2))
PY
      - name: Job Summary
        run: |
          echo "## Data Quality" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "\`\`\`json" >> $GITHUB_STEP_SUMMARY
          cat artifacts/dq_summary.json >> $GITHUB_STEP_SUMMARY
          echo "\`\`\`" >> $GITHUB_STEP_SUMMARY
      - name: Open issue on DQ breach
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            if (!fs.existsSync('artifacts/dq_summary.json')) return;
            const r = JSON.parse(fs.readFileSync('artifacts/dq_summary.json','utf8'));
            if (!r.breaches || !r.breaches.length) return;
            await github.rest.issues.create({
              owner: context.repo.owner, repo: context.repo.repo,
              title: `Data Quality breach (${new Date().toISOString()})`,
              body: "Brechas:\n```\n"+r.breaches.join("\n")+"\n```",
              labels: ["type/bug","area/orchestrator","ci","prio/P1-soon"]
            });
