import sqlite3
import os

DB_PATH = "data/scraper_database.db"

def check_tables():
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] La base de datos no se encuentra en: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ver todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tablas existentes:", tables)

    # Ver estructura de cada tabla
    for (table_name,) in tables:
        print(f"\nEstructura de la tabla '{table_name}':")
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        for column in columns:
            print(f"  - {column[1]} ({column[2]})")

    conn.close()

if __name__ == "__main__":
    check_tables()
