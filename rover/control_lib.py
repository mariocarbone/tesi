from threading import Lock
import threading
import time
from rpi_lib import Raspberry
from arduino_lib import Arduino

class Vehicle_Control():

    def __init__(self):
        print("Vehicle Control avviato")


    status = {}
    status_lock = Lock()
    distance = 0.0
    distance_lock = Lock()

    arduino = Arduino("/dev/ttyACM0", 9600, 1, 1)
    rpi = Raspberry()


    def update_distance(self):
        self.distance, self.distance_lock, self.rpi
        with self.distance_lock:
            self.distance = round(self.rpi.measure_distance(), 2)

    def update_status(self):
        self.status, self.status_lock, self.rpi
        with self.status_lock:
            self.status = self.arduino.get_status()


    def getDistance(self):
        self.distance, self.distance_lock

        with self.distance_lock:
            return self.distance
