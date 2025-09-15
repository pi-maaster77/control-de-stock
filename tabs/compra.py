import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
from libreria.config import db

class Compra(ttk.Frame):
    def __init__(self, notebook):
        super().__init__(notebook)
        self.frame = self
        self.total = 0
        self.setup_ui()
        notebook.add(self.frame, text="Compra")

    def setup_ui(self):
        self.compra_button_frame = ttk.Frame(self)
        self.compra_button_frame.pack(fill="x")

        self.compra_actualizar = ttk.Button(self.compra_button_frame, text="📄", command=self.limpiar, width=2)
        self.compra_actualizar.pack(side="left", padx=5, pady=5)

        self.compra_anadir = ttk.Button(self.compra_button_frame, text="+", command=self.anadir, width=2)
        self.compra_anadir.pack(side="left", padx=5, pady=5)

        self.compra_editar = ttk.Button(self.compra_button_frame, text="✏️", command=self.editar, width=2, state="disabled")
        self.compra_editar.pack(side="left", padx=5, pady=5)

        self.compra_eliminar = ttk.Button(self.compra_button_frame, text="🗑️", command=self.eliminar, width=2, state="disabled")
        self.compra_eliminar.pack(side="left", padx=5, pady=5)

        self.compra_tree = ttk.Treeview(self, columns=("ID", "Producto", "Precio", "Cantidad"), show="headings")
        self.compra_tree.heading("ID", text="Código de Barras")
        self.compra_tree.heading("Producto", text="Producto")
        self.compra_tree.heading("Precio", text="Precio Compra")
        self.compra_tree.heading("Cantidad", text="Cantidad")
        self.compra_tree.pack(fill="both", expand=True)

        self.compra_total_frame = ttk.Frame(self)
        self.compra_total_frame.pack(fill="x")

        self.compra_resultado = ttk.Label(self.compra_total_frame, text="Total: $0", font=("Arial", 14))
        self.compra_resultado.pack()

        self.compra_confirmar = ttk.Button(self.compra_total_frame, text="✔", command=self.confirmar, width=2)
        self.compra_confirmar.pack(side="left", padx=5, pady=5)

        self.compra_tree.bind("<<TreeviewSelect>>", self.actualizar_estado_botones)

    def limpiar(self):
        for item in self.compra_tree.get_children():
            self.compra_tree.delete(item)
        self.total = 0
        self.compra_resultado.config(text=f"Total: ${self.total:.2f}")

    def confirmar(self):
        conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO compra (fecha) VALUES (?)", (datetime.datetime.now(),))
        compra_id = cursor.lastrowid

        for item_id in self.compra_tree.get_children():
            values = self.compra_tree.item(item_id)['values']
            try:
                cdb = int(values[0])
                nombre = values[1]
                precio_compra = float(values[2])
                cantidad = int(values[3])

                cursor.execute("SELECT cantidad, precio FROM producto WHERE cdb=?", (cdb,))
                result = cursor.fetchone()

                if result:
                    cantidad_actual, precio_actual = result
                    nueva_cantidad = cantidad_actual + cantidad
                    cursor.execute("UPDATE producto SET cantidad=? WHERE cdb=?", (nueva_cantidad, cdb))

                    # Actualizar el precio si es distinto
                    if abs(precio_actual - precio_compra) > 0.01:
                        cursor.execute("UPDATE producto SET precio=? WHERE cdb=?", (precio_compra, cdb))
                else:
                    messagebox.showerror("Error", f"Producto no existe: {cdb}")
                    continue

                cursor.execute("INSERT INTO compra_detalle (compra, cdb, cantidad, precio_compra) VALUES (?, ?, ?, ?)", 
                               (compra_id, cdb, cantidad, precio_compra))

                cursor.execute("UPDATE dinero SET total = total - ? WHERE id = 1", (precio_compra * cantidad,))

                conn.commit()
            except Exception as e:
                messagebox.showerror("Error", f"Error al registrar compra: {e}")

        conn.close()
        self.limpiar()
        messagebox.showinfo("Compra", "Compra registrada exitosamente.")

    def anadir(self):
        ventana = tk.Toplevel(self)
        ventana.title("Añadir Producto a la Compra")

        nombre_var = tk.StringVar()

        ttk.Label(ventana, text="Código de Barras:").grid(row=0, column=0, padx=5, pady=5)
        cdb_entry = ttk.Entry(ventana)
        cdb_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(ventana, text="Producto:").grid(row=1, column=0, padx=5, pady=5)
        producto_label = ttk.Label(ventana, textvariable=nombre_var)
        producto_label.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(ventana, text="Cantidad:").grid(row=2, column=0, padx=5, pady=5)
        cantidad_entry = tk.Spinbox(ventana, from_=1, to=1000, width=5)
        cantidad_entry.grid(row=2, column=1, padx=5, pady=5)
        cantidad_entry.delete(0, tk.END)
        cantidad_entry.insert(0, 1)

        ttk.Label(ventana, text="Precio Compra:").grid(row=3, column=0, padx=5, pady=5)
        precio_entry = ttk.Entry(ventana)
        precio_entry.grid(row=3, column=1, padx=5, pady=5)

        agregar_button = ttk.Button(ventana, text="Agregar", command=lambda: agregar_a_compra())
        agregar_button.grid(row=4, columnspan=2, padx=5, pady=5)
        agregar_button.config(state="disabled")

        def buscar_producto(event=None):
            try:
                cdb = int(cdb_entry.get())
                conn = sqlite3.connect(db)
                cursor = conn.cursor()
                cursor.execute("SELECT nombre, precio FROM producto WHERE cdb=?", (cdb,))
                result = cursor.fetchone()
                conn.close()

                if result:
                    nombre, precio_actual = result
                    nombre_var.set(nombre)
                    agregar_button.config(state="normal")

                    precio_entry.delete(0, tk.END)
                    precio_entry.insert(0, f"{precio_actual:.2f}")
                else:
                    nombre_var.set("Producto no encontrado")
                    agregar_button.config(state="disabled")
                    precio_entry.delete(0, tk.END)
            except ValueError:
                nombre_var.set("Código inválido")
                agregar_button.config(state="disabled")
                precio_entry.delete(0, tk.END)


        def agregar_a_compra():
            try:
                cdb = int(cdb_entry.get())
                cantidad = int(cantidad_entry.get())
                precio = float(precio_entry.get())

                if cantidad <= 0 or precio <= 0:
                    raise ValueError("Cantidad y precio deben ser positivos")

                self.compra_tree.insert("", "end", values=(cdb, nombre_var.get(), precio, cantidad))
                self.total += cantidad * precio
                self.compra_resultado.config(text=f"Total: ${self.total:.2f}")
                ventana.destroy()
            except ValueError as ve:
                messagebox.showerror("Error", str(ve))
            except Exception as e:
                messagebox.showerror("Error", f"Error al añadir producto: {e}")

        cdb_entry.bind("<KeyRelease>", buscar_producto)

    def editar(self):
        seleccion = self.compra_tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto para editar")
            return

        item = self.compra_tree.item(seleccion[0])
        cdb, nombre, precio, cantidad = item['values']

        ventana = tk.Toplevel(self)
        ventana.title("Editar Producto")

        ttk.Label(ventana, text="Producto:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(ventana, text=nombre).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(ventana, text="Cantidad:").grid(row=1, column=0, padx=5, pady=5)
        cantidad_entry = tk.Spinbox(ventana, from_=1, to=1000, width=5)
        cantidad_entry.grid(row=1, column=1, padx=5, pady=5)
        cantidad_entry.delete(0, tk.END)
        cantidad_entry.insert(0, cantidad)

        ttk.Label(ventana, text="Precio:").grid(row=2, column=0, padx=5, pady=5)
        precio_entry = ttk.Entry(ventana)
        precio_entry.grid(row=2, column=1, padx=5, pady=5)
        precio_entry.insert(0, precio)

        def guardar():
            try:
                nueva_cantidad = int(cantidad_entry.get())
                nuevo_precio = float(precio_entry.get())
                self.compra_tree.item(seleccion[0], values=(cdb, nombre, nuevo_precio, nueva_cantidad))
                self.recalcular_total()
                ventana.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo editar: {e}")

        ttk.Button(ventana, text="Guardar", command=guardar).grid(row=3, columnspan=2, padx=5, pady=5)

    def eliminar(self):
        seleccion = self.compra_tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
            return

        for item in seleccion:
            self.compra_tree.delete(item)

        self.recalcular_total()
        self.actualizar_estado_botones()

    def actualizar_estado_botones(self, event=None):
        seleccion = self.compra_tree.selection()
        estado = "normal" if seleccion else "disabled"
        self.compra_editar.config(state=estado)
        self.compra_eliminar.config(state=estado)

    def recalcular_total(self):
        self.total = 0
        for child in self.compra_tree.get_children():
            values = self.compra_tree.item(child)['values']
            try:
                precio = float(values[2])
                cantidad = int(values[3])
                self.total += precio * cantidad
            except Exception as e:
                print(f"Error recalculando total: {e}")
        self.compra_resultado.config(text=f"Total: ${self.total:.2f}")
