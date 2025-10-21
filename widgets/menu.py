import tkinter as tk
from tkinter import messagebox, filedialog
from libreria.configuracion import MenuConfiguracion
from libreria.estilo import Estilo
from libreria.querry import ejecutar_sql_desde_archivo

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
        if self.db == None:
            archivo.add_command(label="Configuracion", command=self.menu_configuracion, state="disabled")
        else:
            archivo.add_command(label="Configuracion", command=self.menu_configuracion)
        self.add_cascade(label="Archivo", menu=archivo)

    def menu_configuracion(self):
        # Abrir una ventana hija en lugar de crear una nueva raíz
        top = tk.Toplevel(self.master)
        estilo = Estilo(self.db)
        # aplicar estilos a la raíz principal asegura coherencia; aplicamos también al Toplevel
        try:
            Estilo(self.db).aplicar(self.master)
            estilo.aplicar(top)
        except Exception:
            pass
        MenuConfiguracion(top, self.db)


    def nuevo(self):
        archivo = filedialog.asksaveasfilename(title="Guardar", defaultextension=".db", filetypes=[("Base sqlite", "*.db")])
        if archivo:
            ejecutar_sql_desde_archivo(archivo, "stock.sql")
            from main import Main
            Main(archivo) 
        else:
            messagebox.showerror("Archivo no seleccionado")
    def abrir(self):
        archivo = filedialog.askopenfilename(title="Abrir", defaultextension=".db", filetypes=[("Base sqlite", "*.db")])
        if archivo:
            from main import Main
            Main(archivo) 