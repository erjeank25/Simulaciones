import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
import customtkinter as ctk

class SimulacionTermica:
    def __init__(self, Q_gen, k, T_cool, C, T0):
        self.Q_gen = Q_gen
        self.k = k
        self.T_cool = T_cool
        self.C = C
        self.T0 = T0

    def modelo(self, T, t):
        return (self.Q_gen / self.C) - self.k * (T - self.T_cool)

    def simular(self, tiempo):
        solucion = odeint(self.modelo, self.T0, tiempo)
        return tiempo, solucion

    def graficar(self, tiempo, solucion):
        plt.figure(figsize=(10, 5))
        plt.plot(tiempo, solucion, label='Temperatura del Reactor')
        plt.xlabel('Tiempo (minutos)')
        plt.ylabel('Temperatura (°C)')
        plt.title('Enfriamiento del Reactor Nuclear')
        plt.axhline(self.T_cool, color='red', linestyle='--', label='Temperatura del Sistema de Enfriamiento')
        plt.grid(True)
        plt.legend()
        plt.show()

class InterfazSimulacionTermica(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Simulación Térmica")
        self.geometry("700x400")
        self.minsize(700, 400)
        self.center_window()

        # Frame principal
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Layout de grilla con dos columnas
        self.frame.grid_columnconfigure((0, 1), weight=1)
        self.frame.grid_rowconfigure(4, weight=1)

        # Campos de entrada
        self.campos = [
            ("Q_gen", "Q_gen (W):"), ("k", "k (W/°C):"), ("T_cool", "T_cool (°C):"), ("C", "C (J/°C):"),
            ("T0", "T0 (°C):"), ("tiempo_min", "Tiempo mínimo (min):"), 
            ("tiempo_max", "Tiempo máximo (min):"), ("puntos", "Puntos de tiempo:")
        ]

        for i, (campo, texto) in enumerate(self.campos):
            self.crear_campo(campo, texto, i // 4, i % 4)

        # Frame para el botón y el mensaje
        self.frame_botones = ctk.CTkFrame(self.frame)
        self.frame_botones.grid(row=4, column=0, columnspan=4, pady=10, sticky="ew")
        self.frame_botones.grid_columnconfigure(1, weight=1)

        # Botón para graficar
        self.button_graficar = ctk.CTkButton(self.frame_botones, text="Generar Gráfica", command=self.simular_y_graficar)
        self.button_graficar.grid(row=0, column=0, padx=(0, 10))

        # Label para mensajes
        self.mensaje_label = ctk.CTkLabel(self.frame_botones, text="", anchor="w")
        self.mensaje_label.grid(row=0, column=1, columnspan=3, sticky="w")

    def crear_campo(self, campo, texto, columna, fila):
        label = ctk.CTkLabel(self.frame, text=texto)
        label.grid(row=fila, column=columna*2, padx=10, pady=5, sticky="e")
        entry = ctk.CTkEntry(self.frame)
        entry.grid(row=fila, column=columna*2+1, padx=10, pady=5, sticky="w")
        setattr(self, f'entry_{campo}', entry)

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def validar_entrada(self, valor):
        try:
            return float(valor)
        except ValueError:
            return None

    def mostrar_mensaje(self, mensaje, tipo="error"):
        if tipo == "error":
            self.mensaje_label.configure(text=mensaje, text_color="red")
        else:
            self.mensaje_label.configure(text=mensaje, text_color="green")

    def simular_y_graficar(self):
        # Validación de entradas
        valores = {}
        for campo, _ in self.campos:
            valor = self.validar_entrada(getattr(self, f'entry_{campo}').get())
            if valor is None:
                self.mostrar_mensaje(f"Error: El campo {campo} debe contener un número válido.")
                return
            valores[campo] = valor

        if valores['tiempo_min'] >= valores['tiempo_max']:
            self.mostrar_mensaje("Error: El tiempo mínimo debe ser menor que el tiempo máximo.")
            return

        # Simulación
        tiempo = np.linspace(valores['tiempo_min'], valores['tiempo_max'], int(valores['puntos']))
        simulacion = SimulacionTermica(valores['Q_gen'], valores['k'], valores['T_cool'], valores['C'], valores['T0'])
        tiempo, solucion = simulacion.simular(tiempo)
        self.mostrar_mensaje("Simulación completada. Generando gráfica...", tipo="exito")

        # Generación de gráfica
        simulacion.graficar(tiempo, solucion.flatten())

if __name__ == "__main__":
    app = InterfazSimulacionTermica()
    app.mainloop()