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
        # --- Caja de botones ---
        # self.ventas_button_frame = ttk.Frame(self)
        # self.ventas_button_frame.pack(fill="x")
        # self.ventas_anadir = ttk.Button(self.ventas_button_frame, text="+", command=self.anadir_venta, width=2)
        # self.ventas_anadir.pack(side="left", anchor="w", padx=5, pady=5)
        # self.ventas_editar = ttk.Button(self.ventas_button_frame, text="✏️", command=self.editar_venta, width=2, state="disabled")
        # self.ventas_editar.pack(side="left", anchor="w", padx=5, pady=5)
        # self.ventas_eliminar = ttk.Button(self.ventas_button_frame, text="🗑️", command=self.eliminar_venta, width=2, state="disabled")
        # self.ventas_eliminar.pack(side="left", anchor="w", padx=5, pady=5)
        # self.ventas_actualizar = ttk.Button(self.ventas_button_frame, text="📄", command=self.actualizar_stock_tab, width=2)
        # self.ventas_actualizar.pack(side="left", anchor="w", padx=5, pady=5)
        # self.ventas_actualizar = ttk.Button(self.ventas_button_frame, text="✔", command=self.vender, width=2)
        # self.ventas_actualizar.pack(side="left", anchor="w", padx=5, pady=5)

        # --- Tabla ---
        self.ventas_tree = ttk.Treeview(self, columns=("ID","Producto", "Precio", "Cantidad"), show="headings")
        self.ventas_tree.heading("ID", text="Codigo De Barras")
        self.ventas_tree.heading("Producto", text="Producto")
        self.ventas_tree.heading("Precio", text="Precio")
        self.ventas_tree.heading("Cantidad", text="Cantidad")
        self.ventas_tree.pack(fill="both", expand=True)
        self.actualizar_stock_tab()
        # self.ventas_tree.bind("<<TreeviewSelect>>", self.actualizar_estado_botones_stock)
        # self.ventas_tree.bind("<Double-1>", self.copiar_id_al_portapapeles)

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

        for producto in self.ventas_tree.get_children():
            try:
                cantidad = producto[0]
                cdb = producto[0]
                print(cantidad)
                if cantidad <= 0:
                    raise ValueError("La cantidad debe ser positiva")
                
                cursor.execute("SELECT cantidad, precio FROM productos WHERE cdb=?", (cdb,))
                result = cursor.fetchone()
                print(result)
                if result and result[0] >= cantidad:
                    nueva_cantidad = result[0] - cantidad
                    precio_venta = result[1] if result[1] else 1  # Precio por defecto si no está definido
                    ganancias_local = cantidad * precio_venta
                    cursor.execute("UPDATE productos SET cantidad=? WHERE cdb=?", (nueva_cantidad, cdb))
                    cursor.execute("INSERT INTO ventas (cdb, cantidad, precio_venta, fecha) VALUES (?, ?, ?, ?)",
                                (cdb, cantidad, precio_venta, datetime.datetime.now()))
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
    def actualizar_stock_tab(self):
        # conncection = sqlite3.connect("stock.db")
        # cursor = conncection.cursor()
        # cursor.execute("SELECT cdb, nombre, precio, cantidad FROM productos")
        for row in ((1, "Llave Nuda", 0, 2),):
            self.ventas_tree.insert("", "end", values=row)

    def limpiar_campos(self):
        for widget in self.frame.winfo_children():
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)

