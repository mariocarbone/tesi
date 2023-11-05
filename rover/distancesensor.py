import time
from gpiozero import DistanceSensor

ultrasonic = DistanceSensor(echo=17, trigger=4)

def get_distance(distance_value):
    while True: 
        with distance_value.get_lock(): 
            distance_value.value = round(ultrasonic.distance * 100, 2)
        time.sleep(0.1)  