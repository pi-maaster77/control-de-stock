import sqlite3
import os


def get_connection(db_path: str):
    """Return a sqlite3 connection with sensible pragmas for concurrent GUI use.

    Sets journal_mode=WAL and a busy timeout so short concurrent bursts don't fail.
    Caller must close the connection.
    """
    need_init_wal = not os.path.exists(db_path)
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
    with open(sql, 'r') as file:
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
    ejecutar_sql_desde_archivo('stock.db', input("Nombre del archivo SQL"))