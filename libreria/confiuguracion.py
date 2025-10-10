import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from tkinter.colorchooser import askcolor
import sqlite3
from libreria.config import db

class Estilo:
    def __init__(self, archivo=db):
        self.archivo = archivo

        # Valores por defecto
        self.fg = "#000000"
        self.bg = "#FFFFFF"
        self.font = ("Arial", 12)

        self.cargar()

    def cargar(self):
        """Carga la configuración del estilo desde la base de datos."""
        try:
            conn = sqlite3.connect(self.archivo)
            cursor = conn.cursor()
            cursor.execute("SELECT fg, bg, font_name, font_size FROM configuracion WHERE id = 1")
            row = cursor.fetchone()
            conn.close()

            if row:
                self.fg = row[0] or self.fg
                self.bg = row[1] or self.bg
                font_name = row[2] or self.font[0]
                font_size = row[3] if row[3] is not None else self.font[1]
                self.font = (font_name, font_size)
        except Exception as e:
            print(f"Error al cargar estilo: {e}")

    def guardar(self):
        """Guarda la configuración del estilo en la base de datos."""
        try:
            conn = sqlite3.connect(self.archivo)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO configuracion (id, fg, bg, font_name, font_size)
                VALUES (1, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    fg = excluded.fg,
                    bg = excluded.bg,
                    font_name = excluded.font_name,
                    font_size = excluded.font_size
            """, (self.fg, self.bg, self.font[0], self.font[1]))
            conn.commit()
            conn.close()
            print("Configuración guardada exitosamente")
        except Exception as e:
            print(f"Error al guardar el estilo: {e}")

    def aplicar(self, widget):
        """Aplica los colores y fuente al widget y sus hijos."""
        opciones = widget.configure()

        # --- Widgets estándar de Tkinter ---
        if "fg" in opciones:
            try:
                widget.config(fg=self.fg)
            except Exception:
                pass
        if "bg" in opciones:
            try:
                widget.config(bg=self.bg)
            except Exception:
                pass
        if "font" in opciones:
            try:
                widget.config(font=self.font)
            except Exception:
                pass

        # --- Widgets ttk ---
        if isinstance(widget, ttk.Widget):
            self.aplicar_estilo_global()

        # --- Aplicar a los hijos ---
        for hijo in widget.winfo_children():
            self.aplicar(hijo)

    def aplicar_estilo_global(self):
        """Define estilos globales para ttk (con borde visible y hover punteado)."""
        style = ttk.Style()
        style.theme_use("clam")

        # === Estilos base ===
        style.configure(
            ".", 
            background=self.bg, 
            foreground=self.fg, 
            font=self.font
        )

        # Estilos comunes
        style.configure("TLabel", background=self.bg, foreground=self.fg, font=self.font)
        style.configure("TEntry", fieldbackground=self.bg, foreground=self.fg, font=self.font)
        style.configure("TNotebook", background=self.bg, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.bg, foreground=self.fg, font=self.font)
        style.configure("Treeview", background=self.bg, foreground=self.fg,
                        fieldbackground=self.bg, font=self.font)
        style.configure("Treeview.Heading", background=self.bg, foreground=self.fg, font=self.font)

        # === Botones con borde ===
        # Borde normal visible
        style.configure(
            "TButton",
            background=self.bg,
            foreground=self.fg,
            font=self.font,
            bordercolor=self.fg,
            borderwidth=2,
            relief="solid",
            focusthickness=1,
            focuscolor=self.fg
        )

        # === Mapas dinámicos (reacciones a estados) ===
        # Sin cambios de color, pero con borde punteado al pasar el mouse
        style.map(
            "TButton",
            background=[("active", self.bg), ("pressed", self.bg), ("disabled", self.bg)],
            foreground=[("active", self.fg), ("pressed", self.fg), ("disabled", self.fg)],
            relief=[("pressed", "ridge"), ("active", "groove"), ("!active", "solid")],
            bordercolor=[("active", self.fg), ("disabled", self.fg)],
        )

        # === Otros elementos (mantienen coherencia visual) ===
        style.map("TNotebook.Tab",
                  background=[("selected", self.bg), ("active", self.bg)],
                  foreground=[("selected", self.fg), ("active", self.fg)])
        style.map("TEntry",
                  fieldbackground=[("disabled", self.bg)],
                  foreground=[("disabled", self.fg)])
    def aplicar_a_todas_las_ventanas(self):
        """Aplica el estilo a todas las ventanas (Tk y Toplevel)."""
        root = tk._default_root
        if root:
            for ventana in root.winfo_children():
                if isinstance(ventana, (tk.Toplevel, tk.Tk)):
                    self.aplicar(ventana)

class MenuConfiguracion:
    def __init__(self, root):
        self.root = root
        self.estilo = Estilo()
        

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


# Crear ventana principal

if __name__ == "__main__":
    root = tk.Tk()
    estilo = Estilo()
    estilo.aplicar(root)  # ✅ APLICAR los estilos cargados al inicio
    MenuConfiguracion(root)
    root.mainloop()
