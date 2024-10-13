import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
import customtkinter as ctk

class ReaccionQuimica:
    def __init__(self, k, A0):
        # Inicializa los parámetros de la reacción
        self.k = k  # Constante de velocidad
        self.A0 = A0  # Concentración inicial

    def modelo(self, A, t):
        # Define el modelo de la reacción química
        dA_dt = -self.k * A  # Ecuación diferencial para la concentración de A
        return dA_dt

    def simular(self):
        # Realiza la simulación de la reacción
        tiempo = np.linspace(0, 50, 1000)  # Crea un array de tiempo de 0 a 50 minutos
        solucion = odeint(self.modelo, self.A0, tiempo)  # Resuelve la ecuación diferencial
        return tiempo, solucion

    def graficar(self, tiempo, solucion):
        # Genera el gráfico de la simulación
        plt.figure(figsize=(10, 5))
        plt.plot(tiempo, solucion, label='Concentración de [A]')
        plt.xlabel('Tiempo (minutos)')
        plt.ylabel('Concentración (mol/L)')
        plt.title('Descomposición de un Reactivo de Primer Orden')
        plt.grid(True)
        plt.legend()
        plt.show()

class InterfazReaccionQuimica(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Simulación de Reacción Química")
        self.geometry("400x300")
        self.minsize(400, 300)  # Establece el tamaño mínimo de la ventana
        self.center_window()  # Centra la ventana al aparecer

        # Crea el frame principal
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Crea y coloca los widgets para la entrada de k
        self.label_k = ctk.CTkLabel(self.frame, text="Constante de velocidad (k):")
        self.label_k.pack(pady=5)
        self.entry_k = ctk.CTkEntry(self.frame)
        self.entry_k.pack(pady=5)

        # Crea y coloca los widgets para la entrada de A0
        self.label_A0 = ctk.CTkLabel(self.frame, text="Concentración inicial (A0):")
        self.label_A0.pack(pady=5)
        self.entry_A0 = ctk.CTkEntry(self.frame)
        self.entry_A0.pack(pady=5)

        # Crea y coloca el botón para generar la gráfica
        self.button_graficar = ctk.CTkButton(self.frame, text="Generar Gráfica", command=self.simular_y_graficar)
        self.button_graficar.pack(pady=10)

        # Crea y coloca el label para mostrar mensajes
        self.mensaje_label = ctk.CTkLabel(self.frame, text="")
        self.mensaje_label.pack(pady=10)

    def center_window(self):
        # Centra la ventana en la pantalla
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def validar_entrada(self, valor):
        # Valida que la entrada sea un número flotante
        try:
            return float(valor)
        except ValueError:
            return None

    def mostrar_mensaje(self, mensaje):
        # Actualiza el texto del label de mensajes
        self.mensaje_label.configure(text=mensaje)

    def simular_y_graficar(self):
        # Obtiene y valida los valores de entrada
        k = self.validar_entrada(self.entry_k.get())
        A0 = self.validar_entrada(self.entry_A0.get())

        if k is None or A0 is None:
            self.mostrar_mensaje("Error: Por favor, ingrese valores numéricos válidos.")
            return

        # Crea una instancia de ReaccionQuimica y realiza la simulación
        reaccion = ReaccionQuimica(k, A0)
        tiempo, solucion = reaccion.simular()
        self.mostrar_mensaje("Simulación completada. Generando gráfica...")
        
        # Genera y muestra la gráfica
        reaccion.graficar(tiempo, solucion)

if __name__ == "__main__":
    app = InterfazReaccionQuimica()
    app.mainloop()