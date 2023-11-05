import RPi.GPIO as GPIO
import time
 
GPIO.setmode(GPIO.BOARD)
 
GPIO_TRIGGER = 7
GPIO_ECHO = 11

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

distance = 0
 
def distance():
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    start_time = time.time()
    stop_time = time.time()
 
    while GPIO.input(GPIO_ECHO) == 0:
        start_time = time.time()
 
    while GPIO.input(GPIO_ECHO) == 1:
        stop_time = time.time()
 
    time_elapsed = stop_time - start_time
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (time_elapsed * 34300) / 2
 
    return distance
 
