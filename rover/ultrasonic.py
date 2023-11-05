import RPi.GPIO as GPIO
import time

# GPIO pin configuration
GPIO.setmode(GPIO.BOARD)
GPIO_ECHO = 11

# Variabile globale per la distanza misurata
distance_value = 0.0

# Funzione per gestire l'evento GPIO
def distance_callback(channel):
    global distance_value
    if GPIO.input(channel) == GPIO.HIGH:
        start_time = time.time()
    else:
        stop_time = time.time()
        time_elapsed = stop_time - start_time
        distance = (time_elapsed * 34300) / 2
        distance_value = distance

# Imposta il callback per l'evento GPIO
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.add_event_detect(GPIO_ECHO, GPIO.BOTH, callback=distance_callback)

# Funzione per ottenere la distanza misurata
def get_distance():
    global distance_value
    return distance_value
