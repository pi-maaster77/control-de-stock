import sqlite3
from datetime import datetime
from libreria.config import db

def generar_recibo(venta_id):


    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # Obtener los detalles de la venta
    cursor.execute("""
        SELECT vd.cdb, p.nombre, vd.cantidad, vd.precio_venta, (vd.cantidad * vd.precio_venta) AS total
        FROM venta_detalle vd
        JOIN producto p ON vd.cdb = p.cdb
        WHERE vd.id = ?
    """, (venta_id,))
    items = cursor.fetchall()

    # Calcular el total de la venta
    total_venta = sum(item[4] for item in items)

    # Crear el contenido del recibo
    recibo_content = []
    recibo_content.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    recibo_content.append(f"ID de Venta: {venta_id}")
    recibo_content.append("-" * 40)
    recibo_content.append(f"{'CDB':<10}{'Nombre':<20}{'Cant.':<5}{'Precio':<8}{'Total':<8}")
    recibo_content.append("-" * 40)

    for item in items:
        cdb, nombre, cantidad, precio_venta, total = item
        recibo_content.append(f"{cdb:<10}{nombre:<20}{cantidad:<5}{precio_venta:<8.2f}{total:<8.2f}")

    recibo_content.append("-" * 40)
    recibo_content.append(f"{'Total Venta:':<30}${total_venta:.2f}")
    recibo_content.append("-" * 40)
    recibo_content.append("Gracias por su compra!")

    # Guardar el recibo en un archivo de texto
    with open(f"recibo_venta_{venta_id}.txt", "w") as f:
        for line in recibo_content:
            f.write(line + "\n")

    conn.close()
    mostrar_recibo_en_pantalla(venta_id)

def mostrar_recibo_en_pantalla(venta_id):
    import tkinter as tk
    try:
        with open(f"recibo_venta_{venta_id}.txt", "r") as f:
            recibo_text = f.read()
        ventana = tk.Tk()
        ventana.title(f"Recibo de Venta {venta_id}")
        text_area = tk.Text(ventana, wrap='word', font=('Courier',12))
        text_area.insert(tk.END, recibo_text)
        text_area.config(state=tk.DISABLED)
        text_area.pack(expand=True, fill='both')
        ventana.mainloop()
    except FileNotFoundError:
        print("Recibo no encontrado.")