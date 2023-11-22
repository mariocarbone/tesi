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
		self.status_lock = Lock()
		self.distance = 0.0
		self.distance_lock = Lock()
		self.stop = False
		self.turn_min = 0
		self.turn_max = 100
		self.turn_step = 10
		self.on_track = False
		self.moving = False
		self.status = {
			"speed": 0,
			"speed_left_side": 0,
			"speed_right_side": 0,
			"steer_angle": 50,
			"last_angle": 0,
			"ir_left": 6,
			"ir_center": 6,
			"ir_right": 6,
			"on_track" : False,
			"braking" : False,
			"moving" : False,
			"distance" : 0,
			"last_command": "STATUS"
		}

	def update_status(self):
		if self.arduino.ser.is_open:
			response = self.arduino.get_status()
			if isinstance(response, dict):
				self.status.update(response)
			else:
				print("Lo stato di Arduino non è un dizionario valido.")

	def handle_prediction(self, predictions):
		print(predictions)

	def handle_alert(self,alert):
		print(alert)
		