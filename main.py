import tkinter as tk
import os
import sqlite3
import libreria.querry as querry
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
from libreria.config import db

root = tk.Tk()
root.title("Gestor de Stock")

root.config(menu=Menu(root))

if not os.path.exists(db):
    querry.ejecutar_sql_desde_archivo(db, "stock.sql")

db = "base.db"

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

caja = Caja(notebook)
stock = Stock(notebook)
alerta = Alerta(notebook)
compra = Compra(notebook)
venta = Venta(notebook, alerta.actualizar_alerta_tab)
vencimientos = Vencimientos(notebook)

Estilo().aplicar(root)

transacciones = Reportes(notebook)

def on_tab_change(event):
    stock.actualizar_stock_tab()
    alerta.actualizar_alerta_tab()
    transacciones.actualizar()
    caja.actualizar_total()
    vencimientos.actualizar()

notebook.bind("<<NotebookTabChanged>>", on_tab_change)


root.mainloop()