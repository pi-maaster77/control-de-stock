import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from libreria.notificacion import notificar



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
        conncection = sqlite3.connect("stock.db")
        cursor = conncection.cursor()
        for i in self.alerta_tree.get_children():
            self.alerta_tree.delete(i)
        cursor.execute("SELECT cdb, nombre, cantidad, umbral FROM producto WHERE cantidad <= umbral")
        for row in cursor.fetchall():
            self.alerta_tree.insert("", "end", values=row)
        actual = len(self.alerta_tree.get_children())
        print(actual) 
        if actual and self.previo != actual:
            self.previo = actual
            notificar("Alerta de Stock", f"Hay {actual} productos por debajo del umbral.")


