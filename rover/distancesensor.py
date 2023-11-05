from gpiozero import DistanceSensor

ultrasonic = DistanceSensor(echo=17, trigger=4, queue_len=1)

def get_distance():
    return round(ultrasonic.distance*100,2)
