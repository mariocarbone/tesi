import RPi.GPIO as GPIO
import time

# GPIO pin configuration
GPIO.setmode(GPIO.BOARD)
GPIO_TRIGGER = 7
GPIO_ECHO = 11

def distance_measurement():
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)

    # Allow the sensor to settle
    print("Waiting for sensor to settle...")
    time.sleep(2)

    # Function to trigger a distance measurement
    def trigger_measurement():
        GPIO.output(GPIO_TRIGGER, True)
        time.sleep(0.00001)
        GPIO.output(GPIO_TRIGGER, False)

    # Initialize the sensor
    print("Initializing the sensor...")
    trigger_measurement()
    print("Sensor ready")

    start_time = time.time()
    stop_time = time.time()
    distance = 0

    # Callback function for echo pin
    def echo_callback(channel):
        nonlocal start_time, stop_time, distance

        if GPIO.input(GPIO_ECHO):
            start_time = time.time()
        else:
            stop_time = time.time()
            time_elapsed = stop_time - start_time
            distance = (time_elapsed * 34300) / 2

    # Register the callback function for the falling edge of the echo signal
    GPIO.add_event_detect(GPIO_ECHO, GPIO.BOTH, callback=echo_callback)

    try:
        while True:  # Ensure that you exit the loop when `stop_threads` is set to True
            # Trigger a distance measurement
            trigger_measurement()

            # Wait for a short time to allow the measurement to complete
            time.sleep(0.1)

            print(distance)

    except KeyboardInterrupt:
        print("Measurement stopped")
        GPIO.cleanup()
