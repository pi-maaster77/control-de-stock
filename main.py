import tkinter as tk
import os
import sqlite3
import querry
from tkinter import ttk
from tabs.compra import Compra
from tabs.venta_2 import Venta
from tabs.stock import Stock
from tabs.alerta import Alerta
from tabs.reportes import Reportes

root = tk.Tk()
root.title("Gestor de Stock")

if not os.path.exists("stock.db"):
    querry.ejecutar_sql_desde_archivo("stock.db", "stock.sql")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

funalerta = lambda : None

stock = Stock(notebook)
alerta = Alerta(notebook)
compra = Compra(notebook)
venta = Venta(notebook, alerta.actualizar_alerta_tab)
transacciones = Reportes(notebook)

def on_tab_change(event):
    stock.actualizar_stock_tab()
    alerta.actualizar_alerta_tab()
    transacciones.actualizar()
    #venta_resultado.config(text="")

notebook.bind("<<NotebookTabChanged>>", on_tab_change)


root.mainloop()