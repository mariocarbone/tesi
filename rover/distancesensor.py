from gpiozero import DistanceSensor

ultrasonic = DistanceSensor(echo=17, trigger=4)
def get_distance():
    return round(ultrasonic.distance*100,2)


if __name__ == "__main__":
    while True:
        print(get_distance())