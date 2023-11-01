from threading import Lock
import threading
import time
from rpi_lib import Raspberry
from arduino_lib import Arduino

class Vehicle_Control():

    def __init__(self):
        print("Vehicle Control avviato")
        self.loop()


    status = {}
    distance = 0.0
    distance_lock = Lock()

    arduino = Arduino("/dev/ttyACM0", 9600, 1, 1)
    rpi = Raspberry()


    def update_distance(self):
        self.distance, self.distance_lock, self.rpi
        while True:
            with self.distance_lock:
                distance = round(self.rpi.measure_distance(), 2)
            time.sleep(0.5)

    def getDistance(self):
        self.distance, self.distance_lock

        with self.distance_lock:
            return self.distance


    def loop(self):
        updateThread = threading.Thread(target=self.update_distance)
        updateThread.start()
        updateThread.join()
