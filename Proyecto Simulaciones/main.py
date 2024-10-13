import customtkinter as ctk
import os
import subprocess

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.title("Proyecto Simulaciones")
        self.geometry("500x300")

        # Centrar la ventana en la pantalla
        self.center_window()

        # Crear un frame para contener los elementos
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Crear y colocar el Label antes de los botones
        label = ctk.CTkLabel(self.frame, text="Calculadora de Simulaciones", font=("Arial", 16, "bold"))
        label.grid(row=0, column=0, columnspan=2, pady=(0, 20), padx=10)

        # Lista de nombres de archivos
        files = ["ContinuoReaccionQuimica.py", "ContinuoReactorNuclear.py", "DiscretaPeluqueria.py", "DiscretaRestaurante.py", "DiscretaRestaurante2.py", "DiscretaSistemaRedes.py"]

        # Crear y colocar los botones
        for i, file in enumerate(files):
            button = ctk.CTkButton(self.frame, text=f"Abrir {file}", command=lambda f=file: self.open_file(f))
            button.grid(row=(i//2) + 1, column=i%2, padx=10, pady=10, sticky="ew")

        # Configurar el grid para que se expanda correctamente
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

    def center_window(self):
        # Obtener las dimensiones de la pantalla
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Obtener las dimensiones de la ventana
        window_width = 500
        window_height = 300

        # Calcular la posición x, y para centrar la ventana
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # Establecer la geometría de la ventana
        self.geometry(f'{window_width}x{window_height}+{x}+{y}')

    def open_file(self, filename):
        # Verificar si el archivo existe
        if os.path.exists(filename):
            # Abrir el archivo con el programa predeterminado
            subprocess.run(["python", filename], check=True)
        else:
            print(f"El archivo {filename} no existe.")
            
# Empezar el programa
app = App()
app.mainloop()
