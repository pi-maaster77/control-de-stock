import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


class Reportes(ttk.Frame):
    def __init__(self, notebook):
        super().__init__(notebook)
        self.frame = self
        self.setup_ui()
        self.actualizar()
        notebook.add(self.frame, text="Reportes")

    def setup_ui(self):
        # Título
        ttk.Label(self, text="Reporte de Ventas", font=('Arial', 14, 'bold')).pack(pady=5)

        # Treeview de Ventas
        self.ventas_tree = ttk.Treeview(self, columns=("ID", "Fecha", "Producto", "Cantidad", "Precio"), show="headings")
        for col in self.ventas_tree["columns"]:
            self.ventas_tree.heading(col, text=col)
        self.ventas_tree.pack(fill='x', padx=10, pady=5)

        ttk.Label(self, text="Reporte de Compras", font=('Arial', 14, 'bold')).pack(pady=10)

        # Treeview de Compras
        self.compras_tree = ttk.Treeview(self, columns=("ID", "Fecha", "Producto", "Cantidad", "Precio"), show="headings")
        for col in self.compras_tree["columns"]:
            self.compras_tree.heading(col, text=col)
        self.compras_tree.pack(fill='x', padx=10, pady=5)

    def actualizar(self):
        try:
            conn = sqlite3.connect("stock.db")  # Reemplaza con tu archivo .db
            cursor = conn.cursor()

            # --- Cargar ventas ---
            cursor.execute("""
                SELECT 
                    vd.venta,
                    v.fecha,
                    p.nombre,
                    vd.cantidad,
                    vd.precio_venta
                FROM venta_detalle vd
                JOIN venta v ON vd.venta = v.id
                JOIN producto p ON vd.cdb = p.cdb
                ORDER BY v.fecha DESC
            """)
            ventas = cursor.fetchall()
            for row in ventas:
                self.ventas_tree.insert("", "end", values=row)

            # --- Cargar compras ---
            cursor.execute("""
                SELECT 
                    cd.compra,
                    c.fecha,
                    p.nombre,
                    cd.cantidad,
                    cd.precio_compra
                FROM compra_detalle cd
                JOIN compra c ON cd.compra = c.id
                JOIN producto p ON cd.cdb = p.cdb
                ORDER BY c.fecha DESC
            """)
            compras = cursor.fetchall()
            for row in compras:
                self.compras_tree.insert("", "end", values=row)

            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al cargar datos: {e}")
