import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from tkinter.colorchooser import askcolor
from libreria.estilo import Estilo
import sqlite3

class MenuConfiguracion:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.estilo = Estilo(self.db)
        

        self.root.title("Configuración")
        # Fuentes disponibles
        self.fuentes = sorted(list(tkfont.families()))

        # Variables
        self.fuente_var = tk.StringVar(value=self.fuentes[0])
        self.tamano_var = tk.StringVar(value="12")
        self.color_fuente = "#000000"
        self.color_fondo = "#FFFFFF"

        # === Sección: Fuente y Tamaño ===
        fuente_frame = tk.LabelFrame(self.root, text="Fuente", bg="#e6e6e6", padx=10, pady=10)
        fuente_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(fuente_frame, text="Tipo de fuente:", bg="#e6e6e6").pack(anchor="w")
        self.fuente_listbox = tk.Listbox(fuente_frame, height=5)
        for f in self.fuentes:
            self.fuente_listbox.insert(tk.END, f)
        self.fuente_listbox.selection_set(0)
        self.fuente_listbox.pack(fill="x", pady=5)
        self.fuente_listbox.bind("<<ListboxSelect>>", self.actualizar_estilo)

        tk.Label(fuente_frame, text="Tamaño:", bg="#e6e6e6").pack(anchor="w")
        self.tamano_spin = tk.Spinbox(fuente_frame, from_=8, to=48, increment=2, textvariable=self.tamano_var, command=self.actualizar_estilo)
        self.tamano_spin.pack(fill="x", pady=5)

        # === Sección: Colores ===
        color_frame = tk.LabelFrame(self.root, text="Colores", bg="#e6e6e6", padx=10, pady=10)
        color_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(color_frame, text="Color de fuente", command=self.seleccionar_color_fuente).pack(fill="x", pady=5)
        tk.Button(color_frame, text="Color de fondo", command=self.seleccionar_color_fondo).pack(fill="x", pady=5)

        # === Vista previa ===
        preview_frame = tk.LabelFrame(self.root, text="Vista previa", bg="#e6e6e6", padx=10, pady=10)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.etiqueta = tk.Label(preview_frame, text="Texto de ejemplo",
                                font=(self.fuentes[0], 12),
                                fg=self.color_fuente, bg=self.color_fondo,
                                relief="solid", width=30, height=4)
        self.etiqueta.pack(expand=True, pady=10)

        # === Botón aplicar ===
        tk.Button(self.root, text="Aplicar configuración", bg="#d9d9d9", command=self.aplicar).pack(pady=10)

        self.estilo.aplicar(self.root)  # Aplicar estilos cargados
        self.actualizar_estilo()
        


    def actualizar_estilo(self, event=None):
        try:
            fuente = self.fuente_listbox.get(self.fuente_listbox.curselection())
        except tk.TclError:
            fuente = self.fuentes[0]
        tamano = int(self.tamano_var.get())
        self.etiqueta.config(font=(fuente, tamano), fg=self.color_fuente, bg=self.color_fondo)

    def seleccionar_color_fuente(self):
        color = askcolor(initialcolor=self.color_fuente, title="Seleccionar color de fuente")[1]
        if color:
            self.color_fuente = color
            self.actualizar_estilo()

    def seleccionar_color_fondo(self):
        color = askcolor(initialcolor=self.color_fondo, title="Seleccionar color de fondo")[1]
        if color:
            self.color_fondo = color
            self.actualizar_estilo()

    def aplicar(self):
        try:
            fuente = self.fuente_listbox.get(self.fuente_listbox.curselection())
        except tk.TclError:
            fuente = self.fuentes[0]
        tamano = int(self.tamano_var.get())

        self.estilo.fg = self.color_fuente
        self.estilo.bg = self.color_fondo
        self.estilo.font = (fuente, tamano)

        self.estilo.aplicar(self.root)
        self.estilo.guardar()
