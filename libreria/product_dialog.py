import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

"""
Reusable product selection / add dialog.

Usage:
  def on_add(item):
      # item is a dict: {'cdb': int, 'nombre': str, 'precio_venta': float, 'cantidad': int}

  ProductDialog(parent, db, on_add)

This encapsulates the UI and database lookup so multiple tabs can reuse it.
"""


class ProductDialog:
    def __init__(self, parent, db_path, on_add, title="Añadir Producto", price_calc=None, mode="venta"):
        self.parent = parent
        self.db = db_path
        self.on_add = on_add
        self.price_calc = price_calc or self._default_price_calc
        self.mode = mode  # 'venta' or 'compra'

        self.top = tk.Toplevel(parent)
        self.top.title(title)

        self.nombre_var = tk.StringVar()
        self.stock_maximo = tk.IntVar(value=1)

        tk.Label(self.top, text="Código de Barras:").grid(row=0, column=0, padx=5, pady=5)
        self.cdb_entry = tk.Entry(self.top)
        self.cdb_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.top, text="Producto:").grid(row=1, column=0, padx=5, pady=5)
        producto_label = tk.Label(self.top, textvariable=self.nombre_var)
        producto_label.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.top, text="Cantidad:").grid(row=2, column=0, padx=5, pady=5)
        self.cantidad_entry = tk.Spinbox(self.top, from_=1, to=1, width=5)
        self.cantidad_entry.grid(row=2, column=1, padx=5, pady=5)
        self.cantidad_entry.delete(0, tk.END)
        self.cantidad_entry.insert(0, 1)

        # If modo compra, añadir campos precio y vencimiento
        # If modo vencimiento, añadir solo vencimiento (sin precio)
        if self.mode == "compra":
            tk.Label(self.top, text="Precio Compra:").grid(row=3, column=0, padx=5, pady=5)
            self.precio_entry = tk.Entry(self.top)
            self.precio_entry.grid(row=3, column=1, padx=5, pady=5)

            tk.Label(self.top, text="Vencimiento:").grid(row=4, column=0, padx=5, pady=5)
            self.vencimiento_entry = tk.Entry(self.top)
            self.vencimiento_entry.grid(row=4, column=1, padx=5, pady=5)
        elif self.mode in ("vencimiento", "vencimientos"):
            tk.Label(self.top, text="Vencimiento:").grid(row=3, column=0, padx=5, pady=5)
            self.vencimiento_entry = tk.Entry(self.top)
            self.vencimiento_entry.grid(row=3, column=1, padx=5, pady=5)

        # place the Add button after the last row depending on mode
        # rows: 0=cdb,1=nombre,2=cantidad, 3=(vencimiento or precio), 4=(vencimiento if compra), button after last
        if self.mode == "compra":
            button_row = 5
        elif self.mode in ("vencimiento", "vencimientos"):
            button_row = 4
        else:
            button_row = 3
        self.agregar_button = tk.Button(self.top, text="Agregar", command=self._agregar)
        self.agregar_button.grid(row=button_row, column=0, columnspan=2, padx=5, pady=5)
        self.agregar_button.config(state="disabled")

        # Bind lookup
        self.cdb_entry.bind("<KeyRelease>", self._buscar_producto)
        # UX: focus codigo field and make the dialog transient
        try:
            self.cdb_entry.focus_set()
            self.top.transient(self.parent)
            self.top.grab_set()
        except Exception:
            pass

    def _default_price_calc(self, precio, margen):
        try:
            margen_val = margen if margen is not None else 0.20
            return precio * (1 + margen_val)
        except Exception:
            return float(precio or 0)

    def _parse_fecha_text(self, text):
        """Parsea fechas tolerantes y devuelve datetime.date o None."""
        import datetime as _dt
        if isinstance(text, _dt.date):
            return text
        txt = '' if text is None else str(text).strip()
        if not txt or txt.upper() == 'N/A':
            return None
        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d.%m.%Y"):
            try:
                return _dt.datetime.strptime(txt, fmt).date()
            except Exception:
                continue
        try:
            return _dt.date.fromisoformat(txt)
        except Exception:
            return None

    def _buscar_producto(self, event=None):
        try:
            cdb = int(self.cdb_entry.get())
        except ValueError:
            self.nombre_var.set("Código inválido")
            self.agregar_button.config(state="disabled")
            return

        try:
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            # Include perecedero for compra mode
            cursor.execute("SELECT nombre, precio, cantidad, margen, perecedero FROM producto WHERE cdb=?", (cdb,))
            result = cursor.fetchone()
            conn.close()

            if result:
                # result may include perecedero depending on schema
                if len(result) == 5:
                    nombre, precio, cantidad_disponible, margen, perecedero = result
                else:
                    nombre, precio, cantidad_disponible, margen = result
                    perecedero = False

                precio_venta = self.price_calc(precio, margen)
                self.nombre_var.set(nombre)
                self.stock_maximo.set(cantidad_disponible or 1)
                # update spinbox limit
                self.cantidad_entry.config(to=cantidad_disponible or 1)
                self.cantidad_entry.delete(0, tk.END)
                self.cantidad_entry.insert(0, 1)

                # If compra mode, prefill price and enable/disable vencimiento
                if self.mode == "compra":
                    try:
                        self.precio_entry.delete(0, tk.END)
                        self.precio_entry.insert(0, f"{precio:.2f}")
                    except Exception:
                        pass
                    if perecedero:
                        try:
                            self.vencimiento_entry.config(state="normal")
                        except Exception:
                            pass
                    else:
                        try:
                            self.vencimiento_entry.delete(0, tk.END)
                        except Exception:
                            pass
                        try:
                            self.vencimiento_entry.config(state="disabled")
                        except Exception:
                            pass
                elif self.mode in ("vencimiento", "vencimientos"):
                    # enable/disable vencimiento field depending on perecedero
                    if perecedero:
                        try:
                            self.vencimiento_entry.config(state="normal")
                        except Exception:
                            pass
                    else:
                        try:
                            self.vencimiento_entry.delete(0, tk.END)
                        except Exception:
                            pass
                        try:
                            self.vencimiento_entry.config(state="disabled")
                        except Exception:
                            pass

                # store perecedero for _agregar
                self._last_perecedero = bool(perecedero)

                self.agregar_button.config(state="normal")
            else:
                self.nombre_var.set("Producto no encontrado")
                self.cantidad_entry.config(to=1)
                self.cantidad_entry.delete(0, tk.END)
                self.cantidad_entry.insert(0, 1)
                self.agregar_button.config(state="disabled")
        except Exception as e:
            self.nombre_var.set(f"Error: {e}")
            self.agregar_button.config(state="disabled")

    def _agregar(self):
        try:
            cdb = int(self.cdb_entry.get())
            cantidad = int(self.cantidad_entry.get())

            if not (1 <= cantidad <= self.stock_maximo.get()):
                raise ValueError("La cantidad debe estar dentro del stock disponible")

            # fetch product info again to be safe
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            cursor.execute("SELECT nombre, precio, margen, perecedero FROM producto WHERE cdb=?", (cdb,))
            result = cursor.fetchone()
            conn.close()

            if result:
                if len(result) == 4:
                    nombre, precio, margen, perecedero = result
                else:
                    nombre, precio, margen = result
                    perecedero = False

                # Build item depending on mode
                if self.mode == "compra":
                    try:
                        precio_compra = float(self.precio_entry.get())
                    except Exception:
                        raise ValueError("Precio inválido")

                    venc = ''
                    if bool(perecedero):
                        venc = self.vencimiento_entry.get().strip()
                        if not venc:
                            raise ValueError("Producto perecedero: la fecha de vencimiento es requerida.")

                    item = {
                        'cdb': cdb,
                        'nombre': nombre,
                        'precio': precio_compra,
                        'cantidad': cantidad,
                        'perecedero': bool(perecedero),
                        'vencimiento': venc,
                    }
                elif self.mode in ("vencimiento", "vencimientos"):
                    # handle vencimiento-specific flow
                    venc_txt = ''
                    try:
                        venc_txt = self.vencimiento_entry.get().strip()
                    except Exception:
                        venc_txt = ''

                    if bool(perecedero):
                        fecha = self._parse_fecha_text(venc_txt)
                        if not fecha:
                            raise ValueError("Producto perecedero: la fecha de vencimiento es requerida y debe tener formato válido")
                        venc_iso = fecha.isoformat()
                    else:
                        if venc_txt:
                            raise ValueError("Producto no perecedero: no puede asignarse fecha de vencimiento")
                        venc_iso = None

                    item = {
                        'cdb': cdb,
                        'nombre': nombre,
                        'cantidad': cantidad,
                        'perecedero': bool(perecedero),
                        'vencimiento': venc_iso,
                    }
                else:
                    precio_venta = self.price_calc(precio, margen)
                    item = {
                        'cdb': cdb,
                        'nombre': nombre,
                        'precio_venta': precio_venta,
                        'cantidad': cantidad,
                    }

                # call callback
                if callable(self.on_add):
                    self.on_add(item)
                self.top.destroy()
            else:
                messagebox.showerror("Error", "Producto no encontrado")
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Error al añadir producto: {e}")
