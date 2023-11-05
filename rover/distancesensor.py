from multiprocessing import Value
from gpiozero import DistanceSensor

ultrasonic = DistanceSensor(echo=17, trigger=4)

def get_distance(distance_value)::
    with distance_value.get_lock():
        distance_value.value = round(ultrasonic.distance * 100, 2)

#if __name__ == "__main__":
 #   distance_value = Value('d', 0.0)  # 'd' indica un valore double
  #  get_distance(distance_value)