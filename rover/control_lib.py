from threading import Lock

from rpi_lib import Raspberry
from arduino_lib import Arduino

class Vehicle_Control():

    def __init__(self):
        print("Vehicle Control avviato")


    status = {}
    distance = 0.0
    distance_lock = Lock()

    arduino = Arduino("/dev/ttyACM0", 9600, 1, 1)
    rpi = Raspberry()


    def updateDistance(self):
        global distance, distance_lock, rpi
        with distance_lock:
            distance = round(rpi.measure_distance(), 2)

    def getDistance(self):
        self.distance, self.distance_lock

        with self.distance_lock:
            return self.distance



