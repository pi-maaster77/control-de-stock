from tkinter.ttk import Button
# from libreria import tema


BLANCO = 0
ACTUALIZAR = 1
AGREGAR = 2
EDITAR = 3
ELIMINAR = 4

ICONO = (" ", "R", "+", "E", "D")

class Boton(Button):
    def __init__(self, master=None, tipo=BLANCO, *args, **kwargs):
        super().__init__(master, *args, **kwargs, text=ICONO[tipo])

        self.tipo = tipo
