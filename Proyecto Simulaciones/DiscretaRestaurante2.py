import customtkinter as ctk
import simpy
import random
import sys
import io


class RestauranteSimulacion:
    def __init__(self, semilla, num_mesas, tiempo_comer_min, tiempo_comer_max, tiempo_llegadas, total_clientes):
        self.semilla = semilla
        self.num_mesas = num_mesas
        self.tiempo_comer_min = tiempo_comer_min
        self.tiempo_comer_max = tiempo_comer_max
        self.tiempo_llegadas = tiempo_llegadas
        self.total_clientes = total_clientes

    def cliente(self, env, nombre, restaurante):
        print(f'{nombre} llega al restaurante en el minuto {env.now:.2f}')
        with restaurante.request() as mesa:
            yield mesa
            print(f'{nombre} toma una mesa en el minuto {env.now:.2f}')
            tiempo_comer = random.randint(self.tiempo_comer_min, self.tiempo_comer_max)
            yield env.timeout(tiempo_comer)
            print(f'{nombre} termina de comer y deja la mesa en el minuto {env.now:.2f}')

    def llegada_clientes(self, env, restaurante):
        for i in range(self.total_clientes):
            yield env.timeout(random.expovariate(1.0 / self.tiempo_llegadas))
            env.process(self.cliente(env, f'Cliente {i+1}', restaurante))

    def run(self):
        print('--- Simulación del Restaurante ---')
        random.seed(self.semilla)
        env = simpy.Environment()
        restaurante = simpy.Resource(env, self.num_mesas)
        env.process(self.llegada_clientes(env, restaurante))
        env.run()
        print('--- Fin de la simulación ---')


class RestaurantSimulationGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Simulación de Restaurante")
        self.geometry("800x600")
        self.minsize(800, 600)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1)

        self.create_widgets()

    def create_widgets(self):
        params = [
            ("Semilla", "semilla", 42),
            ("Número de Mesas", "num_mesas", 5),
            ("Tiempo Mínimo de Comer", "tiempo_comer_min", 20),
            ("Tiempo Máximo de Comer", "tiempo_comer_max", 40),
            ("Tiempo Promedio entre Llegadas", "tiempo_llegadas", 10),
            ("Total de Clientes", "total_clientes", 10)
        ]

        self.entries = {}
        for i, (label, attr, default) in enumerate(params):
            ctk.CTkLabel(self, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = ctk.CTkEntry(self)
            entry.insert(0, str(default))
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
            self.entries[attr] = entry

        self.btn_simular = ctk.CTkButton(self, text="Generar Simulación", command=self.run_simulation)
        self.btn_simular.grid(row=len(params), column=0, columnspan=2, pady=20)

        self.txt_resultados = ctk.CTkTextbox(self, width=700, height=300)
        self.txt_resultados.grid(row=len(params)+1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.txt_resultados.configure(state="disabled")

    def validate_inputs(self):
        errors = []
        try:
            tiempo_min = int(self.entries['tiempo_comer_min'].get())
            tiempo_max = int(self.entries['tiempo_comer_max'].get())
            if tiempo_max <= tiempo_min:
                errors.append("El tiempo máximo de comer debe ser mayor que el tiempo mínimo.")
        except ValueError:
            errors.append("Los tiempos de comer deben ser números enteros válidos.")

        for name, entry in self.entries.items():
            try:
                value = int(entry.get())
                if value <= 0:
                    errors.append(f"{name} debe ser un número entero positivo.")
            except ValueError:
                errors.append(f"{name} debe ser un número entero válido.")
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
        simulation = RestauranteSimulacion(
            semilla=int(self.entries['semilla'].get()),
            num_mesas=int(self.entries['num_mesas'].get()),
            tiempo_comer_min=int(self.entries['tiempo_comer_min'].get()),
            tiempo_comer_max=int(self.entries['tiempo_comer_max'].get()),
            tiempo_llegadas=int(self.entries['tiempo_llegadas'].get()),
            total_clientes=int(self.entries['total_clientes'].get())
        )
        simulation.run()

        # Obtener la salida capturada
        simulation_output = sys.stdout.getvalue()

        # Restaurar la salida estándar
        sys.stdout = old_stdout

        # Mostrar los resultados
        self.show_result(simulation_output)

    def show_result(self, text):
        self.txt_resultados.configure(state="normal")
        self.txt_resultados.delete("1.0", ctk.END)
        self.txt_resultados.insert(ctk.END, text)
        self.txt_resultados.configure(state="disabled")


if __name__ == "__main__":
    ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
    app = RestaurantSimulationGUI()
    app.mainloop()
