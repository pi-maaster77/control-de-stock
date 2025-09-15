import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
from libreria.config import db
import libreria.querry as querry



class Vencimientos(ttk.Frame):
    """Pestaña para mostrar productos próximos a vencer.

    Muestra una tabla con columnas: CDB, Producto, Cantidad, Fecha de Vencimiento.
    Ordena por fecha de vencimiento ascendente (más reciente primero).
    """
    def __init__(self, notebook):
        super().__init__(notebook)
        self.frame = self
        self.setup_ui()
        notebook.add(self.frame, text="Vencimientos")

    def setup_ui(self):
        # Botones
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x")

        self.refresh_btn = ttk.Button(button_frame, text="🔃", width=2, command=self.actualizar)
        self.refresh_btn.pack(side="left", padx=5, pady=5)

        self.add_btn = ttk.Button(button_frame, text="+", width=2, command=self.agregar)
        self.add_btn.pack(side="left", padx=5, pady=5)

        self.edit_btn = ttk.Button(button_frame, text="✏️", width=2, command=self.editar, state="disabled")
        self.edit_btn.pack(side="left", padx=5, pady=5)

        self.delete_btn = ttk.Button(button_frame, text="🗑️", width=2, command=self.eliminar, state="disabled")
        self.delete_btn.pack(side="left", padx=5, pady=5)

        self.export_btn = ttk.Button(button_frame, text="Copiar CDB", width=10, command=self.copiar_cdb_seleccion)
        self.export_btn.pack(side="left", padx=5, pady=5)

        # Treeview
        self.tree = ttk.Treeview(self, columns=("CDB", "Producto", "Cantidad", "Fecha"), show="headings")
        self.tree.heading("CDB", text="Código de Barras")
        self.tree.heading("Producto", text="Producto")
        self.tree.heading("Cantidad", text="Cantidad")
        self.tree.heading("Fecha", text="Fecha de Vencimiento")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", self._on_double)

        # For mapping tree items to vencimientos.rowid
        self._rowid_map = {}

        # Label de estado
        self.status = ttk.Label(self, text="Cargando...")
        self.status.pack(fill="x")

        # Inicializar
        self.actualizar()

    def _on_select(self, event=None):
        sel = self.tree.selection()
        estado = "normal" if sel else "disabled"
        self.export_btn.config(state=estado)
        self.edit_btn.config(state=estado)
        self.delete_btn.config(state=estado)

    def _on_double(self, event=None):
        # Copia CDB al portapapeles al hacer doble click
        self.copiar_cdb_seleccion()

    def copiar_cdb_seleccion(self):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        cdb = item['values'][0]
        try:
            self.clipboard_clear()
            self.clipboard_append(str(cdb))
            self.update()
            messagebox.showinfo("Copiado", f"CDB {cdb} copiado al portapapeles")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo copiar: {e}")

    def actualizar(self):
        # Carga los vencimientos próximos desde la tabla `vencimientos` y une con `producto`.
        try:
            conn = querry.get_connection(db)
            cursor = conn.cursor()

            # Seleccionamos los vencimientos futuros incluyendo rowid calificado como v.rowid
            cursor.execute("""
                SELECT v.rowid, v.cdb, p.nombre, v.cantidad, v.fecha_vencimiento
                FROM vencimientos v
                LEFT JOIN producto p ON p.cdb = v.cdb
                WHERE v.fecha_vencimiento IS NOT NULL
                ORDER BY v.fecha_vencimiento ASC
            """)
            rows = cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Error", f"Error al leer vencimientos: {e}")
            rows = []
        finally:
            try:
                conn.close()
            except Exception:
                pass

        # Limpiar tabla
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        hoy = datetime.date.today()
        # reset map
        self._rowid_map.clear()

        for row in rows:
            rowid, cdb, nombre, cantidad, fecha = row
            try:
                # fecha puede venir como string o como date; formateamos a DD-MM-YYYY
                if fecha is None:
                    fecha_display = "N/A"
                elif isinstance(fecha, str):
                    try:
                        fd = datetime.datetime.fromisoformat(fecha).date()
                    except Exception:
                        # Intentar formatos comunes
                        try:
                            fd = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()
                        except Exception:
                            try:
                                fd = datetime.datetime.strptime(fecha, "%d-%m-%Y").date()
                            except Exception:
                                fd = None
                    fecha_display = fd.strftime("%d-%m-%Y") if fd else str(fecha)
                elif isinstance(fecha, datetime.date):
                    fecha_display = fecha.strftime("%d-%m-%Y")
                else:
                    # sqlite3 returns datetime objects sometimes
                    try:
                        fecha_display = fecha.strftime("%d-%m-%Y")
                    except Exception:
                        fecha_display = str(fecha)
            except Exception:
                fecha_display = str(fecha)

            iid = self.tree.insert("", "end", values=(cdb, nombre or "(Sin nombre)", cantidad, fecha_display))
            self._rowid_map[iid] = rowid

        self.status.config(text=f"{len(rows)} vencimientos cargados. Hoy: {hoy.strftime('%d-%m-%Y')}")

    # CRUD: Add / Edit / Delete
    def agregar(self):
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

        ttk.Label(ventana, text="Vencimiento:").grid(row=3, column=0, padx=5, pady=5)

        vencimiento_entry = ttk.Entry(ventana)
        vencimiento_entry.grid(row=3, column=1, padx=5, pady=5)

        agregar_button = ttk.Button(ventana, text="Agregar", command=lambda: guardar())
        agregar_button.grid(row=4, columnspan=2, padx=5, pady=5)
        agregar_button.config(state="disabled")

        # helper: parse fecha text into date or None (tolerant formats)
        def _parse_fecha_text(text):
            # accept datetime.date objects directly
            if isinstance(text, datetime.date):
                return text
            txt = '' if text is None else str(text).strip()
            if not txt or txt.upper() == 'N/A':
                return None
            for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d.%m.%Y"):
                try:
                    return datetime.datetime.strptime(txt, fmt).date()
                except Exception:
                    continue
            try:
                return datetime.date.fromisoformat(txt)
            except Exception:
                return None

        # validation: enable agregar_button only when cdb exists and, if perecedero, fecha valid
        def validar_formulario(event=None):
            try:
                cdb_txt = cdb_entry.get().strip()
                if not cdb_txt:
                    agregar_button.config(state='disabled')
                    return
                try:
                    cdb_val = int(cdb_txt)
                except Exception:
                    agregar_button.config(state='disabled')
                    return

                # cantidad should parse to int > 0
                try:
                    cantidad_val = int(cantidad_entry.get())
                    if cantidad_val <= 0:
                        agregar_button.config(state='disabled')
                        return
                except Exception:
                    agregar_button.config(state='disabled')
                    return

                # lookup product
                conn = querry.get_connection(db)
                cur = conn.cursor()
                cur.execute("SELECT nombre, perecedero FROM producto WHERE cdb=?", (cdb_val,))
                res = cur.fetchone()
                conn.close()
                if not res:
                    agregar_button.config(state='disabled')
                    return
                nombre, perecedero = res

                # if perecedero -> require valid date
                fecha_txt = ''
                try:
                    fecha_txt = vencimiento_entry.get().strip()
                except Exception:
                    # if widget is a DateEntry-like
                    try:
                        d = vencimiento_entry.get_date()
                        fecha_txt = d.strftime('%d-%m-%Y')
                    except Exception:
                        fecha_txt = ''

                if perecedero:
                    if not _parse_fecha_text(fecha_txt):
                        agregar_button.config(state='disabled')
                        return

                # passed all checks
                agregar_button.config(state='normal')
            except Exception:
                agregar_button.config(state='disabled')

        # bind validation to relevant fields
        cdb_entry.bind('<KeyRelease>', validar_formulario)
        cantidad_entry.bind('<KeyRelease>', validar_formulario)
        vencimiento_entry.bind('<KeyRelease>', validar_formulario)

        # helper to lookup product and enable/disable fecha according to perecedero
        def buscar_producto(event=None):
            try:
                cdb_txt = cdb_entry.get().strip()
                if not cdb_txt:
                    nombre_var.set("")
                    return
                cdb_val = int(cdb_txt)
                conn = querry.get_connection(db)
                cur = conn.cursor()
                cur.execute("SELECT nombre, perecedero FROM producto WHERE cdb=?", (cdb_val,))
                res = cur.fetchone()
                conn.close()
                if res:
                    nombre, perecedero = res
                    nombre_var.set(nombre)
                    # enable fecha only if perecedero truthy
                    if perecedero:
                        # keep field as-is (user requested not to disable); nothing to do
                        pass
                    else:
                        # clear the date field for non-perishable products but do not disable it
                        try:
                            vencimiento_entry.delete(0, tk.END)
                        except Exception:
                            try:
                                vencimiento_entry.delete(0, tk.END)
                            except Exception:
                                pass
                else:
                    nombre_var.set("Producto no encontrado")
                    # leave fecha_entry enabled but clear it
                    try:
                        vencimiento_entry.delete(0, tk.END)
                    except Exception:
                        pass
            except Exception:
                nombre_var.set("")
                try:
                    vencimiento_entry.delete(0, tk.END)
                except Exception:
                    pass

        cdb_entry.bind('<KeyRelease>', buscar_producto)

        def guardar():
            try:
                cdb = int(cdb_entry.get())
                cantidad = int(cantidad_entry.get())
                # check product and perecedero flag
                conn = querry.get_connection(db)
                cur = conn.cursor()
                cur.execute("SELECT nombre, perecedero FROM producto WHERE cdb=?", (cdb,))
                prod = cur.fetchone()
                if not prod:
                    conn.close()
                    raise ValueError("Producto no existe")
                nombre_db, perecedero = prod

                # read from DateEntry or Entry
                try:
                    fecha_text = vencimiento_entry.get().strip()
                except Exception:
                    try:
                        d = vencimiento_entry.get_date()
                        fecha_text = d.strftime('%d-%m-%Y')
                    except Exception:
                        fecha_text = ''

                if perecedero:
                    if not fecha_text:
                        conn.close()
                        raise ValueError("Producto perecedero: la fecha de vencimiento es requerida")
                    fecha = None
                    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d.%m.%Y"):
                        try:
                            fecha = datetime.datetime.strptime(fecha_text, fmt).date()
                            break
                        except Exception:
                            continue
                    if not fecha:
                        try:
                            fecha = datetime.date.fromisoformat(fecha_text)
                        except Exception:
                            conn.close()
                            raise ValueError("Formato de fecha inválido. Use DD-MM-YYYY (u otro formato común)")
                    # Insertar vencimiento. Guardar fecha como ISO (YYYY-MM-DD)
                    cur.execute("INSERT INTO vencimientos (cdb, cantidad, fecha_vencimiento) VALUES (?, ?, ?)",
                                (cdb, cantidad, fecha.isoformat()))
                else:
                    # non-perishable: do not allow a date
                    if fecha_text and fecha_text.strip():
                        conn.close()
                        raise ValueError("Producto no perecedero: no puede asignarse fecha de vencimiento")
                    cur.execute("INSERT INTO vencimientos (cdb, cantidad, fecha_vencimiento) VALUES (?, ?, ?)",
                                (cdb, cantidad, None))
                conn.commit()
                conn.close()
                ventana.destroy()
                self.actualizar()
            except ValueError as ve:
                messagebox.showerror("Error", str(ve))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo agregar: {e}")

    def _parse_fecha_text(self, text):
        """Parsea fechas tolerantes y devuelve datetime.date o None."""
        # accept datetime.date objects directly
        if isinstance(text, datetime.date):
            return text
        txt = '' if text is None else str(text).strip()
        if not txt or txt.upper() == 'N/A':
            return None
        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d.%m.%Y"):
            try:
                return datetime.datetime.strptime(txt, fmt).date()
            except Exception:
                continue
        try:
            return datetime.date.fromisoformat(txt)
        except Exception:
            return None

    def editar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Advertencia", "Seleccione un vencimiento para editar")
            return

        iid = sel[0]
        rowid = self._rowid_map.get(iid)
        if rowid is None:
            messagebox.showerror("Error", "No se pudo identificar el registro seleccionado")
            return

        # traer datos desde la base de datos usando rowid
        try:
            conn = querry.get_connection(db)
            cur = conn.cursor()
            cur.execute(
                "SELECT v.cdb, p.nombre, v.cantidad, v.fecha_vencimiento FROM vencimientos v LEFT JOIN producto p ON p.cdb = v.cdb WHERE v.rowid = ?",
                (rowid,)
            )
            result = cur.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo obtener el registro desde la BD:\n{e}")
            return

        if not result:
            messagebox.showerror("Error", "El registro ya no existe en la base de datos")
            return

        cdb_val, nombre_val, cantidad_val, fecha_val = result

        # Conversión a datetime.date si hay fecha (usar el parser tolerante)
        fecha_date = None
        if fecha_val:
            fecha_date = self._parse_fecha_text(fecha_val) or None

        ventana = tk.Toplevel(self)
        ventana.title("Editar Vencimiento")

        nombre_var = tk.StringVar(value=nombre_val or "")

        ttk.Label(ventana, text="Código de Barras:").grid(row=0, column=0, padx=5, pady=5)
        cdb_entry = ttk.Entry(ventana)
        cdb_entry.grid(row=0, column=1, padx=5, pady=5)
        cdb_entry.insert(0, str(cdb_val))

        ttk.Label(ventana, text="Producto:").grid(row=1, column=0, padx=5, pady=5)
        producto_label = ttk.Label(ventana, textvariable=nombre_var)
        producto_label.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(ventana, text="Cantidad:").grid(row=2, column=0, padx=5, pady=5)
        cantidad_entry = tk.Spinbox(ventana, from_=1, to=1000, width=5)
        cantidad_entry.grid(row=2, column=1, padx=5, pady=5)
        cantidad_entry.delete(0, tk.END)
        cantidad_entry.insert(0, str(cantidad_val))

        ttk.Label(ventana, text="Vencimiento:").grid(row=3, column=0, padx=5, pady=5)
        vencimiento_entry = ttk.Entry(ventana)
        vencimiento_entry.grid(row=3, column=1, padx=5, pady=5)
        if fecha_date:
            # show in DD-MM-YYYY for easier entry
            vencimiento_entry.insert(0, fecha_date.strftime("%d-%m-%Y"))

        # helper: lookup product and clear fecha for non-perecedero (but keep field enabled)
        def buscar_producto_edit(event=None):
            try:
                cdb_txt = cdb_entry.get().strip()
                if not cdb_txt:
                    nombre_var.set("")
                    return
                try:
                    cdb_int = int(cdb_txt)
                except Exception:
                    nombre_var.set("")
                    return
                conn = querry.get_connection(db)
                cur = conn.cursor()
                cur.execute("SELECT nombre, perecedero FROM producto WHERE cdb=?", (cdb_int,))
                res = cur.fetchone()
                conn.close()
                if res:
                    nm, perec = res
                    nombre_var.set(nm)
                    if not perec:
                        try:
                            vencimiento_entry.delete(0, tk.END)
                        except Exception:
                            pass
                else:
                    nombre_var.set("Producto no encontrado")
            except Exception:
                nombre_var.set("")

        # validation for edit: enable save only when product exists and, if perecedero, fecha valid
        def validar_formulario_edit(event=None):
            try:
                cdb_txt = cdb_entry.get().strip()
                if not cdb_txt:
                    guardar_btn.config(state='disabled')
                    return
                try:
                    cdb_int = int(cdb_txt)
                except Exception:
                    guardar_btn.config(state='disabled')
                    return

                try:
                    cantidad_int = int(cantidad_entry.get())
                    if cantidad_int <= 0:
                        guardar_btn.config(state='disabled')
                        return
                except Exception:
                    guardar_btn.config(state='disabled')
                    return

                conn = querry.get_connection(db)
                cur = conn.cursor()
                cur.execute("SELECT nombre, perecedero FROM producto WHERE cdb=?", (cdb_int,))
                prod = cur.fetchone()
                conn.close()
                if not prod:
                    guardar_btn.config(state='disabled')
                    return
                _, perec = prod

                fecha_txt = ''
                try:
                    fecha_txt = vencimiento_entry.get().strip()
                except Exception:
                    fecha_txt = ''

                if perec:
                    if not self._parse_fecha_text(fecha_txt):
                        guardar_btn.config(state='disabled')
                        return

                guardar_btn.config(state='normal')
            except Exception:
                try:
                    guardar_btn.config(state='disabled')
                except Exception:
                    pass

        # create guardar button
        guardar_btn = ttk.Button(ventana, text="Guardar cambios", command=lambda: self._guardar_edicion(
            rowid, cdb_entry.get(), cantidad_entry.get(), vencimiento_entry.get(), ventana))
        guardar_btn.grid(row=4, columnspan=2, padx=5, pady=10)

        # bind events
        cdb_entry.bind('<KeyRelease>', buscar_producto_edit)
        cdb_entry.bind('<KeyRelease>', validar_formulario_edit)
        cantidad_entry.bind('<KeyRelease>', validar_formulario_edit)
        vencimiento_entry.bind('<KeyRelease>', validar_formulario_edit)

        # initialize
        try:
            buscar_producto_edit()
        except Exception:
            pass
        try:
            validar_formulario_edit()
        except Exception:
            try:
                guardar_btn.config(state='disabled')
            except Exception:
                pass

    def _guardar_edicion(self, rowid, cdb, cantidad, fecha, ventana):
        try:
            conn = querry.get_connection(db)
            cur = conn.cursor()

            # normalize inputs
            try:
                cdb_int = int(str(cdb).strip())
            except Exception:
                raise ValueError("CDB inválido")
            try:
                cantidad_int = int(str(cantidad).strip())
            except Exception:
                raise ValueError("Cantidad inválida")

            fecha_iso = None
            if fecha and str(fecha).strip():
                parsed = self._parse_fecha_text(fecha)
                if not parsed:
                    raise ValueError("Fecha inválida")
                fecha_iso = parsed.isoformat()

            cur.execute(
                "UPDATE vencimientos SET cdb=?, cantidad=?, fecha_vencimiento=? WHERE rowid=?",
                (cdb_int, cantidad_int, fecha_iso, rowid)
            )
            conn.commit()
            conn.close()
            ventana.destroy()
            self.actualizar()
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def eliminar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Advertencia", "Seleccione uno o más vencimientos para eliminar")
            return

        if not messagebox.askyesno("Confirmar", f"¿Eliminar {len(sel)} vencimiento(s)?"):
            return

        try:
            conn = querry.get_connection(db)
            cur = conn.cursor()
            for iid in sel:
                rowid = self._rowid_map.get(iid)
                if rowid:
                    cur.execute("DELETE FROM vencimientos WHERE rowid=?", (rowid,))
            conn.commit()
            conn.close()
            self.actualizar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar: {e}")
