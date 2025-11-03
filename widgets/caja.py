import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import urllib.request
import json
from libreria.toplevel import TopLevel

class Caja(ttk.Frame):
    def __init__(self, notebook, db):
        super().__init__(notebook)
        self.db = db
        self.frame = self
        self.total_var = tk.StringVar()
        self.eur_var = tk.StringVar()
        self.usd_var = tk.StringVar()
        # Moneda base // se puede cambiar la moneda de la caja // e.g. 'USD', 'EUR', 'ARS')
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("SELECT moneda1 FROM CONFIGURACION") 
        self.base_currency = cursor.fetchone()[0]
        cursor.execute("SELECT moneda2, moneda3 FROM CONFIGURACION")
        self.monedas_secundarias = cursor.fetchone()
        print(self.monedas_secundarias)
        conn.close()
        print(self.base_currency)
        self.setup_ui()
        self.actualizar_total()
        notebook.add(self.frame, text="Caja")

    def setup_ui(self):
        ttk.Label(self, text="Total en caja:").pack(pady=10)
        self.total_entry = ttk.Entry(self, textvariable=self.total_var, justify="center", width=20)
        self.total_entry.pack(pady=5)

        # etiquetas de conversión
        conv_frame = ttk.Frame(self)
        conv_frame.pack(pady=5)
        self.moneda1 = ttk.Label(conv_frame, text=self.monedas_secundarias[0])
        self.moneda1.grid(row=0, column=0, sticky="e", padx=5)
        ttk.Label(conv_frame, textvariable=self.eur_var).grid(row=0, column=1, sticky="w", padx=5)
        self.moneda2 = ttk.Label(conv_frame, text=self.monedas_secundarias[1])
        self.moneda2.grid(row=1, column=0, sticky="e", padx=5)
        ttk.Label(conv_frame, textvariable=self.usd_var).grid(row=1, column=1, sticky="w", padx=5)

        botones_frame = ttk.Frame(self)
        botones_frame.pack(pady=10)

        ttk.Button(botones_frame, text="Actualizar", command=self.actualizar_total).grid(row=0, column=0, padx=5)
        ttk.Button(botones_frame, text="Modificar", command=self.modificar_total).grid(row=0, column=1, padx=5)
        ttk.Button(botones_frame, text="+ Agregar", command=self.agregar_dinero).grid(row=0, column=2, padx=5)
        ttk.Button(botones_frame, text="- Quitar", command=self.quitar_dinero).grid(row=0, column=3, padx=5)
        ttk.Button(botones_frame, text="Configurar monedas", command=self.configurar_monedas).grid(row=0, column=4, padx=5)

    def configurar_monedas(self):
        monedas = ["ARS", "USD", "EUR", "BRL", "CLP"]
        popup = TopLevel(self)
        popup.title("Configurar monedas")
        ttk.Label(popup, text="Moneda principal:").pack(padx=10, pady=(10, 2))
        moneda_principal = tk.StringVar(value=self.base_currency)
        combo = ttk.Combobox(popup, values=monedas, textvariable=moneda_principal, state="readonly")
        combo.pack(padx=10, pady=2)

        ttk.Label(popup, text="Monedas secundarias:").pack(padx=10, pady=(10, 2))
        secundarias_vars = {}
        for m in monedas:
            if m != self.base_currency:
                var = tk.BooleanVar(value=(m in self.monedas_secundarias))
                chk = ttk.Checkbutton(popup, text=m, variable=var)
                chk.pack(anchor="w", padx=20)
                secundarias_vars[m] = var

        def guardar():
            self.base_currency = moneda_principal.get()
            # Solo mostrar secundarias seleccionadas y distintas de principal
            seleccionadas = [m for m, v in secundarias_vars.items() if v.get() and m != self.base_currency]
            # Actualizar etiquetas y lógica de conversión
            self.monedas_secundarias = seleccionadas
            if len(seleccionadas) < 2:
                while len(seleccionadas) < 2:
                    seleccionadas.append("")
            popup.destroy()
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            cursor.execute("""UPDATE configuracion                                
                           SET moneda1=?, moneda2=?, moneda3=?
                                WHERE id=1 """, (self.base_currency, seleccionadas[0], seleccionadas[1]))
            cursor.execute("SELECT * FROM configuracion")
            conn.commit()
            print(cursor.fetchall())
            print("monedas actualizadas")
            self.moneda1.configure(text=self.monedas_secundarias[0])
            self.moneda2.configure(text=self.monedas_secundarias[1])
            self.actualizar_total()
            conn.close()

        ttk.Button(popup, text="Guardar", command=guardar).pack(pady=10)

    def get_conversion_rates(self):
        """
        Intenta obtener las tasas de conversión desde exchangerate.host.
        Si falla, devuelve tasas por defecto (estimadas).
        """
        # Determinar monedas a consultar
        secundarias = getattr(self, 'monedas_secundarias', self.monedas_secundarias)
        symbols = ','.join(secundarias)
        try:
            url = f"https://api.exchangerate.host/latest?base={self.base_currency}&symbols={symbols}"
            with urllib.request.urlopen(url, timeout=5) as resp:
                data = json.load(resp)
                rates = data.get("rates", {})
                # Si falta alguna, poner valor por defecto
                for m in secundarias:
                    if m not in rates:
                        rates[m] = 0.01
                return rates
        except Exception:
            # Tasas por defecto estimadas.
            return {m: 0.01 for m in secundarias}

    def actualizar_total(self):
        try:
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            cursor.execute("SELECT total FROM dinero WHERE id=1")
            result = cursor.fetchone()
            conn.close()
            if result:
                total = float(result[0])
                self.total_var.set(f"{total:.2f}")
                # obtener tasas y actualizar variables de conversión
                rates = self.get_conversion_rates()
                secundarias = getattr(self, 'monedas_secundarias', self.monedas_secundarias)
                # Limpiar etiquetas previas
                for widget in self.winfo_children():
                    if isinstance(widget, ttk.Frame):
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Label) and "(" in child.cget("text"):
                                child.config(text="")
                # Mostrar solo las secundarias seleccionadas
                conv_frame = None
                for widget in self.winfo_children():
                    if isinstance(widget, ttk.Frame):
                        conv_frame = widget
                        break
                if conv_frame:
                    for i, m in enumerate(secundarias):
                        val = total * rates.get(m, 0.0)
                        label = f"{val:.2f} {m}"
                        # Buscar el label correspondiente
                        for child in conv_frame.winfo_children():
                            if isinstance(child, ttk.Label) and m in child.cget("text"):
                                child.config(text=label)
            else:
                self.total_var.set("0.00")
                # Limpiar etiquetas
                for widget in self.winfo_children():
                    if isinstance(widget, ttk.Frame):
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.Label) and "(" in child.cget("text"):
                                child.config(text="0.00")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo obtener el total: {e}")

    
    def modificar_total(self):
        try:
            self.autenticar()
            nuevo_total = float(self.total_var.get())
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            cursor.execute("UPDATE dinero SET total=? WHERE id=1", (nuevo_total,))
            conn.commit()
            conn.close()
            self.actualizar_total()
            messagebox.showinfo("Éxito", "Total actualizado correctamente")
        except ValueError:
            messagebox.showerror("Error", "Ingrese un valor numérico válido")
        except LoginError as e:
            messagebox.showerror("Error", "Fallo de autenticacion")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el total: {e}")

    def agregar_dinero(self):
        self._modificar_monto(+1)

    def quitar_dinero(self):
        self._modificar_monto(-1)

    def _modificar_monto(self, signo):
        def confirmar():
            try:
                self.autenticar()
                monto = float(entry.get())
                conn = sqlite3.connect(self.db)
                cursor = conn.cursor()
                cursor.execute("UPDATE dinero SET total = total + ? WHERE id=1", (signo * monto,))
                conn.commit()
                conn.close()
                self.actualizar_total()
                popup.destroy()
            except ValueError:
                messagebox.showerror("Error", "Ingrese un valor válido")
            except LoginError as e:
                messagebox.showerror("Error", "Fallo de autenticacion")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo modificar el dinero: {e}")

        popup = TopLevel(self)
        popup.title("Agregar dinero" if signo > 0 else "Quitar dinero")
        tk.Label(popup, text="Monto:").pack(padx=10, pady=5)
        entry = tk.Entry(popup)
        entry.pack(padx=10, pady=5)
        tk.Button(popup, text="Confirmar", command=confirmar).pack(padx=10, pady=10)
        entry.focus()
    
    def autenticar(self):
        connection = sqlite3.connect(self.db)
        cursor = connection.cursor()
        cursor.execute("SELECT passwd FROM configuracion WHERE id=1")
        passwd = cursor.fetchone()[0]
        connection.close()

        # Si la contraseña está vacía, no solicitamos autenticación
        if not passwd:
            return True  # Autenticación omitida, la contraseña está vacía
        
        # Si la contraseña no está vacía, proceder con la autenticación
        def confirmar():
            nonlocal autenticado

            if not entry.get():
                messagebox.showerror("Error", "Ingrese una contraseña")
            elif entry.get() != passwd:
                popup.destroy()
            else:
                autenticado = True
                popup.destroy()

        autenticado = False
        popup = TopLevel(self)
        popup.title("Autenticar")
        popup.grab_set()  # bloquea otras ventanas hasta que se cierre esta
        tk.Label(popup, text="Contraseña: ").pack(padx=10, pady=5)
        entry = tk.Entry(popup, show="*")  # oculta la contraseña
        entry.pack(padx=10, pady=5)
        tk.Button(popup, text="Confirmar", command=confirmar).pack(padx=10, pady=10)
        entry.focus()
        self.wait_window(popup)  # espera a que la ventana se cierre

        if not autenticado:
            self.actualizar_total()
            raise LoginError()
        
        return True

class LoginError(Exception):
    def __init__(self):
        super().__init__("Error de autenticacion")