import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


class Reportes(ttk.Frame):
    def __init__(self, notebook):
        super().__init__(notebook)
        self.frame = self
        self.setup_ui()
        notebook.add(self.frame, text="reportes")

    def setup_ui(self):
        self.ventas_tree = ttk.Treeview(self, columns=("ID", "Producto", "Cantidad", "Precio Venta", "Fecha"), show="headings")
        self.ventas_tree.heading("ID", text="ID")
        self.ventas_tree.heading("Producto", text="Producto")
        self.ventas_tree.heading("Cantidad", text="Cantidad")
        self.ventas_tree.heading("Precio Venta", text="Precio Venta")
        self.ventas_tree.heading("Fecha", text="Fecha")
        self.ventas_tree.pack(fill="both", expand=True)

    def actualizar(self):
        conncection = sqlite3.connect("stock.db")
        cursor = conncection.cursor()
        for i in self.ventas_tree.get_children():
            self.ventas_tree.delete(i)
        cursor.execute("SELECT id, cdb, cantidad, precio_venta FROM ventas")
        for row in cursor.fetchall():
            self.ventas_tree.insert("", "end", values=row)

