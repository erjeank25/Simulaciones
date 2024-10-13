import random
import simpy
import math
import customtkinter as ctk

class SimulacionPeluqueria:
    def __init__(self, semilla, num_peluqueros, tiempo_corte_min, tiempo_corte_max, t_llegadas, tot_clientes):
        self.semilla = semilla
        self.num_peluqueros = num_peluqueros
        self.tiempo_corte_min = tiempo_corte_min
        self.tiempo_corte_max = tiempo_corte_max
        self.t_llegadas = t_llegadas
        self.tot_clientes = tot_clientes
        self.te = 0.0  # tiempo de espera total
        self.dt = 0.0  # duración del servicio
        self.fin = 0.0  # minuto en que finaliza
        self.env = simpy.Environment()
        self.personal = simpy.Resource(self.env, num_peluqueros)
        random.seed(self.semilla)
        self.resultados = []

    def cortar(self, cliente):
        R = random.random()
        tiempo = self.tiempo_corte_max - self.tiempo_corte_min
        tiempo_corte = self.tiempo_corte_min + (tiempo * R)  # dist Uniforme
        yield self.env.timeout(tiempo_corte)
        self.resultados.append(f"Corte listo a {cliente} en {tiempo_corte:.2f} minutos")
        self.dt += tiempo_corte

    def cliente(self, name):
        llega = self.env.now
        self.resultados.append(f"--> {name} llegó a la peluquería en el minuto {llega:.2f}")
        with self.personal.request() as request:
            yield request
            pasa = self.env.now
            espera = pasa - llega
            self.te += espera
            self.resultados.append(f"{name} Pasa y espera en la peluquería en el minuto {pasa:.2f} habiendo esperado {espera:.2f}")
            yield self.env.process(self.cortar(name))
            deja = self.env.now
            self.resultados.append(f"<--{name} deja la peluquería en minuto {deja:.2f}")
            self.fin = deja

    def principal(self):
        for i in range(self.tot_clientes):
            R = random.random()
            llegada = -self.t_llegadas * math.log(R)
            yield self.env.timeout(llegada)
            self.env.process(self.cliente(f'cliente {i+1}'))

    def ejecutar_simulacion(self):
        self.env.process(self.principal())
        self.env.run()

        lpc = self.te / self.fin
        tep = self.te / self.tot_clientes
        upi = (self.dt / self.fin) / self.num_peluqueros

        self.resultados.append("\nIndicadores obtenidos")
        self.resultados.append(f"Longitud promedio de la cola: {lpc:.2f}")
        self.resultados.append(f"Tiempo de espera promedio: {tep:.2f}")
        self.resultados.append(f"Uso promedio de la instalación: {upi:.2f}")

        return "\n".join(self.resultados)

class InterfazSimulacionPeluqueria(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Simulación Peluquería")
        self.geometry("800x600")
        self.minsize(800, 600)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1)

        self.crear_widgets()

    def crear_widgets(self):
        campos = [
            ("Semilla:", "semilla"),
            ("Número de peluqueros:", "num_peluqueros"),
            ("Tiempo de corte mínimo:", "tiempo_corte_min"),
            ("Tiempo de corte máximo:", "tiempo_corte_max"),
            ("Tiempo entre llegadas:", "t_llegadas"),
            ("Total de clientes:", "tot_clientes")
        ]

        for i, (label, attr) in enumerate(campos):
            ctk.CTkLabel(self, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = ctk.CTkEntry(self)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
            setattr(self, f"entry_{attr}", entry)

        self.btn_simular = ctk.CTkButton(self, text="Generar Simulación", command=self.ejecutar_simulacion)
        self.btn_simular.grid(row=6, column=0, columnspan=2, pady=20)

        self.txt_resultados = ctk.CTkTextbox(self, width=700, height=300)
        self.txt_resultados.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.txt_resultados.configure(state="disabled")

    def validar_entradas(self):
        try:
            semilla = int(self.entry_semilla.get())
            num_peluqueros = int(self.entry_num_peluqueros.get())
            tiempo_corte_min = float(self.entry_tiempo_corte_min.get())
            tiempo_corte_max = float(self.entry_tiempo_corte_max.get())
            t_llegadas = float(self.entry_t_llegadas.get())
            tot_clientes = int(self.entry_tot_clientes.get())

            if tiempo_corte_max <= tiempo_corte_min:
                raise ValueError("El tiempo de corte máximo debe ser mayor que el mínimo.")

            return semilla, num_peluqueros, tiempo_corte_min, tiempo_corte_max, t_llegadas, tot_clientes
        except ValueError as e:
            self.mostrar_error(str(e))
            return None

    def mostrar_error(self, mensaje):
        self.txt_resultados.configure(state="normal")
        self.txt_resultados.delete("1.0", ctk.END)
        self.txt_resultados.insert(ctk.END, f"Error: {mensaje}")
        self.txt_resultados.configure(state="disabled")

    def ejecutar_simulacion(self):
        parametros = self.validar_entradas()
        if parametros:
            simulacion = SimulacionPeluqueria(*parametros)
            resultados = simulacion.ejecutar_simulacion()
            self.txt_resultados.configure(state="normal")
            self.txt_resultados.delete("1.0", ctk.END)
            self.txt_resultados.insert(ctk.END, resultados)
            self.txt_resultados.configure(state="disabled")

if __name__ == "__main__":
    app = InterfazSimulacionPeluqueria()
    app.mainloop()