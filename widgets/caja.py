import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import urllib.request
import json

class Caja(ttk.Frame):
    def __init__(self, notebook, db):
        super().__init__(notebook)
        self.db = db
        self.frame = self
        self.total_var = tk.StringVar()
        self.eur_var = tk.StringVar()
        self.usd_var = tk.StringVar()
        # Moneda base // se puede cambiar la moneda de la caja // e.g. 'USD', 'EUR', 'ARS')
        self.base_currency = "ARS"
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
        ttk.Label(conv_frame, text="Euros (EUR):").grid(row=0, column=0, sticky="e", padx=5)
        ttk.Label(conv_frame, textvariable=self.eur_var).grid(row=0, column=1, sticky="w", padx=5)
        ttk.Label(conv_frame, text="Dólares (USD):").grid(row=1, column=0, sticky="e", padx=5)
        ttk.Label(conv_frame, textvariable=self.usd_var).grid(row=1, column=1, sticky="w", padx=5)

        botones_frame = ttk.Frame(self)
        botones_frame.pack(pady=10)

        ttk.Button(botones_frame, text="Actualizar", command=self.actualizar_total).grid(row=0, column=0, padx=5)
        ttk.Button(botones_frame, text="Modificar", command=self.modificar_total).grid(row=0, column=1, padx=5)
        ttk.Button(botones_frame, text="+ Agregar", command=self.agregar_dinero).grid(row=0, column=2, padx=5)
        ttk.Button(botones_frame, text="- Quitar", command=self.quitar_dinero).grid(row=0, column=3, padx=5)

    def get_conversion_rates(self):
        """
        Intenta obtener las tasas de conversión desde exchangerate.host.
        Si falla, devuelve tasas por defecto (estimadas).
        """
        try:
            url = f"https://api.exchangerate.host/latest?base={self.base_currency}&symbols=EUR,USD"
            with urllib.request.urlopen(url, timeout=5) as resp:
                data = json.load(resp)
                rates = data.get("rates", {})
                eur = rates.get("EUR")
                usd = rates.get("USD")
                if eur is None or usd is None:
                    raise ValueError("Tasas incompletas")
                return {"EUR": eur, "USD": usd}
        except Exception:
            # Tasas por defecto estimadas.
            # Cambia estos valores según cuanto este la moneda base real.
            return {"EUR": 0.005, "USD": 0.006}

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
                eur_val = total * rates["EUR"]
                usd_val = total * rates["USD"]
                self.eur_var.set(f"{eur_val:.2f} EUR")
                self.usd_var.set(f"{usd_val:.2f} USD")
            else:
                self.total_var.set("0.00")
                self.eur_var.set("0.00 EUR")
                self.usd_var.set("0.00 USD")
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

        popup = tk.Toplevel(self)
        popup.title("Agregar dinero" if signo > 0 else "Quitar dinero")
        tk.Label(popup, text="Monto:").pack(padx=10, pady=5)
        entry = tk.Entry(popup)
        entry.pack(padx=10, pady=5)
        tk.Button(popup, text="Confirmar", command=confirmar).pack(padx=10, pady=10)
        entry.focus()
    
    def autenticar(self):
        def confirmar():
            nonlocal autenticado

            connection = sqlite3.connect(self.db)
            cursor = connection.cursor()
            cursor.execute("SELECT passwd FROM configuracion WHERE id=1")
            passwd = cursor.fetchone()[0]
            print(passwd)
            connection.close()

            if not entry.get():
                messagebox.showerror("Error", "Ingrese una contraseña")
            elif entry.get() != passwd:
                popup.destroy()
            else:
                autenticado = True
                popup.destroy()

        autenticado = False
        popup = tk.Toplevel(self)
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