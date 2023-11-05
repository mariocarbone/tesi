import RPi.GPIO as GPIO
import time
from threading import Thread, Lock

# GPIO pin configuration
GPIO.setmode(GPIO.BOARD)
GPIO_TRIGGER = 7
GPIO_ECHO = 11

# Variabile globale per la distanza misurata
distance_value = 0.0
distance_lock = Lock()

# Funzione per misurare la distanza utilizzando il sensore ad ultrasuoni
def distance_measurement():
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)

    while True:
        GPIO.output(GPIO_TRIGGER, True)
        time.sleep(0.00001)
        GPIO.output(GPIO_TRIGGER, False)

        start_time = time.time()
        stop_time = time.time()

        while GPIO.input(GPIO_ECHO) == 0:
            start_time = time.time()

        while GPIO.input(GPIO_ECHO) == 1:
            stop_time = time.time()

        time_elapsed = stop_time - start_time
        distance = (time_elapsed * 34300) / 2

        # Aggiorna la variabile globale `distance_value` con il valore misurato
        with distance_lock:
            distance_value = distance

        time.sleep(0.5)

# Funzione per ottenere la distanza misurata
def get_distance():
    global distance_value
    return distance_value
