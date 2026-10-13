'''
SISTEMA DE CONTROL DE SEGUNDO ORDEN

Esta implementación ejecuta una función de transferencia discreta H(z)
basada en un sistema de segundo orden continuo.
Se utiliza un temporizador por hardware de la Raspberry Pi Pico 2W
para garantizar un tiempo de muestreo estricto de Ts = 0.025s (40 Hz).

Por:
- Ayala Hernández María Fernanda
- Salazar Islas Luis Daniel
- Tepal Briseño Hansel Yael
- Ugartechea González Luis Antonio
'''

# --- EXPLICACIÓN DEL FUNCIONAMIENTO ---
# El script utiliza el módulo `machine.Timer` de MicroPython para
# generar una interrupción de hardware exacta cada 25 milisegundos (40 Hz),
# cumpliendo con la restricción de muestreo sin bloquear el microcontrolador.
# En cada interrupción (ciclo de reloj) el sistema realiza lo siguiente:
# 1. Lee la entrada actual x[k] (ej. desde un pin analógico).
# 2. Calcula la salida actual y[k] resolviendo la ecuación de diferencias obtenida al discretizar H(s) a H(z).
# 3. Actualiza el historial de variables (memoria) desplazando los valores anteriores (x[k-1], y[k-1], etc.) para que estén listos en el próximo ciclo.
# --------------- ARM Assembly function ---------------

from machine import Pin, Timer, ADC
from math import isfinite
import time

# --- COEFICIENTES DEL SISTEMA DISCRETO H(z) ---
b0 = 0.01
b1 = 0.02
b2 = 0.01
a1 = -1.6
a2 = 0.64

# Sistema con respuesta más rápida y amortiguada:
# b0 = 0.04
# b1 = 0.08
# b2 = 0.04
# a1 = -1.2
# a2 = 0.36

# Sistema con respuesta más lenta:
# b0 = 0.005
# b1 = 0.010
# b2 = 0.005
# a1 = -1.8
# a2 = 0.81

# --- VARIABLES DE ESTADO (Memoria del sistema) ---
x_k1 = 0.0
x_k2 = 0.0
y_k1 = 0.0
y_k2 = 0.0
entrada_filtrada = 0.0
ultima_entrada = 0
ultima_salida = 0.0
nueva_muestra = False

ALFA_ENTRADA = 0.1
LIMITE_SALIDA = 65535.0

entrada_adc = ADC(26)

def iteracion_control(timer):
    global x_k1, x_k2, y_k1, y_k2, entrada_filtrada
    global ultima_entrada, ultima_salida, nueva_muestra
    # 1. Leer la entrada actual x[k]
    # El ADC tiene un valor de 0 a 65535
    lectura_adc = entrada_adc.read_u16()
    entrada_filtrada = (ALFA_ENTRADA * lectura_adc) + ((1 - ALFA_ENTRADA) * entrada_filtrada)
    x_k = entrada_filtrada

    # 2. Calcular la salida y[k] mediante la ecuación de diferencias
    y_k = (b0 * x_k) + (b1 * x_k1) + (b2 * x_k2) - (a1 * y_k1) - (a2 * y_k2)

    if not isfinite(y_k):
        y_k = 0.0
        y_k1 = 0.0
        y_k2 = 0.0
    elif y_k > LIMITE_SALIDA:
        y_k = LIMITE_SALIDA
    elif y_k < -LIMITE_SALIDA:
        y_k = -LIMITE_SALIDA

    # Guardar la muestra para imprimirla fuera de la interrupción.
    ultima_entrada = x_k
    ultima_salida = y_k
    nueva_muestra = True

    # 4. Actualizar las variables de estado para la siguiente interrupción
    x_k2 = x_k1
    x_k1 = x_k
    y_k2 = y_k1
    y_k1 = y_k

# --- INICIALIZACIÓN DEL TIMER ---
tiempo_muestreo = 25 # En milisegundos
timer_muestreo = Timer(-1)
timer_muestreo.init(period=tiempo_muestreo, mode=Timer.PERIODIC, callback=iteracion_control)

frecuencia_muestreo = 1000 / tiempo_muestreo
print("Sistema de control de segundo orden iniciado a {:.2f} Hz.".format(frecuencia_muestreo))

# El bucle principal queda libre para otras tareas (pantallas, comunicaciones, etc.)
try:
    while True:
        if nueva_muestra:
            nueva_muestra = False
            # Formato consumido por la interfaz gráfica: DATA,tiempo_ms,x,y.
            print("{:.3f} {:.3f}".format(ultima_entrada, ultima_salida))
        time.sleep_ms(1)
except KeyboardInterrupt:
    # Detener el timer si se cancela la ejecución en la consola
    timer_muestreo.deinit()
    print()
    print("Sistema detenido.")