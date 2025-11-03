import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
from libreria.boton import *
from libreria.toplevel import TopLevel


class Stock(ttk.Frame):
    def __init__(self, notebook, db):
        super().__init__(notebook)
        self.db = db
        self.frame = self
        self.setup_ui()
        notebook.add(self.frame, text="Stock")
    def setup_ui(self):
        # --- Caja de botones ---
        self.stock_button_frame = ttk.Frame(self)
        self.stock_button_frame.pack(fill="x")
        self.stock_actualizar = Boton(self.stock_button_frame, tipo=ACTUALIZAR, command=self.actualizar_stock_tab)
        self.stock_actualizar.pack(side="left", anchor="w", padx=5, pady=5)
        self.stock_anadir = Boton(self.stock_button_frame, tipo=AGREGAR, command=self.anadir_stock_tab)
        self.stock_anadir.pack(side="left", anchor="w", padx=5, pady=5)
        self.stock_editar = Boton(self.stock_button_frame, tipo=EDITAR, command=self.editar_stock_tab, state="disabled")
        self.stock_editar.pack(side="left", anchor="w", padx=5, pady=5)
        self.stock_eliminar = Boton(self.stock_button_frame, tipo=ELIMINAR, command=self.eliminar_stock_tab, state="disabled")
        self.stock_eliminar.pack(side="left", anchor="w", padx=5, pady=5)
        
        # --- Tabla ---
        self.stock_tree = ttk.Treeview(self, columns=("ID","Producto", "Precio", "Cantidad", "Margen", "Umbral"), show="headings")
        self.stock_tree.heading("ID", text="Codigo De Barras")
        self.stock_tree.heading("Producto", text="Producto")
        self.stock_tree.heading("Precio", text="Precio")
        self.stock_tree.heading("Cantidad", text="Cantidad")
        self.stock_tree.heading("Margen", text="Margen")
        self.stock_tree.heading("Umbral", text="Umbral")
        self.stock_tree.pack(fill="both", expand=True)
        self.stock_tree.bind("<<TreeviewSelect>>", self.actualizar_estado_botones_stock)
        self.stock_tree.bind("<Double-1>", self.copiar_id_al_portapapeles)

    def editar_stock_tab(self):
        selected = self.stock_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un producto para editar")
            return

        item = self.stock_tree.item(selected[0])
        cdb, nombre, precio, cantidad, margen, umbral = item['values']

        def guardar():
            try:
                nuevo_cdb = int(cdb_entry.get())
                nuevo_nombre = nombre_entry.get()
                nuevo_precio = float(precio_entry.get())
                nueva_cantidad = int(cantidad_entry.get())
                nuevo_umbral = int(umbral_entry.get())
                nuevo_margen = float(margen_entry.get())
                nuevo_perecedero = perecedero_var.get()
                conncection = sqlite3.connect(self.db)
                cursor = conncection.cursor()
                cursor.execute("""UPDATE producto 
                                SET cdb=?, nombre=?, precio=?, cantidad=?, umbral=?, margen=?, perecedero=?
                                WHERE cdb=?""",
                            (nuevo_cdb, nuevo_nombre, nuevo_precio, nueva_cantidad, nuevo_umbral, nuevo_margen, nuevo_perecedero, cdb))
                conncection.commit()
                conncection.close()
                self.actualizar_stock_tab()
                top.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error al editar producto: {e}")

        top = TopLevel(self)
        top.title("Editar Producto")

        tk.Label(top, text="Código de Barras:").grid(row=0, column=0, padx=5, pady=5)
        cdb_entry = tk.Entry(top)
        cdb_entry.insert(0, cdb)
        cdb_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(top, text="Nombre:").grid(row=1, column=0, padx=5, pady=5)
        nombre_entry = tk.Entry(top)
        nombre_entry.insert(0, nombre)
        nombre_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(top, text="Precio:").grid(row=2, column=0, padx=5, pady=5)
        precio_entry = tk.Entry(top)
        precio_entry.insert(0, str(precio))
        precio_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(top, text="Cantidad:").grid(row=3, column=0, padx=5, pady=5)
        cantidad_entry = tk.Entry(top)
        cantidad_entry.insert(0, str(cantidad))
        cantidad_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(top, text="Umbral:").grid(row=4, column=0, padx=5, pady=5)
        umbral_entry = tk.Entry(top)
        umbral_entry.insert(0, str(umbral))
        umbral_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(top, text="Margen:").grid(row=5, column=0, padx=5, pady=5)
        margen_entry = tk.Entry(top)
        margen_entry.insert(0, str(margen))
        margen_entry.grid(row=5, column=1, padx=5, pady=5)

        tk.Label(top, text="Perecedero").grid(row=6, column=0, padx=5, pady=5)
        perecedero_var = tk.BooleanVar()
        perecedero_check = tk.Checkbutton(top, variable=perecedero_var)
        perecedero_check.grid(row=6, column=1, padx=5, pady=5)
        perecedero_var.set(bool(item.get('perecedero', False)))

        tk.Button(top, text="Guardar", command=guardar).grid(row=7, column=0, columnspan=2, padx=5, pady=5)

    def anadir_stock_tab(self):
        def guardar():
            try:
                cdb = int(cdb_entry.get())
                nombre = nombre_entry.get()
                precio = float(precio_entry.get())
                cantidad = 0
                umbral = int(umbral_entry.get())
                margen = float(margen_entry.get())
                perecedero = perecedero_var.get()

                connection = sqlite3.connect(self.db)
                cursor = connection.cursor()

                # 1. Insertar producto
                cursor.execute("""
                    INSERT INTO producto (cdb, nombre, precio, cantidad, umbral, margen, perecedero)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (cdb, nombre, precio, cantidad, umbral, margen, perecedero)
                )

                # 2. Registrar compra
                cursor.execute("INSERT INTO compra (fecha) VALUES (?)", (datetime.datetime.now(),))
                compra_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO compra_detalle (compra, cdb, cantidad, precio_compra)
                    VALUES (?, ?, ?, ?)""",
                    (compra_id, cdb, cantidad, precio)
                )

                # 3. Actualizar dinero (restar costo)
                cursor.execute("UPDATE dinero SET total = total - ? WHERE id = 1", (precio * cantidad,))

                connection.commit()
                connection.close()

                self.actualizar_stock_tab()
                top.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error al añadir producto: {e}")


        top = TopLevel(self)
        top.title("Añadir Producto")

        tk.Label(top, text="Código de Barras:").grid(row=0, column=0, padx=5, pady=5)
        cdb_entry = tk.Entry(top)
        cdb_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(top, text="Nombre:").grid(row=1, column=0, padx=5, pady=5)
        nombre_entry = tk.Entry(top)
        nombre_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(top, text="Precio:").grid(row=2, column=0, padx=5, pady=5)
        precio_entry = tk.Entry(top)
        precio_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(top, text="Umbral:").grid(row=3, column=0, padx=5, pady=5)
        umbral_entry = tk.Entry(top)
        umbral_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(top, text="Margen:").grid(row=4, column=0, padx=5, pady=5)
        margen_entry = tk.Entry(top)
        margen_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(top, text="Perecedero").grid(row=5, column=0, padx=5, pady=5)
        perecedero_var = tk.BooleanVar()
        perecedero_check = tk.Checkbutton(top, variable=perecedero_var)
        perecedero_check.grid(row=5, column=1, padx=5, pady=5)


        tk.Button(top, text="Guardar", command=guardar).grid(row=7, column=0, columnspan=2, padx=5, pady=5)

    def actualizar_stock_tab(self):
        conncection = sqlite3.connect(self.db)
        cursor = conncection.cursor()
        for i in self.stock_tree.get_children():
            self.stock_tree.delete(i)
        cursor.execute("SELECT cdb, nombre, precio, cantidad, margen, umbral FROM producto")
        for row in cursor.fetchall():
            self.stock_tree.insert("", "end", values=row)


    def eliminar_stock_tab(self):
        seleccion = self.stock_tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione uno o más productos para eliminar")
            return
        if len(seleccion) == 1:
            item = self.stock_tree.item(seleccion[0])
            producto = item['values'][1]
            mensaje = f"¿Está seguro de que desea eliminar el producto '{producto}'?"
        else:
            mensaje = f"¿Está seguro de que desea eliminar los {len(seleccion)} productos seleccionados?"

        if not messagebox.askyesno("Confirmar", mensaje):
            return

        try:
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()

            for item_id in seleccion:
                item = self.stock_tree.item(item_id)
                cdb = item['values'][0]
                cursor.execute("DELETE FROM producto WHERE cdb=?", (cdb,))

            conn.commit()
            conn.close()

            self.actualizar_stock_tab()
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar productos: {e}")


    def actualizar_estado_botones_stock(self, event=None):
        seleccion = self.stock_tree.selection()
        estado = "normal" if seleccion else "disabled"
        self.stock_editar.config(state=estado)
        self.stock_eliminar.config(state=estado)

    def copiar_id_al_portapapeles(self, event):
        selected = self.stock_tree.selection()
        if not selected:
            return
        item = self.stock_tree.item(selected[0])
        cdb = item["values"][0]  # ID está en la primera columna
        self.clipboard_clear()
        self.clipboard_append(str(cdb))
        self.update()  # Mantiene el portapapeles incluso si se cierra la app
