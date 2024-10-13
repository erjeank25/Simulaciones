import os
import sys
import random
import datetime
import simpy

def clear():
    os.system(['clear', 'cls'][os.name == 'nt'])

def toc(raw):
    return '%02d:%02d' % (raw / 60, raw % 60)

def get_int_input(prompt, min_value=None, max_value=None):
    while True:
        try:
            value = int(input(prompt))
            if min_value is not None and value < min_value:
                print(f"El valor debe ser al menos {min_value}")
            elif max_value is not None and value > max_value:
                print(f"El valor debe ser como máximo {max_value}")
            else:
                return value
        except ValueError:
            print("Por favor, ingrese un número entero válido")

def get_float_input(prompt, min_value=None):
    while True:
        try:
            value = float(input(prompt))
            if min_value is not None and value <= min_value:
                print(f"El valor debe ser mayor que {min_value}")
            else:
                return value
        except ValueError:
            print("Por favor, ingrese un número válido")

def get_range_input(prompt):
    while True:
        try:
            min_val, max_val = map(int, input(prompt).split(','))
            if min_val >= max_val:
                print("El valor máximo debe ser mayor que el mínimo")
            else:
                return [min_val, max_val]
        except ValueError:
            print("Por favor, ingrese dos números enteros separados por coma")

# Obtener inputs del usuario
HOUR_OPEN = get_int_input("Ingrese Hora de Apertura (Entre 0 y 23): ", 0, 23)
HOUR_CLOSE = get_int_input("Ingrese Hora de Cierre (Entre 0 y 23): ", HOUR_OPEN + 1, 23)
PEAK_START = get_int_input("Ingrese Inicio de Hora Pico (Entre 0 y 23): ", 0, 23)
PEAK_END = get_int_input("Ingrese Fin de Hora Pico Entre (0 y 23): ", PEAK_START + 1, 23)
NUM_COUNTERS = get_int_input("Ingrese numero de operadores (2 o 3): ", 1)
TIME_COUNTER_A = get_int_input("Ingrese Tiempo de Mostrador A (min): ", 1)
TIME_COUNTER_B = get_int_input("Ingrese Tiempo de Mostrador B (min): ", 1)
TIME_COUNTER_C = get_int_input("Ingrese Tiempo de Mostrador C (min): ", 1)
CUSTOMER_RANGE_NORM = get_range_input("Ingrese Rango de Clientes en Horario Normal (dos enteros separados por coma, min,max): ")
CUSTOMER_RANGE_PEAK = get_range_input("Ingrese Rango de Clientes en Horario Pico (dos enteros separados por coma, min,max): ")
RANDOM_SEED = get_int_input("Ingrese la semilla aleatoria (entero): ")

# Configuración de la simulación
START = HOUR_OPEN * 60
SIM_TIME = HOUR_CLOSE * 60
PEAK_TIME = 60 * (PEAK_END - PEAK_START)

# Variables globales
STATE = 0
TEMP = 0
SUM_ALL = 0.00
CALC = [0] * 500

# Clases y funciones de la simulación (sin cambios)
class waitingLane(object):
    def __init__(self, env):
        self.env = env
        self.lane = simpy.Resource(env, 3)

    def serve(self, cust):
        yield self.env.timeout(0)
        print("[w] (%s) %s entered the area" % (toc(env.now), cust))

class counterFirst(object):
    def __init__(self, env):
        self.env = env
        self.employee = simpy.Resource(env, 1)

    def serve(self, cust):
        yield self.env.timeout(random.randint(TIME_COUNTER_A - 1, TIME_COUNTER_A + 1))
        print("[?] (%s) %s ordered the menu" % (toc(env.now), cust))

class counterSecond(object):
    def __init__(self, env):
        self.env = env
        self.employee = simpy.Resource(env, 1)

    def serve(self, cust):
        yield self.env.timeout(random.randint(TIME_COUNTER_B - 1, TIME_COUNTER_B + 1))
        print("[$] (%s) %s paid the order" % (toc(env.now), cust))

class counterFirstSecond(object):
    def __init__(self, env):
        self.env = env
        self.employee = simpy.Resource(env, 1)

    def serve(self, cust):
        yield self.env.timeout(random.randint(TIME_COUNTER_A - 1, TIME_COUNTER_A + 1))
        print("[?] (%s) %s ordered the menu" % (toc(env.now), cust))
        yield self.env.timeout(random.randint(TIME_COUNTER_B - 1, TIME_COUNTER_B + 1))
        print("[$] (%s) %s paid the order" % (toc(env.now), cust))

class counterThird(object):
    def __init__(self, env):
        self.env = env
        self.employee = simpy.Resource(env, 1)

    def serve(self, cust):
        yield self.env.timeout(random.randint(TIME_COUNTER_C - 1, TIME_COUNTER_C + 1))
        print("[#] (%s) %s took the order" % (toc(env.now), cust))

def customer2A(env, name, wl, ce12, ce3):

    with wl.lane.request() as request:

        if (env.now >= SIM_TIME):
            print("[!] Not enough time! %s cancelled" % name)
            return

        yield request
        yield env.process(wl.serve(name))
        print("[w] (%s) %s is in waiting lane" % (toc(env.now), name))

    # Start the actual drive-thru process
    print("[v] (%s) %s is in drive-thru counter" % (toc(env.now), name))

    with ce12.employee.request() as request:

        if (env.now + TIME_COUNTER_A + TIME_COUNTER_B >= SIM_TIME):
            print("[!] Not enough time! Assumed %s is quickly finished" % name)
            yield env.timeout(0.5)
            return

        yield request

        CALC[int(name[5:])] = env.now
        yield env.process(ce12.serve(name))
        print("[?] (%s) %s choose the order" % (toc(env.now), name))

        yield env.process(ce12.serve(name))
        print("[$] (%s) %s is paying and will take the order" %
              (toc(env.now), name))
        env.process(customer2B(env, name, ce12, ce3))


