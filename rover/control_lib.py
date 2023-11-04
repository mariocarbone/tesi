from threading import Lock
import threading
import time
from rpi_lib import Raspberry
from arduino_lib import Arduino

class Vehicle_Control():

    def __init__(self):
        print("Vehicle Control avviato")
        self.arduino = Arduino("/dev/ttyACM0", 9600, 1, 1)
        self.rpi = Raspberry()
        self.status = {}
        self.status['braking'] = False
        self.status['moving'] = False
        self.status_lock = Lock()
        self.distance = 0.0
        self.distance_lock = Lock()

    def update_distance(self):
        #self.distance, self.distance_lock, self.rpi
        with self.distance_lock:
            self.distance = round(self.rpi.measure_distance(), 2)

    def update_status(self):
        #self.status, self.status_lock, self.rpi, self.arduino
        with self.status_lock:
            self.status = self.arduino.get_status()
            print(self.arduino.get_status())
            print(self.status)
            if(int(self.status['speed'])==0):
                self.status.update(('moving', False))
            else:
                self.status.update(('moving', True))

    def get_distance(self):
        self.distance, self.distance_lock

        with self.distance_lock:
            return self.distance

    def get_status(self):
        self.status, self.status_lock

        with self.status_lock:
            return self.status