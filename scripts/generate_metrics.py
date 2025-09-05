# Placeholder for scripts/generate_metrics.py
import sqlite3
import os
import json

DB_PATH = "data/scraper_database.db"
METRICS_PATH = "artifacts/metrics.json"

def generate_metrics():
    print("=======================================")
    print("=== GENERANDO METRICAS DEL SISTEMA ===")
    print("=======================================")

    if not os.path.exists(DB_PATH):
        print(f"[ERROR] La base de datos no se encuentra en: {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        total_records = cursor.execute("SELECT COUNT(*) FROM scrapes").fetchone()[0]
        successful = cursor.execute("SELECT COUNT(*) FROM scrapes WHERE status = 'SUCCESS'").fetchone()[0]
        
        success_rate = (successful / total_records) * 100 if total_records > 0 else 0

        avg_response_time = cursor.execute("SELECT AVG(response_time) FROM scrapes WHERE response_time IS NOT NULL").fetchone()[0]

        metrics = {
            "total_scrapes": total_records,
            "successful_scrapes": successful,
            "success_rate_percent": round(success_rate, 2),
            "average_response_time_seconds": round(avg_response_time, 2) if avg_response_time else 0
        }

        print("\n[INFO] Metricas Generadas:")
        print(f"  - Tasa de exito: {metrics['success_rate_percent']:}%")
        print(f"  - Tiempo de respuesta promedio: {metrics['average_response_time_seconds']:}s")

        if not os.path.exists("artifacts"):
            os.makedirs("artifacts")

        with open(METRICS_PATH, "w") as f:
            json.dump(metrics, f, indent=2)

        print(f"\n[SUCCESS] Metricas guardadas en: {METRICS_PATH}")

        conn.close()
        print("\n=======================================")
        print("===   GENERACION COMPLETADA   ===")
        print("=======================================")

    except Exception as e:
        print(f"\n[ERROR] Ocurrio un error al generar las metricas: {e}")

if __name__ == "__main__":
    generate_metrics()