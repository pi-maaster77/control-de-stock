import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import libreria.querry as querry
from libreria.config import db
from libreria.product_dialog import ProductDialog


class Vencimientos(ttk.Frame):
    """Pestaña para mostrar productos próximos a vencer y gestionar vencimientos."""
    def __init__(self, notebook):
        super().__init__(notebook)
        self.frame = self
        self._rowid_map = {}  # map tree iid -> rowid in sqlite
        self.setup_ui()
        notebook.add(self.frame, text="Vencimientos")

    def setup_ui(self):
        # botones
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x")

        self.btn_actualizar = ttk.Button(btn_frame, text="🔃", command=self.actualizar)
        self.btn_actualizar.pack(side="left", padx=5, pady=5)

        self.btn_anadir = ttk.Button(btn_frame, text="+", command=self.anadir)
        self.btn_anadir.pack(side="left", padx=5, pady=5)

        self.btn_editar = ttk.Button(btn_frame, text="✏️", command=self.editar, state="disabled")
        self.btn_editar.pack(side="left", padx=5, pady=5)

        self.btn_eliminar = ttk.Button(btn_frame, text="🗑️", command=self.eliminar, state="disabled")
        self.btn_eliminar.pack(side="left", padx=5, pady=5)

        # tabla
        self.tree = ttk.Treeview(self, columns=("cdb", "producto", "cantidad", "vencimiento"), show="headings")
        self.tree.heading("cdb", text="Código de Barras")
        self.tree.heading("producto", text="Producto")
        self.tree.heading("cantidad", text="Cantidad")
        self.tree.heading("vencimiento", text="Vencimiento")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _on_select(self, event=None):
        sel = self.tree.selection()
        estado = "normal" if sel else "disabled"
        self.btn_editar.config(state=estado)
        self.btn_eliminar.config(state=estado)

    def actualizar(self):
        """Carga los vencimientos desde la base de datos y los muestra en la tabla."""
        try:
            conn = querry.get_connection(db)
            cur = conn.cursor()
            cur.execute("SELECT rowid, cdb, cantidad, fecha_vencimiento FROM vencimientos ORDER BY fecha_vencimiento NULLS LAST")
            rows = cur.fetchall()
            conn.close()
        except Exception:
            # fallback simple query without ordering nuance
            try:
                conn = querry.get_connection(db)
                cur = conn.cursor()
                cur.execute("SELECT rowid, cdb, cantidad, fecha_vencimiento FROM vencimientos")
                rows = cur.fetchall()
                conn.close()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer la base de datos: {e}")
                return

        # limpiar tabla
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        self._rowid_map.clear()

        for row in rows:
            rowid, cdb, cantidad, fecha = row
            fecha_txt = ''
            if fecha:
                try:
                    # fecha puede venir como 'YYYY-MM-DD' o datetime.date
                    if isinstance(fecha, (str, bytes)):
                        fecha_txt = str(fecha)
                    elif isinstance(fecha, datetime.date):
                        fecha_txt = fecha.isoformat()
                    else:
                        fecha_txt = str(fecha)
                except Exception:
                    fecha_txt = str(fecha)

            # lookup product name
            nombre = ''
            try:
                conn2 = querry.get_connection(db)
                cur2 = conn2.cursor()
                cur2.execute("SELECT nombre FROM producto WHERE cdb=?", (cdb,))
                res = cur2.fetchone()
                conn2.close()
                if res:
                    nombre = res[0]
            except Exception:
                nombre = ''

            iid = self.tree.insert("", "end", values=(cdb, nombre, cantidad, fecha_txt))
            self._rowid_map[iid] = rowid

        self._on_select()

    def anadir(self):
        """Abre el ProductDialog en modo 'vencimiento' y añade el resultado a la BD."""
        def on_add(item):
            try:
                cdb = int(item.get('cdb'))
                cantidad = int(item.get('cantidad'))
                venc_txt = item.get('vencimiento') or ''

                fecha = self._parse_fecha_text(venc_txt)
                conn = querry.get_connection(db)
                cur = conn.cursor()
                if fecha:
                    cur.execute("INSERT INTO vencimientos (cdb, cantidad, fecha_vencimiento) VALUES (?, ?, ?)",
                                (cdb, cantidad, fecha.isoformat()))
                else:
                    cur.execute("INSERT INTO vencimientos (cdb, cantidad, fecha_vencimiento) VALUES (?, ?, ?)",
                                (cdb, cantidad, None))
                conn.commit()
                conn.close()
                self.actualizar()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo agregar vencimiento: {e}")

        ProductDialog(self, db, on_add, title="Añadir Vencimiento", mode="vencimiento")

    def _parse_fecha_text(self, text):
        """Parsea fechas tolerantes y devuelve datetime.date o None."""
        if isinstance(text, datetime.date):
            return text
        txt = '' if text is None else str(text).strip()
        if not txt or txt.upper() == 'N/A':
            return None
        # probar varios formatos comunes
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
        cantidad_entry = tk.Spinbox(ventana, from_=1, to=1000000, width=7)
        cantidad_entry.grid(row=2, column=1, padx=5, pady=5)
        cantidad_entry.delete(0, tk.END)
        cantidad_entry.insert(0, str(cantidad_val))

        ttk.Label(ventana, text="Vencimiento:").grid(row=3, column=0, padx=5, pady=5)
        vencimiento_entry = ttk.Entry(ventana)
        vencimiento_entry.grid(row=3, column=1, padx=5, pady=5)
        if fecha_date:
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
