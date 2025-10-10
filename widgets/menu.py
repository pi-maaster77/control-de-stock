import tkinter as tk
from tkinter import messagebox
from libreria.confiuguracion import MenuConfiguracion, Estilo

class Menu(tk.Menu):
    def __init__(self, root):
        super().__init__(root)
        self.setup()
    
    def setup(self):
        archivo = tk.Menu(self, tearoff=0)
        archivo.add_command(label="Nuevo...")
        archivo.add_command(label="Abrir...")
        archivo.add_separator()
        archivo.add_command(label="Configuracion", command=self.menu_configuracion)
        self.add_cascade(label="Archivo", menu=archivo)

    def menu_configuracion(self):
        root = tk.Tk()
        estilo = Estilo()
        estilo.aplicar(root)  # ✅ APLICAR los estilos cargados al inicio
        MenuConfiguracion(root)
        root.mainloop()