"""
(Type 2) Define customer behavior at second counter
"""


def customer2B(env, name, ce12, ce3):

    with ce3.employee.request() as request:

        if (env.now + TIME_COUNTER_C >= SIM_TIME):
            print("[!] Not enough time! Assumed %s is quickly finished" % name)
            yield env.timeout(0.5)
            return

        yield request

        yield env.process(ce3.serve(name))
        print("[^] (%s) %s leaves" % (toc(env.now), name))

        global TEMP
        TEMP = int(name[5:])
        CALC[int(name[5:])] = env.now - CALC[int(name[5:])]


"""
(Type 3) Define customer behavior at first counter
"""


def customer3A(env, name, wl, ce1, ce2, ce3):

    with wl.lane.request() as request:

        if (env.now >= SIM_TIME):
            print("[!] Not enough time! %s cancelled" % name)
            return

        yield request
        yield env.process(wl.serve(name))
        print("[w] (%s) %s is in waiting lane" % (toc(env.now), name))

    # Start the actual drive-thru process
    print("[v] (%s) %s is in drive-thru counter" % (toc(env.now), name))

    with ce1.employee.request() as request:

        if (env.now + TIME_COUNTER_A >= SIM_TIME):
            print("[!] Not enough time! Assumed %s is quickly finished" % name)
            yield env.timeout(0.5)

        yield request

        CALC[int(name[5:])] = env.now
        yield env.process(ce1.serve(name))
        print("[?] (%s) %s choose the order" % (toc(env.now), name))

        print("[2] (%s) %s will pay the order" % (toc(env.now), name))
        env.process(customer3B(env, name, ce1, ce2, ce3))


"""
(Type 3) Define customer behavior at second counter
"""


def customer3B(env, name, ce1, ce2, ce3):

    with ce2.employee.request() as request:

        if (env.now + TIME_COUNTER_B >= SIM_TIME):
            print("[!] Not enough time! Assumed %s is quickly finished" % name)
            yield env.timeout(0.5)
            return

        yield request

        yield env.process(ce2.serve(name))
        print("[$] (%s) %s is paying the order" % (toc(env.now), name))

        print("[3] (%s) %s will take the order" % (toc(env.now), name))
        env.process(customer3C(env, name, ce1, ce2, ce3))


"""
(Type 3) Define customer behavior at third counter
"""


def customer3C(env, name, ce1, ce2, ce3):

    with ce3.employee.request() as request:

        if (env.now + TIME_COUNTER_C >= SIM_TIME):
            print("[!] Not enough time! Assumed %s is quickly finished" % name)
            yield env.timeout(0.5)
            return

        yield request

        yield env.process(ce3.serve(name))
        print("[^] (%s) %s leaves" % (toc(env.now), name))

        global TEMP
        TEMP = int(name[5:])
        CALC[int(name[5:])] = env.now - CALC[int(name[5:])]


"""
Define detail of 2 counters setup environment
"""


def setup2(env, cr):
    # Create all counters
    wl = waitingLane(env)
    ce12 = counterFirstSecond(env)
    ce3 = counterThird(env)
    i = 0

    # Create more customers while the simulation is running
    while True:
        yield env.timeout(random.randint(*cr))
        i += 1
        env.process(customer2A(env, "Cust %d" % i, wl, ce12, ce3))


"""
Define detail of 3 counters setup environment
"""


def setup3(env, cr):
    # Create all counters
    wl = waitingLane(env)
    ce1 = counterFirst(env)
    ce2 = counterSecond(env)
    ce3 = counterThird(env)
    i = 0

    # Create more customers while the simulation is running
    while True:
        yield env.timeout(random.randint(*cr))
        i += 1
        env.process(customer3A(env, "Cust %d" % i, wl, ce1, ce2, ce3))

if __name__ == "__main__":
    clear()
    print("""
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
>> Restaurant Queuing Model Simulation
>> Drive-Thru Fast Food Restaurant Design Model Evaluation
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>""")

    random.seed(RANDOM_SEED)

    env = simpy.Environment(initial_time=START)
    print("Environment created at %d!" % env.now)

    if NUM_COUNTERS == 2:
        env.process(setup2(env, CUSTOMER_RANGE_NORM))
    elif NUM_COUNTERS == 3:
        env.process(setup3(env, CUSTOMER_RANGE_NORM))
    else:
        print("Error: NUM_COUNTERS debe ser 2 o 3")
        sys.exit(1)

    print("Setup initialized!")
    print("Start simulation!")
    env.run(until=SIM_TIME)

    for i in range(TEMP + 1):
        SUM_ALL += CALC[i]

    averageTimeService = SUM_ALL / (TEMP + 1)
    servicePerSecond = 1.00 / (averageTimeService * 60)
    servicePerMinute = servicePerSecond * 60

    print("The end!")
    print("[i] Model: %d counters" % NUM_COUNTERS)
    print("[i] Average time:       %.4f" % averageTimeService)
    print("[i] Service per minute: %f" % servicePerMinute)