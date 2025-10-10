import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from libreria.notificacion import notificar
from libreria.config import db
import libreria.querry as querry

class Alerta(ttk.Frame):
    def __init__(self, notebook):
        super().__init__(notebook)
        self.frame = self
        self.setup_ui()
        self.previo = None
        notebook.add(self.frame, text="Alertas")
    def setup_ui(self):
        self.alerta_tree = ttk.Treeview(self, columns=("ID", "Producto", "Cantidad", "Umbral"), show="headings")
        self.alerta_tree.heading("ID", text="ID")
        self.alerta_tree.heading("Producto", text="Producto")
        self.alerta_tree.heading("Cantidad", text="Cantidad")
        self.alerta_tree.heading("Umbral", text="Umbral")
        self.alerta_tree.pack(fill="both", expand=True)
    def actualizar_alerta_tab(self):
        conn = querry.get_connection(db)
        cursor = conn.cursor()
        try:
            # clear the tree view
            for i in self.alerta_tree.get_children():
                self.alerta_tree.delete(i)

            # productos con bajo stock
            cursor.execute("SELECT cdb, nombre, cantidad, umbral FROM producto WHERE cantidad <= umbral")
            for row in cursor.fetchall():
                self.alerta_tree.insert("", "end", values=row)

            # proximos vencimientos (7 dias)
            cursor.execute("""
                SELECT v.cdb, p.nombre, v.cantidad, v.fecha_vencimiento 
                FROM vencimientos v
                JOIN producto p ON v.cdb = p.cdb
                WHERE v.fecha_vencimiento <= date('now', '+7 days')
            """)
            prox = cursor.fetchall()
            for row in prox:
                self.alerta_tree.insert("", "end", values=(row[0], f"{row[1]} (Vence: {row[3]})", row[2], "Vencimiento"))

            # eliminar y ajustar productos expirados
            cursor.execute("SELECT cdb, cantidad FROM vencimientos WHERE fecha_vencimiento < date('now')")
            productos_a_vencer = cursor.fetchall()

            for cdb, cantidad in productos_a_vencer:
                cursor.execute("SELECT cantidad FROM producto WHERE cdb=?", (cdb,))
                result = cursor.fetchone()
                if result:
                    cantidad_actual = result[0]
                    nueva_cantidad = max(0, cantidad_actual - cantidad)
                    cursor.execute("UPDATE producto SET cantidad=? WHERE cdb=?", (nueva_cantidad, cdb))

            cursor.execute("DELETE FROM vencimientos WHERE fecha_vencimiento < date('now')")

            conn.commit()

            actual = len(self.alerta_tree.get_children())
            if actual and self.previo != actual:
                self.previo = actual
                if actual > 1:
                    notificar("Alerta de Stock", f"Hay {actual} productos que necesitan revision.")
                else:
                    notificar("Alerta de Stock", f"Hay un producto que necesita revision.")
        except Exception as e:
            # ensure we don't crash the UI loop on DB errors
            print(f"Error actualizando alertas: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass



