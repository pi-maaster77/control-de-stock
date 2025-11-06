import sqlite3
import os
import sys


def resource_path(relative_path: str) -> str:
    """Return absolute path to resource, working for dev and for PyInstaller bundles.

    - In development returns path relative to the project root (one level up from this file).
    - When frozen by PyInstaller returns the path inside the temporary _MEIPASS folder.
    """
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    else:
        # this file is in <project>/libreria/querry.py -> project root is one level up
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    return os.path.join(base, relative_path)


def get_connection(db_path: str):
    """Return a sqlite3 connection with sensible pragmas for concurrent GUI use.

    Sets journal_mode=WAL and a busy timeout so short concurrent bursts don't fail.
    Caller must close the connection.
    """
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES, timeout=5.0)
    try:
        cur = conn.cursor()
        # Enable WAL to reduce locking between readers and writers
        cur.execute("PRAGMA journal_mode=WAL;")
        # Set busy timeout (milliseconds) to wait for locks briefly instead of failing
        cur.execute("PRAGMA busy_timeout = 2500;")
        conn.commit()
    except Exception:
        # If pragmas fail, keep the connection but continue; caller will handle errors
        pass
    return conn


def ejecutar_sql_desde_archivo(db, sql):
    # Resolver la ruta del archivo SQL tanto en desarrollo como en ejecutable
    sql_path = resource_path(sql)
    with open(sql_path, 'r', encoding='utf-8') as file:
        sql_content = file.read()

    statements = [s.strip() for s in sql_content.split(';') if s.strip()]

    for statement in statements:
        try:
            conn = get_connection(db)
            cursor = conn.cursor()
            cursor.execute(statement)
            conn.commit()
            try:
                rows = cursor.fetchall()
            except Exception:
                rows = []
            print(f"Ejecutado: {statement}")
            if rows:
                print(rows)
        except Exception as e:
            print(f"Error al ejecutar '{statement}': {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass


if __name__ == "__main__":
    ejecutar_sql_desde_archivo(input("Archivo SQL: "), input("Nombre del archivo SQL"))