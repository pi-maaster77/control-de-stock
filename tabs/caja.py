import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


class Caja(ttk.Frame):
    def __init__(self, notebook):
        super().__init__(notebook)
        self.frame = self
        self.total_var = tk.StringVar()
        self.setup_ui()
        self.actualizar_total()
        notebook.add(self.frame, text="Caja")

    def setup_ui(self):
        ttk.Label(self, text="Total en caja:", font=("Arial", 14)).pack(pady=10)
        self.total_entry = ttk.Entry(self, textvariable=self.total_var, font=("Arial", 14), justify="center", width=20)
        self.total_entry.pack(pady=5)

        botones_frame = ttk.Frame(self)
        botones_frame.pack(pady=10)

        ttk.Button(botones_frame, text="Actualizar", command=self.actualizar_total).grid(row=0, column=0, padx=5)
        ttk.Button(botones_frame, text="Modificar", command=self.modificar_total).grid(row=0, column=1, padx=5)
        ttk.Button(botones_frame, text="+ Agregar", command=self.agregar_dinero).grid(row=0, column=2, padx=5)
        ttk.Button(botones_frame, text="- Quitar", command=self.quitar_dinero).grid(row=0, column=3, padx=5)

    def actualizar_total(self):
        try:
            conn = sqlite3.connect("stock.db")
            cursor = conn.cursor()
            cursor.execute("SELECT total FROM dinero WHERE id=1")
            result = cursor.fetchone()
            conn.close()
            if result:
                self.total_var.set(f"{result[0]:.2f}")
            else:
                self.total_var.set("0.00")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo obtener el total: {e}")

    def modificar_total(self):
        try:
            nuevo_total = float(self.total_var.get())
            conn = sqlite3.connect("stock.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE dinero SET total=? WHERE id=1", (nuevo_total,))
            conn.commit()
            conn.close()
            self.actualizar_total()
            messagebox.showinfo("Éxito", "Total actualizado correctamente")
        except ValueError:
            messagebox.showerror("Error", "Ingrese un valor numérico válido")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el total: {e}")

    def agregar_dinero(self):
        self._modificar_monto(+1)

    def quitar_dinero(self):
        self._modificar_monto(-1)

    def _modificar_monto(self, signo):
        def confirmar():
            try:
                monto = float(entry.get())
                conn = sqlite3.connect("stock.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE dinero SET total = total + ? WHERE id=1", (signo * monto,))
                conn.commit()
                conn.close()
                self.actualizar_total()
                popup.destroy()
            except ValueError:
                messagebox.showerror("Error", "Ingrese un valor válido")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo modificar el dinero: {e}")

        popup = tk.Toplevel(self)
        popup.title("Agregar dinero" if signo > 0 else "Quitar dinero")
        ttk.Label(popup, text="Monto:").pack(padx=10, pady=5)
        entry = ttk.Entry(popup)
        entry.pack(padx=10, pady=5)
        ttk.Button(popup, text="Confirmar", command=confirmar).pack(padx=10, pady=10)
        entry.focus()
