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
			if response:
				try:
					stato_arduino = json.loads(response)
					with self.status_lock:
						self.status.update(stato_arduino)
						if int(self.status.get('speed', 0)) == 0:
							self.status.update({'moving': False})
						else:
							self.status.update({'moving': True})
				except json.JSONDecodeError as e:
					print(f"Errore nella decodifica JSON: {e}")
					
	def get_distance(self):
		self.distance, self.distance_lock

		with self.distance_lock:
			return self.distance

	def get_status(self):
		self.status, self.status_lock

		with self.status_lock:
			return self.status
		
	def start_path(self):
		while self.stop:
			if self.distance > 10:
				self.arduino.speed(50)

			if int(self.status['ir_center']) > 35:
				print("SULLA TRACCIA")
			elif int(self.status['ir_center']) < 35 :
				if int(self.status['ir_left']) > 35 :
					self.arduino.turn_right(20)
				elif int(self.status['ir_right']) > 35 :
					self.arduino.turn_left(20)

	def stop_path(self):
		self.stop = True
		self.arduino.stop()