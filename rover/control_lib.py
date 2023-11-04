from threading import Lock
import threading
import time
import json
from rpi_lib import Raspberry
from arduino_lib import Arduino

class Vehicle_Control():

	def __init__(self):
		print("Vehicle Control avviato")
		self.arduino = Arduino("/dev/ttyACM0", 9600, 1, 1)
		self.rpi = Raspberry()
		self.status = {
			"speed": 0,
			"speed_left_side": 0,
			"speed_right_side": 0,
			"steer_angle": 0,
			"last_angle": 0,
			"ir_left": 6,
			"ir_center": 6,
			"ir_right": 6,
			"on_track" : False,
			"last_command": "STATUS",
			"braking" : False,
			"moving" : False,

		}
		self.status_lock = Lock()
		self.distance = 0.0
		self.distance_lock = Lock()
		self.stop = False

	def update_distance(self):
		#self.distance, self.distance_lock, self.rpi
		with self.distance_lock:
			self.distance = round(self.rpi.measure_distance(), 2)

	def update_status(self):
		if self.arduino.ser.is_open:
			response = self.arduino.get_status()
			if isinstance(response, dict):
				with self.status_lock:
					self.status.update(response)
					if self.get_speed() == 0:
						self.status.update({'moving': False})
					else:
						self.status.update({'moving': True})
					
					if self.get_ir_center() < 35:
						self.status.update({'on_track': True})
					else:
						self.status.update({'on_track': False})
			else:
				print("La risposta da Arduino non è un dizionario valido.")
				# Puoi gestire il caso in cui la risposta non è un dizionario valido

					
	def get_distance(self):
		self.distance, self.distance_lock

		with self.distance_lock:
			return self.distance

	def get_status(self):
		self.status, self.status_lock

		with self.status_lock:
			return self.status

	def get_speed(self):
		return int(self.status['speed'])
	
	def get_ir_left(self):
		return int(self.status['ir_left'])
	
	def get_ir_center(self):
		return int(self.status['ir_center'])
	
	def get_ir_right(self):
		return int(self.status['ir_right'])
	
	def start_path(self):
		self.path_thread = threading.Thread(target=self.start)
		self.path_thread.start()

	def stop_path(self):
		self.stop = True
		self.arduino.stop()
		self.path_thread.join()  # Attendere che il thread si completi

	def start(self):
		while not self.stop:
			if self.distance > 10:
				avviato = False
				onTrack = False
				if self.get_ir_center() > 35:
					onTrack = True
					if not avviato:
						avviato = True
						self.arduino.speed(50)
				else:
					if self.get_ir_left() > 35:
						onTrack = False
						self.arduino.turn_right(20)
					elif self.get_ir_right() > 35:
						onTrack = False
						self.arduino.turn_left(20)
					time.sleep(0.1)
			else:
				self.arduino.stop()
			time.sleep(0.2)

			


		