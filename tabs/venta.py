import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
import libreria.recibo as recibo
from libreria.config import db

sqlite3.register_adapter(datetime.datetime, lambda val: val.isoformat(" "))
sqlite3.register_converter("timestamp", lambda val: datetime.datetime.fromisoformat(val.decode()))


class Venta(ttk.Frame):
    def __init__(self, notebook, funalerta):
        super().__init__(notebook)
        self.frame = self
        self.funalerta = funalerta
        self.total = 0
        self.setup_ui()
        notebook.add(self.frame, text="Venta")

    def setup_ui(self):
        self.ventas_button_frame = ttk.Frame(self)
        self.ventas_button_frame.pack(fill="x")

        self.ventas_actualizar = ttk.Button(self.ventas_button_frame, text="📄", command=self.limpiar, width=2)
        self.ventas_actualizar.pack(side="left", padx=5, pady=5)

        self.ventas_anadir = ttk.Button(self.ventas_button_frame, text="+", command=self.anadir, width=2)
        self.ventas_anadir.pack(side="left", padx=5, pady=5)

        self.ventas_editar = ttk.Button(self.ventas_button_frame, text="✏️", command=self.editar, width=2, state="disabled")
        self.ventas_editar.pack(side="left", padx=5, pady=5)

        self.ventas_eliminar = ttk.Button(self.ventas_button_frame, text="🗑️", command=self.eliminar, width=2, state="disabled")
        self.ventas_eliminar.pack(side="left", padx=5, pady=5)

        self.ventas_tree = ttk.Treeview(self, columns=("ID", "Producto", "Precio", "Cantidad"), show="headings")
        self.ventas_tree.heading("ID", text="Código de Barras")
        self.ventas_tree.heading("Producto", text="Producto")
        self.ventas_tree.heading("Precio", text="Precio")
        self.ventas_tree.heading("Cantidad", text="Cantidad")
        self.ventas_tree.pack(fill="both", expand=True)

        self.ventas_vender_frame = ttk.Frame(self)
        self.ventas_vender_frame.pack(fill="x")

        self.venta_resultado = ttk.Label(self.ventas_vender_frame, text="Total: $0", font=("Arial", 14))
        self.venta_resultado.pack()

        self.ventas_vender = ttk.Button(self.ventas_vender_frame, text="✔", command=self.vender, width=2)
        self.ventas_vender.pack(side="left", padx=5, pady=5)

        self.ventas_tree.bind("<<TreeviewSelect>>", self.actualizar_estado_botones)

    def limpiar(self):
        for item in self.ventas_tree.get_children():
            self.ventas_tree.delete(item)
        self.total = 0
        self.venta_resultado.config(text=f"Total: ${self.total:.2f}")

    def vender(self):
        conn = sqlite3.connect(db, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = conn.cursor()

        """
        CREATE TABLE IF NOT EXISTS venta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute("INSERT INTO venta (fecha) VALUES (?)", (datetime.datetime.now(),))
        venta_id = cursor.lastrowid

        for item_id in self.ventas_tree.get_children():
            values = self.ventas_tree.item(item_id)['values']
            try:
                cdb = int(values[0])
                cantidad = int(values[3])

                if cantidad <= 0:
                    raise ValueError("La cantidad debe ser positiva")

                cursor.execute("SELECT cantidad, precio, margen FROM producto WHERE cdb=?", (cdb,))
                result = cursor.fetchone()
                
                if result and result[0] >= cantidad:
                    nueva_cantidad = result[0] - cantidad
                    precio_base = result[1] if result[1] else 1
                    margen = result[2] if result[2] is not None else 0.20
                    precio_venta = precio_base * (1 + margen)
                    ganancias_local = cantidad * precio_venta

                    cursor.execute("UPDATE producto SET cantidad=? WHERE cdb=?", (nueva_cantidad, cdb))
                    cursor.execute("INSERT INTO venta_detalle (venta, cdb, cantidad, precio_venta) VALUES (?, ?, ?, ?)", (venta_id, cdb, cantidad, precio_venta))
                    # faltaria la parte de eliminar quitar de vencimientos si es que se vende algo
                    cursor.execute("SELECT cantidad FROM vencimientos WHERE cdb=? ORDER BY fecha_vencimiento", (cdb,))
                    vencimientos = cursor.fetchall()
                    cantidad_a_restar = cantidad
                    for vencimiento in vencimientos:
                        if cantidad_a_restar <= 0:
                            break
                        cantidad_vencimiento = vencimiento[0]
                        if cantidad_vencimiento > cantidad_a_restar:
                            nueva_cantidad_vencimiento = cantidad_vencimiento - cantidad_a_restar
                            cursor.execute("UPDATE vencimientos SET cantidad=? WHERE cdb=? AND fecha_vencimiento=(SELECT fecha_vencimiento FROM vencimientos WHERE cdb=? ORDER BY fecha_vencimiento LIMIT 1)", (nueva_cantidad_vencimiento, cdb, cdb))
                            cantidad_a_restar = 0
                        else:
                            cursor.execute("DELETE FROM vencimientos WHERE cdb=? AND fecha_vencimiento=(SELECT fecha_vencimiento FROM vencimientos WHERE cdb=? ORDER BY fecha_vencimiento LIMIT 1)", (cdb, cdb))
                            cantidad_a_restar -= cantidad_vencimiento

                    cursor.execute("UPDATE dinero SET total = total + ? WHERE id = 1", (ganancias_local,))
                    conn.commit()
                else:
                    messagebox.showerror("Error", f"Stock insuficiente o producto no existe: {cdb}")
            except ValueError as ve:
                messagebox.showerror("Error", str(ve))
            except Exception as e:
                messagebox.showerror("Error", f"Error al vender: {e}")

        conn.close()
        self.venta_resultado.config(text=f"Ganancia: ${self.total:.2f}")
        self.limpiar()
        recibo.generar_recibo(venta_id)
        self.funalerta()

    def anadir(self):
        anadir_ventana = tk.Toplevel(self)
        anadir_ventana.title("Añadir Producto a la Venta")

        nombre_var = tk.StringVar()
        stock_maximo = tk.IntVar(value=1000)

        ttk.Label(anadir_ventana, text="Código de Barras:").grid(row=0, column=0, padx=5, pady=5)
        cdb_entry = ttk.Entry(anadir_ventana)
        cdb_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(anadir_ventana, text="Producto:").grid(row=1, column=0, padx=5, pady=5)
        producto_label = ttk.Label(anadir_ventana, textvariable=nombre_var)
        producto_label.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(anadir_ventana, text="Cantidad:").grid(row=2, column=0, padx=5, pady=5)
        cantidad_entry = tk.Spinbox(anadir_ventana, from_=1, to=1, width=5)
        cantidad_entry.grid(row=2, column=1, padx=5, pady=5)
        cantidad_entry.delete(0, tk.END)
        cantidad_entry.insert(0, 1)

        agregar_button = ttk.Button(anadir_ventana, text="Agregar", command=lambda: agregar_a_venta())
        agregar_button.grid(row=3, columnspan=2, padx=5, pady=5)
        agregar_button.config(state="disabled")

        def buscar_producto(event=None):
            try:
                cdb = int(cdb_entry.get())
                conn = sqlite3.connect(db)
                cursor = conn.cursor()
                cursor.execute("SELECT nombre, precio, cantidad, margen FROM producto WHERE cdb=?", (cdb,))
                result = cursor.fetchone()
                conn.close()

                if result:
                    nombre, precio, cantidad_disponible, margen = result
                    precio_venta = precio * (1 + margen)
                    nombre_var.set(nombre)
                    stock_maximo.set(cantidad_disponible)

                    # Actualizar Spinbox para limitar cantidad permitida
                    cantidad_entry.config(to=cantidad_disponible)
                    cantidad_entry.delete(0, tk.END)
                    cantidad_entry.insert(0, 1)

                    agregar_button.config(state="normal")
                else:
                    nombre_var.set("Producto no encontrado")
                    cantidad_entry.config(to=1)
                    cantidad_entry.delete(0, tk.END)
                    cantidad_entry.insert(0, 1)
                    agregar_button.config(state="disabled")
            except ValueError:
                nombre_var.set("Código inválido")
                agregar_button.config(state="disabled")

        def agregar_a_venta():
            try:
                cdb = int(cdb_entry.get())
                cantidad = int(cantidad_entry.get())

                if not (1 <= cantidad <= stock_maximo.get()):
                    raise ValueError("La cantidad debe estar dentro del stock disponible")

                conn = sqlite3.connect(db)
                cursor = conn.cursor()
                cursor.execute("SELECT nombre, precio, margen FROM producto WHERE cdb=?", (cdb,))
                result = cursor.fetchone()
                conn.close()

                if result:
                    nombre, precio, margen = result
                    precio_venta = precio * (1 + margen)
                    self.ventas_tree.insert("", "end", values=(cdb, nombre, precio_venta, cantidad))
                    anadir_ventana.destroy()
                    self.total += precio_venta * cantidad
                    self.venta_resultado.config(text=f"Total: ${self.total:.2f}")
                else:
                    messagebox.showerror("Error", "Producto no encontrado")
            except ValueError as ve:
                messagebox.showerror("Error", str(ve))
            except Exception as e:
                messagebox.showerror("Error", f"Error al añadir producto: {e}")

        # Evento cuando se suelta una tecla en el campo de código de barras
        cdb_entry.bind("<KeyRelease>", buscar_producto)

    def editar(self):
        seleccion = self.ventas_tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto para editar")
            return

        item = self.ventas_tree.item(seleccion[0])
        cdb, nombre, precio, cantidad_actual = item['values']
        cantidad_actual = int(cantidad_actual)

        editar_ventana = tk.Toplevel(self)
        editar_ventana.title("Editar Producto en la Venta")

        stock_disponible = 0

        # Consultar stock desde la base de datos
        try:
            conn = sqlite3.connect(db)
            cursor = conn.cursor()
            cursor.execute("SELECT cantidad FROM producto WHERE cdb=?", (cdb,))
            result = cursor.fetchone()
            conn.close()
            if result:
                stock_disponible = result[0]
            else:
                messagebox.showerror("Error", "Producto no encontrado en base de datos")
                editar_ventana.destroy()
                return
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo consultar el stock: {e}")
            editar_ventana.destroy()
            return

        # Calcular el máximo permitido para editar (stock disponible + lo que ya está en carrito)
        cantidad_maxima = stock_disponible + cantidad_actual

        ttk.Label(editar_ventana, text="Código de Barras:").grid(row=0, column=0, padx=5, pady=5)
        cdb_entry = ttk.Entry(editar_ventana)
        cdb_entry.grid(row=0, column=1, padx=5, pady=5)
        cdb_entry.insert(0, cdb)
        cdb_entry.config(state="disabled")

        ttk.Label(editar_ventana, text="Producto:").grid(row=1, column=0, padx=5, pady=5)
        nombre_label = ttk.Label(editar_ventana, text=nombre)
        nombre_label.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(editar_ventana, text="Cantidad:").grid(row=2, column=0, padx=5, pady=5)
        cantidad_entry = tk.Spinbox(editar_ventana, from_=1, to=cantidad_maxima, width=5)
        cantidad_entry.grid(row=2, column=1, padx=5, pady=5)
        cantidad_entry.delete(0, tk.END)
        cantidad_entry.insert(0, cantidad_actual)

        def guardar_cambios():
            try:
                nueva_cantidad = int(cantidad_entry.get())
                if not (1 <= nueva_cantidad <= cantidad_maxima):
                    raise ValueError(f"La cantidad debe estar entre 1 y {cantidad_maxima}")

                self.ventas_tree.item(seleccion[0], values=(cdb, nombre, precio, nueva_cantidad))
                editar_ventana.destroy()
                self.recalcular_total()
            except ValueError as ve:
                messagebox.showerror("Error", str(ve))
            except Exception as e:
                messagebox.showerror("Error", f"Error al editar producto: {e}")

        guardar_button = ttk.Button(editar_ventana, text="Guardar", command=guardar_cambios)
        guardar_button.grid(row=3, columnspan=2, padx=5, pady=5)

    def eliminar(self):
        seleccion = self.ventas_tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
            return

        for item in seleccion:
            self.ventas_tree.delete(item)

        self.recalcular_total()
        self.actualizar_estado_botones()


    def actualizar_estado_botones(self, event=None):
        seleccion = self.ventas_tree.selection()
        estado = "normal" if seleccion else "disabled"
        self.ventas_editar.config(state=estado)
        self.ventas_eliminar.config(state=estado)

    def limpiar_campos(self):
        for widget in self.frame.winfo_children():
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)

    def recalcular_total(self):
        self.total = 0
        for child in self.ventas_tree.get_children():
            values = self.ventas_tree.item(child)['values']
            try:
                precio_venta = float(values[2])  # Este ya es el precio con margen
                cantidad = int(values[3])
                self.total += precio_venta * cantidad
            except (ValueError, IndexError) as e:
                print(f"Error al recalcular total en item {values}: {e}")
        self.venta_resultado.config(text=f"Total: ${self.total:.2f}")
