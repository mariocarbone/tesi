import RPi.GPIO as GPIO
import time


class Raspberry(str):

	def __init__(self):
		print("Raspberry Inizializzato")
		
# Funzione per misurare la distanza
	def measure_distance():
		
		global distance, distance_value
		GPIO.setmode(GPIO.BOARD)
		
		trig_pin = 7
		echo_pin = 11
		GPIO.setup(trig_pin, GPIO.OUT)
		GPIO.setup(echo_pin, GPIO.IN)
		
		while True:
			
			GPIO.output(trig_pin, GPIO.HIGH)
			time.sleep(0.00001)
			GPIO.output(trig_pin, GPIO.LOW)
			
			while GPIO.input(echo_pin) == 0:
				pulse_start = time.time()
			while GPIO.input(echo_pin) == 1:
				pulse_end = time.time()
				
			pulse_duration = pulse_end - pulse_start
			
			distance_value = pulse_duration * 17150
			
			#with distance_lock:
			#	distance.value = round(distance_value, 2)
			return round(distance_value,2)

			time.sleep(1)
