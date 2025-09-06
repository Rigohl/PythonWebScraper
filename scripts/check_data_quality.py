# Placeholder for scripts/check_data_quality.py
import os
import sqlite3

DB_PATH = "data/scraper_database.db"


def check_data_quality():
    print("=======================================")
    print("=== VERIFICANDO CALIDAD DE DATOS ===")
    print("=======================================")

    if not os.path.exists(DB_PATH):
        print(f"[ERROR] La base de datos no se encuentra en: {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Total de registros
        total_records = cursor.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
        print(f"\n[INFO] Total de registros en la base de datos: {total_records}")

        # Registros exitosos vs fallidos
        successful = cursor.execute(
            "SELECT COUNT(*) FROM pages WHERE status = 'SUCCESS'"
        ).fetchone()[0]
        failed = cursor.execute(
            "SELECT COUNT(*) FROM pages WHERE status = 'FAILED'"
        ).fetchone()[0]
        low_quality = cursor.execute(
            "SELECT COUNT(*) FROM pages WHERE status = 'LOW_QUALITY'"
        ).fetchone()[0]

        print(f"  - Exitosos: {successful}")
        print(f"  - Fallidos: {failed}")
        print(f"  - Baja Calidad: {low_quality}")

        # Registros sin datos extraidos
        no_data = cursor.execute(
            "SELECT COUNT(*) FROM pages WHERE status = 'SUCCESS' AND (extracted_data IS NULL OR extracted_data = '')"
        ).fetchone()[0]
        print(f"\n[WARNING] Registros exitosos sin datos extraidos: {no_data}")

        # Dominios mas scrapeados
        print("\n[INFO] Top 5 dominios mas scrapeados:")
        # Extraer dominio de la URL
        top_domains = cursor.execute(
            """
            SELECT
                CASE
                    WHEN url LIKE 'http://%' THEN substr(url, 8)
                    WHEN url LIKE 'https://%' THEN substr(url, 9)
                    ELSE url
                END as domain,
                COUNT(*) as count
            FROM pages
            WHERE url IS NOT NULL
            GROUP BY domain
            ORDER BY count DESC
            LIMIT 5
        """
        ).fetchall()
        for domain, count in top_domains:
            # Extraer solo el dominio principal
            clean_domain = domain.split("/")[0] if "/" in domain else domain
            print(f"  - {clean_domain}: {count} registros")

        conn.close()
        print("\n=======================================")
        print("=== VERIFICACION COMPLETADA ===")
        print("=======================================")

    except Exception as e:
        print(f"\n[ERROR] Ocurrio un error al verificar la base de datos: {e}")


if __name__ == "__main__":
    check_data_quality()
