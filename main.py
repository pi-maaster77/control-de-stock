import tkinter as tk
from tkinter import ttk
from widgets.compra import Compra
from widgets.venta import Venta
from widgets.stock import Stock
from widgets.alerta import Alerta
from widgets.reportes import Reportes
from widgets.caja import Caja
from libreria.confiuguracion import Estilo
from widgets.vencimientos import Vencimientos
from widgets.menu import Menu

class Main(tk.Tk):
    def __init__(self, db=None):
        super().__init__()
        self.db = db
        self.config(menu=Menu(self, db))
        if db == None:
            pass
        else:
            self.iniciar_interfaz()
        self.title("Gestor de Stock")
        self.mainloop()

    def iniciar_interfaz(self):
        # Aplicar estilos antes de crear widgets para que ttk los herede correctamente
        try:
            Estilo(self.db).aplicar(self)
        except Exception:
            pass

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.caja = Caja(self.notebook, self.db)
        self.stock = Stock(self.notebook, self.db)
        self.alerta = Alerta(self.notebook, self.db)
        self.compra = Compra(self.notebook, self.db)
        self.venta = Venta(self.notebook, self.alerta.actualizar_alerta_tab, self.db)
        self.vencimientos = Vencimientos(self.notebook, self.db)
        self.transacciones = Reportes(self.notebook, self.db)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        self.stock.actualizar_stock_tab()
        self.alerta.actualizar_alerta_tab()
        self.transacciones.actualizar()
        self.caja.actualizar_total()
        self.vencimientos.actualizar()
         
if __name__ == "__main__":
    Main()
