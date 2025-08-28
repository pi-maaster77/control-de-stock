import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime


sqlite3.register_adapter(datetime.datetime, lambda val: val.isoformat(" "))
sqlite3.register_converter("timestamp", lambda val: datetime.datetime.fromisoformat(val.decode()))


class Venta(ttk.Frame):
    def __init__(self, notebook, funalerta):
        super().__init__(notebook)
        self.frame = self
        self.funalerta = funalerta
        self.setup_ui()
        notebook.add(self.frame, text="Venta")
    def setup_ui(self):
        self.venta_producto = tk.Entry(self.frame)
        self.venta_cantidad = tk.Entry(self.frame)
        self.venta_resultado = ttk.Label(self.frame, text="")

        ttk.Label(self.frame, text="Producto:").pack()
        self.venta_producto.pack()
        ttk.Label(self.frame, text="Cantidad:").pack()
        self.venta_cantidad.pack()
        ttk.Button(self.frame, text="Vender", command=self.vender).pack(pady=5)
        self.venta_resultado.pack()
        ttk.Button(self.frame, text="Ver ganancias totales", command=self.mostrar_ganancias).pack(pady=5)
    def mostrar_ganancias(self):
        conncection = sqlite3.connect("stock.db")
        cursor = conncection.cursor()
        cursor.execute("SELECT total FROM dinero")
        ganancias = cursor.fetchone()[0]
        conncection.close()
        print(ganancias)
        messagebox.showinfo("Ganancias totales", f"Ganancias acumuladas: ${ganancias}")
    def vender(self):
        conncection = sqlite3.connect("stock.db", detect_types=sqlite3.PARSE_DECLTYPES)

        cursor = conncection.cursor()
        producto = self.venta_producto.get()
        try:
            cantidad = int(self.venta_cantidad.get())
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser positiva")
            
            
            cursor.execute("SELECT cantidad, precio FROM productos WHERE cdb=?", (producto,))
            result = cursor.fetchone()
            print(result)
            if result and result[0] >= cantidad:
                nueva_cantidad = result[0] - cantidad
                precio_venta = result[1] if result[1] else 1  # Precio por defecto si no está definido
                ganancias_local = cantidad * precio_venta
                cursor.execute("UPDATE productos SET cantidad=? WHERE cdb=?", (nueva_cantidad, producto))
                cursor.execute("INSERT INTO ventas (cdb, cantidad, precio_venta, fecha) VALUES (?, ?, ?, ?)",
                               (producto, cantidad, precio_venta, datetime.datetime.now()))
                cursor.execute("UPDATE dinero SET total = total + ? WHERE id = 1", (ganancias_local,))
                conncection.commit()
                conncection.close()
                self.venta_resultado.config(text=f"Ganancia: ${ganancias_local:.2f}")
                self.limpiar_campos()
                self.funalerta()
            else:
                messagebox.showerror("Error", "Stock insuficiente o producto no existe")
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Error al vender: {e}")
        
        
    def limpiar_campos(self):
        for widget in self.frame.winfo_children():
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)

