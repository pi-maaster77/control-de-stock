import tkinter as tk
from tkinter import messagebox, filedialog
# from libreria.estilo import Estilo
from libreria.querry import ejecutar_sql_desde_archivo

class Menu(tk.Menu):
    def __init__(self, root, db):
        super().__init__(root)
        self.db = db
        self.setup()
    
    def setup(self):
        top = tk.Toplevel(self.master)
        archivo = tk.Menu(self, tearoff=0)
        archivo.add_command(label="Nuevo...", command=self.nuevo)
        archivo.add_command(label="Abrir...", command=self.abrir)

        archivo.add_separator()

        archivo.add_command(label="Modo Claro", command=lambda : top.master.cambiar_tema("flatly"))
        archivo.add_command(label="Modo Oscuro", command=lambda : top.master.cambiar_tema("darkly"))    

        self.add_cascade(label="Archivo", menu=archivo)




    def nuevo(self):
        archivo = filedialog.asksaveasfilename(title="Guardar", defaultextension=".db", filetypes=[("Base sqlite", "*.db")])
        if archivo:
            ejecutar_sql_desde_archivo(archivo, "stock.sql")
            from main import Main
            Main(archivo) 
            with open("last.txt", "w") as f:
                f.write(archivo)
        else:
            messagebox.showerror("Archivo no seleccionado")
    def abrir(self):
        archivo = filedialog.askopenfilename(title="Abrir", defaultextension=".db", filetypes=[("Base sqlite", "*.db")])
        if archivo:
            from main import Main
            Main(archivo)
            with open("last.txt", "w") as f:
                f.write(archivo)