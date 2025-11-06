import ttkbootstrap as tb # pip install ttkbootstrap. Funciona como tkinter pero con temas modernos
from widgets.compra import Compra
from widgets.venta import Venta
from widgets.stock import Stock
from widgets.alerta import Alerta
from widgets.reportes import Reportes
from widgets.caja import Caja
from widgets.vencimientos import Vencimientos
from widgets.menu import Menu


import sys

class Main(tb.Window):
    def __init__(self, db=None):
        super().__init__(themename="darkly")  # Tema por defecto
        self.db = db
        self.show_menu = "--no-menu" not in sys.argv
        self.config(menu=Menu(self, self.db))

        if self.db is None:
            try:
                with open("last.txt", "r") as f:
                    self.db = f.read().strip()
                self.iniciar_interfaz()
            except Exception as e:
                print("E24: Error reading last.txt -", e)
        else:
            self.iniciar_interfaz()

        # Configurar el menú solo si no se especificó --no-menu

        self.title("Gestor de Stock")
        self.mainloop()

    def cambiar_tema(self, tema):
        self.style.theme_use(tema)

    def iniciar_interfaz(self):
        # from libreria.estilo import Estilo
        # Crear y aplicar estilos usando nuestra clase Estilo
        """
        try:
            estilo = Estilo(self.db)
            estilo.aplicar(self)
        except Exception as e:
            print("ERROR al aplicar estilo:", e)
        """
        self.notebook = tb.Notebook(self)
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
