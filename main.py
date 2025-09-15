import tkinter as tk
import os
import sqlite3
import libreria.querry as querry
from tkinter import ttk
from tabs.compra import Compra
from tabs.venta import Venta
from tabs.stock import Stock
from tabs.alerta import Alerta
from tabs.reportes import Reportes
from tabs.caja import Caja
from confiuguracion import Estilo
from libreria.config import db

root = tk.Tk()
root.title("Gestor de Stock")

if not os.path.exists(db):
    querry.ejecutar_sql_desde_archivo(db, "stock.sql")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

caja = Caja(notebook)
stock = Stock(notebook)
alerta = Alerta(notebook)
compra = Compra(notebook)
venta = Venta(notebook, alerta.actualizar_alerta_tab)

# Estilo().aplicar(root)

transacciones = Reportes(notebook)

def on_tab_change(event):
    stock.actualizar_stock_tab()
    alerta.actualizar_alerta_tab()
    transacciones.actualizar()
    caja.actualizar_total()

notebook.bind("<<NotebookTabChanged>>", on_tab_change)


root.mainloop()