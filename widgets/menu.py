import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
# from libreria.estilo import Estilo
from libreria.querry import ejecutar_sql_desde_archivo
from libreria.toplevel import TopLevel
import sqlite3

class Menu(tk.Menu):
    def __init__(self, root, db):
        super().__init__(root)
        self.db = db
        self.setup()
    
    def setup(self):
        archivo = tk.Menu(self, tearoff=0)
        archivo.add_command(label="Nuevo...", command=self.nuevo)
        archivo.add_command(label="Abrir...", command=self.abrir)

        archivo.add_separator()

        archivo.add_command(label="Modo Claro", command=lambda : self.master.cambiar_tema("flatly"))
        archivo.add_command(label="Modo Oscuro", command=lambda : self.master.cambiar_tema("darkly"))    

        archivo.add_separator()

        archivo.add_command(label="Cambiar la contraseña", command=self.canmbiar_contraseña)

        self.add_cascade(label="Archivo", menu=archivo)

    def canmbiar_contraseña(self):
        def cambiar_contraseña_accion():
            connection = sqlite3.connect(self.db)
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT passwd FROM configuracion WHERE id=1")
                passwd = cursor.fetchone()[0]
                if actual_entry.get() != passwd:
                    messagebox.showerror("Error", "Contraseña actual incorrecta")
                    cambiar_window.destroy()
                    return
                if nueva_entry.get() != nueva_entry_2.get():
                    messagebox.showerror("Error", "Las nuevas contraseñas no coinciden")
                    cambiar_window.destroy()
                    return
                cursor.execute("UPDATE configuracion SET passwd = ? WHERE id=1", (nueva_entry.get(),))
                connection.commit()
                messagebox.showinfo("Éxito", "Contraseña cambiada exitosamente")
                cambiar_window.destroy()
            finally:
                connection.close()

        cambiar_window = TopLevel(self.master)
        cambiar_window.title("Cambiar Contraseña")

        ttk.Label(cambiar_window, text="Contraseña Actual:").grid(row=0, column=0, padx=10, pady=10)
        actual_entry = ttk.Entry(cambiar_window, show="*")
        actual_entry.grid(row=0, column=1, padx=10, pady=10)
        ttk.Label(cambiar_window, text="Nueva Contraseña:").grid(row=1, column=0, padx=10, pady=10)
        nueva_entry = ttk.Entry(cambiar_window, show="*")
        nueva_entry.grid(row=1, column=1, padx=10, pady=10)
        ttk.Label(cambiar_window, text="Confirmar Contraseña:").grid(row=2, column=0, padx=10, pady=10)
        nueva_entry_2 = ttk.Entry(cambiar_window, show="*")
        nueva_entry_2.grid(row=2, column=1, padx=10, pady=10)

        ttk.Button(cambiar_window, text="Cambiar Contraseña", command=cambiar_contraseña_accion).grid(row=3, column=0, columnspan=2, pady=10)
  
    def nuevo(self):
        archivo = filedialog.asksaveasfilename(title="Guardar", defaultextension=".db", filetypes=[("Base sqlite", "*.db")])
        if archivo:
            ejecutar_sql_desde_archivo(archivo, "stock.sql")
            with open("last.txt", "w") as f:
                f.write(archivo)
            # Reiniciar la aplicación
            root = self.master
            root.destroy()
            import sys
            import os
            # Detectar si estamos ejecutando como script o como ejecutable
            if getattr(sys, 'frozen', False):
                # Estamos en un ejecutable
                program = sys.executable
                args = [program, "--no-menu"]
            else:
                # Estamos en modo desarrollo
                program = sys.executable
                args = [program, "-m", "main", "--no-menu"]
            os.execv(program, args)
        else:
            messagebox.showerror("Archivo no seleccionado")

    def abrir(self):
        archivo = filedialog.askopenfilename(title="Abrir", defaultextension=".db", filetypes=[("Base sqlite", "*.db")])
        if archivo:
            with open("last.txt", "w") as f:
                f.write(archivo)
            # Reiniciar la aplicación
            root = self.master
            root.destroy()
            import sys
            import os
            # Detectar si estamos ejecutando como script o como ejecutable
            if getattr(sys, 'frozen', False):
                # Estamos en un ejecutable
                program = sys.executable
                args = [program, "--no-menu"]
            else:
                # Estamos en modo desarrollo
                program = sys.executable
                args = [program, "-m", "main", "--no-menu"]
            os.execv(program, args)