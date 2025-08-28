import sqlite3

def ejecutar_sql_desde_archivo(db, sql):
    with open(sql, 'r') as file:
        sql_content = file.read()

    for statement in sql_content.split(';'):
        statement = statement.strip()
        if statement:
            try:
                conn = sqlite3.connect(db)
                cursor = conn.cursor()
                cursor.execute(statement)
                conn.commit()
                print(f"Ejecutado: {statement}")
                print(cursor.fetchall())
            except Exception as e:
                print(f"Error al ejecutar '{statement}': {e}")
            finally:
                conn.close()

if __name__ == "__main__":
    ejecutar_sql_desde_archivo('stock.db', input("Nombre del archivo SQL"))