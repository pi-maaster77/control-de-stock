from ttkbootstrap import Button
import tkinter as tk

# Definición de constantes
BLANCO = 0
ACTUALIZAR = 1
AGREGAR = 2
EDITAR = 3
ELIMINAR = 4

# Definición de iconos
ICONO = (" ", "R", "+", "E", "D")

# Definición de leyendas para cada tipo de botón
LEYENDAS = {
    BLANCO: "Limpiar",
    ACTUALIZAR: "Actualizar",
    AGREGAR: "Agregar",
    EDITAR: "Editar",
    ELIMINAR: "Eliminar"
}

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None

        # Bind eventos al widget para mostrar y ocultar el tooltip
        self.widget.bind("<Enter>", self.show_tooltip)  # Cuando el mouse entra
        self.widget.bind("<Leave>", self.hide_tooltip)  # Cuando el mouse sale

    def show_tooltip(self, event):
        # Crear un Label para mostrar el texto del tooltip
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.overrideredirect(True)  # Ocultar bordes de la ventana emergente
        self.tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")  # Posición del tooltip

        label = tk.Label(self.tooltip, text=self.text, background="yellow", relief="solid", padx=5, pady=2)
        label.pack()

    def hide_tooltip(self, event):
        # Cerrar el tooltip cuando el mouse sale
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class Boton(Button):
    TIPO_STYLE = {
        BLANCO: "secondary.TButton",
        ACTUALIZAR: "info.TButton",
        AGREGAR: "success.TButton",
        EDITAR: "warning.TButton",
        ELIMINAR: "danger.TButton",
    }

    def __init__(self, master=None, tipo=BLANCO, *args, **kwargs):
        # Establecer el estilo según el tipo
        style = self.TIPO_STYLE.get(tipo, "secondary.TButton")
        super().__init__(master, *args, **kwargs, text=ICONO[tipo], style=style)
        
        # Guardar el tipo y texto del botón
        self.tipo = tipo
        self.tooltip_text = LEYENDAS.get(tipo, "Botón")

        # Crear el tooltip para mostrar la leyenda
        Tooltip(self, self.tooltip_text)

