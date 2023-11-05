from gpiozero import DistanceSensor
from multiprocessing import Value

ultrasonic = DistanceSensor(echo=17, trigger=4)

def get_distance_value(distance_value):
    with distance_value.get_lock():  # Acquire lock before accessing shared memory
        distance_value.value = round(ultrasonic.distance * 100, 2)