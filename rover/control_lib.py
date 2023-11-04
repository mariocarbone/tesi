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

	def update_distance(self):
		#self.distance, self.distance_lock, self.rpi
		with self.distance_lock:
			self.distance = round(self.rpi.measure_distance(), 2)

	def update_status(self):

		if self.arduino.ser.is_open:
			with self.status_lock:
				
				response = self.arduino.get_status()
				if response:
					try:
						self.status.update(json.loads(response))
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