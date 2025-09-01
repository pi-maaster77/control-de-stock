import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


# --- Compra ---

class Compra(ttk.Frame):
    tab_name = "Compra"

    def __init__(self, notebook):
        super().__init__(notebook)
        self.frame = self
        self.setup_ui()
        notebook.add(self.frame, text=self.tab_name)

    def setup_ui(self):
        self.compra_producto = tk.Entry(self.frame)
        self.compra_cantidad = tk.Entry(self.frame)

        ttk.Label(self.frame, text="Producto:").pack()
        self.compra_producto.pack()
        ttk.Label(self.frame, text="Cantidad:").pack()
        self.compra_cantidad.pack()

        ttk.Button(self.frame, text="Comprar", command=self.comprar).pack(pady=5)

    def comprar(self):
        producto = self.compra_producto.get()
        try:
            cantidad = int(self.compra_cantidad.get())
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser positiva")
            conncection = sqlite3.connect("stock.db")
            cursor = conncection.cursor()
            cursor.execute("SELECT cantidad FROM producto WHERE cdb=?", (producto,))
            result = cursor.fetchone()
            if result:
                nueva_cantidad = result[0] + cantidad
                cursor.execute("UPDATE producto SET cantidad=? WHERE cdb=?", (nueva_cantidad, producto))
            conncection.commit()
            conncection.close()
            self.limpiar_campos()
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Error al comprar: {e}")
    def limpiar_campos(self):
        for widget in self.frame.winfo_children():
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)

