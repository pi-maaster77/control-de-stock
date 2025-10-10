import tkinter as tk
from tkinter import messagebox

# Funciones para los comandos
def nuevo_archivo():
    text_area.delete(1.0, tk.END)

def abrir_archivo():
    messagebox.showinfo("Abrir", "Aquí se abriría un archivo.")

def guardar_archivo():
    messagebox.showinfo("Guardar", "Aquí se guardaría el archivo.")

def salir():
    root.quit()

def copiar():
    text_area.event_generate("<<Copy>>")

def pegar():
    text_area.event_generate("<<Paste>>")

def cortar():
    text_area.event_generate("<<Cut>>")

def acerca_de():
    messagebox.showinfo("Acerca de", "Ejemplo de Bloc de Notas en Tkinter")

# Crear la ventana principal
root = tk.Tk()
root.title("Bloc de Notas")
root.geometry("600x400")

# Crear el área de texto
text_area = tk.Text(root, wrap="word")
text_area.pack(expand=1, fill="both")

# Crear la barra de menú
barra_menu = tk.Menu(root)
root.config(menu=barra_menu)

# Menú Archivo
menu_archivo = tk.Menu(barra_menu, tearoff=0)
menu_archivo.add_command(label="Nuevo", command=nuevo_archivo)
menu_archivo.add_command(label="Abrir...", command=abrir_archivo)
menu_archivo.add_command(label="Guardar", command=guardar_archivo)
menu_archivo.add_separator()
menu_archivo.add_command(label="Salir", command=salir)
barra_menu.add_cascade(label="Archivo", menu=menu_archivo)

# Menú Edición
menu_editar = tk.Menu(barra_menu, tearoff=0)
menu_editar.add_command(label="Cortar", command=cortar)
menu_editar.add_command(label="Copiar", command=copiar)
menu_editar.add_command(label="Pegar", command=pegar)
barra_menu.add_cascade(label="Edición", menu=menu_editar)

# Menú Ayuda
menu_ayuda = tk.Menu(barra_menu, tearoff=0)
menu_ayuda.add_command(label="Acerca de", command=acerca_de)
barra_menu.add_cascade(label="Ayuda", menu=menu_ayuda)

# Ejecutar el bucle principal
root.mainloop()
