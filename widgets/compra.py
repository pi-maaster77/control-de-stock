import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime


from libreria.config import db
import libreria.querry as querry
from typing import Optional
from libreria.product_dialog import ProductDialog

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

        self.compra_actualizar = ttk.Button(self.compra_button_frame, text="📄", command=self.limpiar, )
        self.compra_actualizar.pack(side="left", padx=5, pady=5)

        self.compra_anadir = ttk.Button(self.compra_button_frame, text="+", command=self.anadir, )
        self.compra_anadir.pack(side="left", padx=5, pady=5)

        self.compra_editar = ttk.Button(self.compra_button_frame, text="✏️", command=self.editar, state="disabled")
        self.compra_editar.pack(side="left", padx=5, pady=5)

        self.compra_eliminar = ttk.Button(self.compra_button_frame, text="🗑️", command=self.eliminar, state="disabled")
        self.compra_eliminar.pack(side="left", padx=5, pady=5)

        self.compra_tree = ttk.Treeview(self, columns=("ID", "Producto", "Precio", "Cantidad", "Vencimiento"), show="headings")
        self.compra_tree.heading("ID", text="Código de Barras")
        self.compra_tree.heading("Producto", text="Producto")
        self.compra_tree.heading("Precio", text="Precio Compra")
        self.compra_tree.heading("Cantidad", text="Cantidad")
        self.compra_tree.heading("Vencimiento", text="Próximo Vencimiento")
        self.compra_tree.pack(fill="both", expand=True)

        self.compra_total_frame = ttk.Frame(self)
        self.compra_total_frame.pack(fill="x")

        self.compra_resultado = ttk.Label(self.compra_total_frame, text="Total: $0", font=("Arial", 14))
        self.compra_resultado.pack()

        self.compra_confirmar = ttk.Button(self.compra_total_frame, text="✔", command=self.confirmar, )
        self.compra_confirmar.pack(side="left", padx=5, pady=5)

        self.compra_tree.bind("<<TreeviewSelect>>", self.actualizar_estado_botones)

    def limpiar(self):
        for item in self.compra_tree.get_children():
            self.compra_tree.delete(item)
        self.total = 0
        self.compra_resultado.config(text=f"Total: ${self.total:.2f}")

    # Helper para parsear fechas
    def _parse_fecha(self, text: str) -> Optional[datetime.date]:
        if not text:
            return None
        if isinstance(text, datetime.date):
            return text
        txt = str(text).strip()
        formatos = ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d.%m.%Y"]
        for fmt in formatos:
            try:
                return datetime.datetime.strptime(txt, fmt).date()
            except Exception:
                continue
        try:
            return datetime.date.fromisoformat(txt)
        except Exception:
            return None

    # Helper para leer fecha desde widget de forma robusta
    def _leer_fecha_desde_widget(self, widget) -> Optional[datetime.date]:
        try:
            if hasattr(widget, "get_date"):
                val = widget.get_date()
                if isinstance(val, datetime.date):
                    return val
                if isinstance(val, str) and val.strip():
                    return self._parse_fecha(val.strip())
                return None
            txt = widget.get().strip()
            return self._parse_fecha(txt) if txt else None
        except Exception:
            try:
                txt = str(widget.get()).strip()
                return self._parse_fecha(txt) if txt else None
            except Exception:
                return None

    def confirmar(self):
        conn = querry.get_connection(db)
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO compra (fecha) VALUES (?)", (datetime.datetime.now(),))
            compra_id = cursor.lastrowid

            for item_id in self.compra_tree.get_children():
                values = self.compra_tree.item(item_id)['values']
                try:
                    cdb = int(values[0])
                    precio_compra = float(values[2])
                    cantidad = int(values[3])
                    raw_venc = values[4]

                    if raw_venc is None or str(raw_venc).strip() in ("", "N/A", "None"):
                        fecha_de_vencimiento = None
                    else:
                        fecha_de_vencimiento = self._parse_fecha(str(raw_venc).strip())
                        if not fecha_de_vencimiento:
                            conn.rollback()
                            messagebox.showerror("Error", f"Formato de fecha inválido para el producto {values}.")
                            return

                    cursor.execute("SELECT cantidad, precio FROM producto WHERE cdb=?", (cdb,))
                    result = cursor.fetchone()

                    if fecha_de_vencimiento:
                        fecha_iso = fecha_de_vencimiento.isoformat()
                        cursor.execute("INSERT INTO vencimientos (cdb, cantidad, fecha_vencimiento) VALUES (?, ?, ?)", 
                                       (cdb, cantidad, fecha_iso))
                    if result:
                        cantidad_actual, precio_actual = result
                        nueva_cantidad = cantidad_actual + cantidad
                        cursor.execute("UPDATE producto SET cantidad=? WHERE cdb=?", (nueva_cantidad, cdb))

                        if abs(precio_actual - precio_compra) > 0.01:
                            cursor.execute("UPDATE producto SET precio=? WHERE cdb=?", (precio_compra, cdb))
                    else:
                        messagebox.showerror("Error", f"Producto no existe: {cdb}")
                        continue

                    cursor.execute("INSERT INTO compra_detalle (compra, cdb, cantidad, precio_compra) VALUES (?, ?, ?, ?)", 
                                   (compra_id, cdb, cantidad, precio_compra))
                    cursor.execute("UPDATE dinero SET total = total - ? WHERE id = 1", (precio_compra * cantidad,))
                except Exception as e:
                    messagebox.showerror("Error", f"Error al procesar item {values}: {e}")

            conn.commit()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Error al registrar compra: {e}")
        finally:
            conn.close()

        self.limpiar()
        messagebox.showinfo("Compra", "Compra registrada exitosamente.")

    def anadir(self):
        # Use ProductDialog in 'compra' mode
        def on_add(item):
            try:
                # item contains cdb, nombre, precio, cantidad, perecedero, vencimiento
                cdb = item.get('cdb')
                nombre = item.get('nombre')
                precio = item.get('precio')
                cantidad = item.get('cantidad')
                venc = item.get('vencimiento') or ""

                venc_display = venc if venc else "N/A"
                self.compra_tree.insert("", "end", values=(cdb, nombre, precio, cantidad, venc_display))
                self.total += cantidad * precio
                self.compra_resultado.config(text=f"Total: ${self.total:.2f}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al procesar producto añadido: {e}")

        ProductDialog(self, db, on_add, title="Añadir Producto a la Compra", mode="compra")

    def editar(self):
        seleccion = self.compra_tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto para editar")
            return

        item = self.compra_tree.item(seleccion[0])
        try:
            cdb, nombre, precio, cantidad, vencimiento_val = item['values']
        except Exception:
            vals = item.get('values', [])
            cdb = vals[0] if len(vals) > 0 else ''
            nombre = vals[1] if len(vals) > 1 else ''
            precio = vals[2] if len(vals) > 2 else 0
            cantidad = vals[3] if len(vals) > 3 else 1
            vencimiento_val = vals[4] if len(vals) > 4 else "N/A"

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

        ttk.Label(ventana, text="Vencimiento:").grid(row=3, column=0, padx=5, pady=5)
        vencimiento_entry = ttk.Entry(ventana)
        vencimiento_entry.insert(0, vencimiento_val if vencimiento_val != "N/A" else "")
        vencimiento_entry.grid(row=3, column=1, padx=5, pady=5)

        def guardar():
            try:
                nueva_cantidad = int(cantidad_entry.get())
                nuevo_precio = float(precio_entry.get())
                nueva_fecha = self._leer_fecha_desde_widget(vencimiento_entry)
                fecha_venc = nueva_fecha.strftime("%d-%m-%Y") if nueva_fecha else "N/A"
                self.compra_tree.item(seleccion[0], values=(cdb, nombre, nuevo_precio, nueva_cantidad, fecha_venc))
                self.recalcular_total()
                ventana.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo editar: {e}")

        ttk.Button(ventana, text="Guardar", command=guardar).grid(row=4, columnspan=2, padx=5, pady=5)

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
