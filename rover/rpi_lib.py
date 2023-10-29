import RPi.GPIO as GPIO
import time

class Raspberry(str):

	def __init__(self):
		print("Raspberry Inizializzato")
		
		GPIO.setmode(GPIO.BOARD)
		self.trig_pin = 7
		self.echo_pin = 11
		GPIO.setup(self.trig_pin, GPIO.OUT)
		GPIO.setup(self.echo_pin, GPIO.IN)
		
	# Funzione per misurare la distanza
	def measure_distance(self):
		
		GPIO.output(self.trig_pin, GPIO.HIGH)
		time.sleep(0.00001)
		GPIO.output(self.trig_pin, GPIO.LOW)
		
		while GPIO.input(self.echo_pin) == 0:
			pulse_start = time.time()
		while GPIO.input(self.echo_pin) == 1:
			pulse_end = time.time()
			
		pulse_duration = pulse_end - pulse_start
		
		distance_value = pulse_duration * 17150
				
		#print("Distance = ", distance_value)
		
		return round(distance_value,2)
		GPIO.cleanup()