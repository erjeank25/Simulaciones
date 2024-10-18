import simpy
import random
import sys
import io
import customtkinter as ctk

class NetworkSimulationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Simulación de Red de Computadoras")
        self.geometry("800x600")
        self.minsize(800, 600)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(8, weight=1)

        self.create_widgets()

    def create_widgets(self):
        params = [
            ("Semilla", "semilla", 42),
            ("Capacidad del Servidor", "capacidad_servidor", 1),
            ("Capacidad de la Cola", "capacidad_cola", 5),
            ("Tiempo Mínimo de Procesamiento", "tiempo_procesamiento_min", 2),
            ("Tiempo Máximo de Procesamiento", "tiempo_procesamiento_max", 5),
            ("Tiempo Promedio Entre Llegadas", "tiempo_llegadas", 3),
            ("Total de Paquetes", "total_paquetes", 50)
        ]

        self.entries = {}
        for i, (label, attr, default) in enumerate(params):
            ctk.CTkLabel(self, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = ctk.CTkEntry(self)
            entry.insert(0, str(default))
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
            self.entries[attr] = entry

        self.btn_simular = ctk.CTkButton(self, text="Empezar Simulación", command=self.run_simulation)
        self.btn_simular.grid(row=len(params), column=0, columnspan=2, pady=20)

        self.txt_resultados = ctk.CTkTextbox(self, width=700, height=300)
        self.txt_resultados.grid(row=len(params)+1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.txt_resultados.configure(state="disabled")

    def validate_inputs(self):
        errors = []
        for name, entry in self.entries.items():
            try:
                value = float(entry.get())
                if value <= 0:
                    errors.append(f"{name} debe ser un número entero positivo.")
            except ValueError:
                errors.append(f"{name} debe ser un número entero válido.")

        # Verificar que el tiempo máximo de procesamiento sea mayor que el mínimo
        try:
            tiempo_min = int(self.entries['tiempo_procesamiento_min'].get())
            tiempo_max = int(self.entries['tiempo_procesamiento_max'].get())
            if tiempo_max <= tiempo_min:
                errors.append("El tiempo máximo de procesamiento debe ser mayor que el mínimo.")
        except ValueError:
            errors.append("Los tiempos de procesamiento deben ser números enteros válidos.")

        return errors

    def run_simulation(self):
        errors = self.validate_inputs()
        if errors:
            self.show_result("\n".join(errors))
            return

        # Capturar la salida estándar
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        # Ejecutar la simulación
        self.simulate()

        # Obtener la salida capturada
        simulation_output = sys.stdout.getvalue()

        # Restaurar la salida estándar
        sys.stdout = old_stdout

        # Mostrar los resultados
        self.show_result(simulation_output)

    def simulate(self):
        # Obtener parámetros de la interfaz
        SEMILLA = int(self.entries['semilla'].get())
        CAPACIDAD_SERVIDOR = int(self.entries['capacidad_servidor'].get())
        CAPACIDAD_COLA = int(self.entries['capacidad_cola'].get())
        TIEMPO_PROCESAMIENTO_MIN = int(self.entries['tiempo_procesamiento_min'].get())
        TIEMPO_PROCESAMIENTO_MAX = int(self.entries['tiempo_procesamiento_max'].get())
        TIEMPO_LLEGADAS = float(self.entries['tiempo_llegadas'].get())
        TOTAL_PAQUETES = int(self.entries['total_paquetes'].get())

        # Variables para seguimiento de estadísticas
        paquetes_perdidos = 0
        tiempo_total_espera = 0
        paquetes_procesados = 0

        # Función para simular el proceso de un paquete
        def paquete(env, nombre, servidor):
            nonlocal paquetes_perdidos, tiempo_total_espera, paquetes_procesados

            llegada = env.now  # Momento de llegada del paquete al sistema
            print(f'{nombre} llega al servidor en el segundo {llegada:.2f}')

            with servidor.request() as req:
                # Si el servidor y la cola están llenos, el paquete se pierde
                if len(servidor.queue) >= CAPACIDAD_COLA:
                    paquetes_perdidos += 1
                    print(f'{nombre} se pierde debido a cola llena en el segundo {env.now:.2f}')
                    return

                # El paquete espera su turno en la cola si es necesario
                yield req
                espera = env.now - llegada
                tiempo_total_espera += espera
                print(f'{nombre} comienza a ser procesado después de esperar {espera:.2f} segundos en el segundo {env.now:.2f}')

                # Simula el tiempo de procesamiento del paquete
                tiempo_procesamiento = random.randint(TIEMPO_PROCESAMIENTO_MIN, TIEMPO_PROCESAMIENTO_MAX)
                yield env.timeout(tiempo_procesamiento)
                print(f'{nombre} termina de ser procesado en el segundo {env.now:.2f}')
                paquetes_procesados += 1

        # Función para la llegada de paquetes
        def llegada_paquetes(env, servidor):
            for i in range(TOTAL_PAQUETES):
                yield env.timeout(random.expovariate(1.0 / TIEMPO_LLEGADAS))
                env.process(paquete(env, f'Paquete {i+1}', servidor))

        # Configuración y ejecución de la simulación
        print('--- Simulación de Red de Computadoras ---')
        random.seed(SEMILLA)
        env = simpy.Environment()
        servidor = simpy.Resource(env, CAPACIDAD_SERVIDOR)
        env.process(llegada_paquetes(env, servidor))
        env.run()
        print('--- Fin de la simulación ---')

        # Salidas de la simulación
        print("\nResultados de la simulación:")
        print(f'Total de paquetes simulados: {TOTAL_PAQUETES}')
        print(f'Paquetes procesados: {paquetes_procesados}')
        print(f'Paquetes perdidos: {paquetes_perdidos}')
        print(f'Tasa de pérdida de paquetes: {100 * paquetes_perdidos / TOTAL_PAQUETES:.2f}%')
        print(f'Tiempo promedio de espera de los paquetes: {tiempo_total_espera / paquetes_procesados if paquetes_procesados > 0 else 0:.2f} segundos')
        print(f'Utilización del servidor: {100 * (paquetes_procesados * (TIEMPO_PROCESAMIENTO_MIN + TIEMPO_PROCESAMIENTO_MAX) / 2) / env.now:.2f}%')

    def show_result(self, text):
        self.txt_resultados.configure(state="normal")
        self.txt_resultados.delete("1.0", ctk.END)
        self.txt_resultados.insert(ctk.END, text)
        self.txt_resultados.configure(state="disabled")


if __name__ == "__main__":
    ctk.set_default_color_theme("blue")
    app = NetworkSimulationApp()
    app.mainloop()
