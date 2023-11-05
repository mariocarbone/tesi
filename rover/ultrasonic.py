import RPi.GPIO as GPIO
import time

# GPIO pin configuration
GPIO.setmode(GPIO.BOARD)
GPIO_TRIGGER = 7
GPIO_ECHO = 11

# Initialize GPIO pins
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

start_time = 0
stop_time = 0
distance = 0

# Callback function for echo pin
def echo_callback(channel):
    global start_time, stop_time, distance

    if GPIO.input(GPIO_ECHO):
        start_time = time.time()
    else:
        stop_time = time.time()
        time_elapsed = stop_time - start_time
        distance = (time_elapsed * 34300) / 2

# Register the callback function for the falling edge of the echo signal
GPIO.add_event_detect(GPIO_ECHO, GPIO.FALLING, callback=echo_callback)

try:
    while True:
        # Your main loop code here
        print("Distance:", distance, "cm")
        time.sleep(1)

except KeyboardInterrupt:
    print("Measurement stopped")
    GPIO.cleanup()
