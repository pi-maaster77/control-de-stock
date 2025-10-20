import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
from tkinter.colorchooser import askcolor
import sqlite3

class Estilo:
    def __init__(self, db):
        self.db = db
        # Valores por defecto (evitan errores si la BD está vacía o falta)
        self.fg = "#000000"
        self.bg = "#FFFFFF"
        # tomar una fuente por defecto razonable
        self.font = ("TkDefaultFont", 10)
        # marca para evitar reconfigurar repetidamente dentro de la misma llamada
        self._ultima_aplicacion_id = None
        self.cargar()

    def cargar(self):
        """Carga la configuración del estilo desde la base de datos."""
        try:
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()
            cursor.execute("SELECT fg, bg, font_name, font_size FROM configuracion WHERE id = 1")
            row = cursor.fetchone()
            conn.close()

            if row:
                # Solo actualizar si hay valores válidos en la BD
                if row[0]:
                    self.fg = row[0]
                if row[1]:
                    self.bg = row[1]
                if row[2]:
                    font_name = row[2]
                else:
                    font_name = self.font[0]
                font_size = row[3] if row[3] is not None else self.font[1]
                self.font = (font_name, font_size)
        except Exception as e:
            # No interrumpir la ejecución: mantener valores por defecto
            print(f"Error al cargar estilo: {e}")

    def guardar(self):
        """Guarda la configuración del estilo en la base de datos."""
        try:
            conn = sqlite3.connect(self.db)
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
        # Aplicar estilos globales de ttk (una sola vez por ejecución de aplicar)
        try:
            # crear un id simple para evitar reentrada infinita si se llama recursivamente
            current_id = id(widget)
            if self._ultima_aplicacion_id != current_id:
                self.aplicar_estilo_global()
                self._ultima_aplicacion_id = current_id
        except Exception:
            # no bloquear si algo falla aquí
            pass

        # --- Aplicar a widgets "clásicos" de Tkinter mediante configure() ---
        try:
            opciones = widget.configure()
        except Exception:
            opciones = {}

        if isinstance(opciones, dict):
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

        # No intentar forzar propiedades en widgets ttk; el estilo global los maneja.

        # --- Aplicar recursivamente a los hijos ---
        for hijo in widget.winfo_children():
            # evitar reaplicar estilo global en cada nodo, la función anterior ya lo hizo
            self.aplicar(hijo)

    def aplicar_estilo_global(self):
        """Define estilos globales para ttk (con borde visible y hover punteado)."""
        try:
            style = ttk.Style()
        except Exception as e:
            print(f"No se pudo crear ttk.Style(): {e}")
            return

        # Seleccionar un tema disponible (clam suele existir). Si no, usar el primero.
        try:
            temas = style.theme_names()
            if "clam" in temas:
                style.theme_use("clam")
            else:
                style.theme_use(temas[0])
        except Exception as e:
            print(f"No se pudo establecer el tema ttk: {e}")

        # Estilos comunes
        # Etiquetas, entradas y notebooks
        style.configure("TLabel", background=self.bg, foreground=self.fg, font=self.font)
        # para entradas usar fieldbackground para el fondo y foreground para el texto
        try:
            style.configure("TEntry", fieldbackground=self.bg, foreground=self.fg, font=self.font)
        except Exception:
            # algunos temas o versiones pueden requerir otras opciones; ignorar si falla
            pass
        style.configure("TNotebook", background=self.bg, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.bg, foreground=self.fg, font=self.font)
        try:
            style.configure("Treeview", background=self.bg, foreground=self.fg,
                            fieldbackground=self.bg, font=self.font)
            style.configure("Treeview.Heading", background=self.bg, foreground=self.fg, font=self.font)
        except Exception:
            pass

        # === Botones con borde ===
        # Borde normal visible
        # Botones: no todos los temas admiten bordercolor/focuscolor; usar opciones comunes
        try:
            style.configure(
                "TButton",
                background=self.bg,
                foreground=self.fg,
                font=self.font,
                borderwidth=1,
                relief="raised",
            )
        except Exception:
            pass

        # === Mapas dinámicos (reacciones a estados) ===
        # Sin cambios de color, pero con borde punteado al pasar el mouse
        try:
            style.map(
                "TButton",
                background=[("active", self.bg), ("pressed", self.bg), ("disabled", self.bg)],
                foreground=[("active", self.fg), ("pressed", self.fg), ("disabled", self.fg)],
                relief=[("pressed", "sunken"), ("active", "raised")],
            )
        except Exception:
            pass

        # === Otros elementos (mantienen coherencia visual) ===
        try:
            style.map("TNotebook.Tab",
                      background=[("selected", self.bg), ("active", self.bg)],
                      foreground=[("selected", self.fg), ("active", self.fg)])
        except Exception:
            pass

        try:
            style.map("TEntry",
                      fieldbackground=[("disabled", self.bg)],
                      foreground=[("disabled", self.fg)])
        except Exception:
            pass
    def aplicar_a_todas_las_ventanas(self):
        """Aplica el estilo a todas las ventanas (Tk y Toplevel)."""
        root = tk._default_root
        if root:
            for ventana in root.winfo_children():
                if isinstance(ventana, (tk.Toplevel, tk.Tk)):
                    self.aplicar(ventana)

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
