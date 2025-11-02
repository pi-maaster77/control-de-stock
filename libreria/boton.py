
from ttkbootstrap import Button


BLANCO = 0
ACTUALIZAR = 1
AGREGAR = 2
EDITAR = 3
ELIMINAR = 4

ICONO = (" ", "R", "+", "E", "D")

class Boton(Button):
    TIPO_STYLE = {
        BLANCO: "secondary.TButton",
        ACTUALIZAR: "info.TButton",
        AGREGAR: "success.TButton",
        EDITAR: "warning.TButton",
        ELIMINAR: "danger.TButton",
    }

    def __init__(self, master=None, tipo=BLANCO, *args, **kwargs):
        style = self.TIPO_STYLE.get(tipo, "secondary.TButton")
        super().__init__(master, *args, **kwargs, text=ICONO[tipo], style=style)
        self.tipo = tipo
