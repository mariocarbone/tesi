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
		self.status_lock = Lock()
		self.distance = 0.0
		self.distance_lock = Lock()
		self.stop = 0
		self.turn_min = 0
		self.turn_max = 100
		self.turn_step = 10
		self.on_track = 0
		self.moving = 0
		
		self.status = {
			"speed": 45,
			"speed_left_side": 40,
			"speed_right_side": 50,
			"steer_side_value": 30,
			"steer_side": "left",
			"line_following_mode": 0,
			"ir_left": 0,
			"ir_center": 1,
			"ir_right": 0,
			"on_track": 1,
			"distance": 25,
			"stopped": 0,
			"braking": 0,
			"moving": 0,
			"object_in_front": 0,
			"last_command": "STATUS"
		}

	def update_status(self):
		if self.arduino.ser.is_open:
			response = self.arduino.get_status()
			if isinstance(response, dict):
				self.status.update(response)
			else:
				print("Lo stato di Arduino non è un dizionario valido.")

	def alert_to_controls(self,alert):
		print(alert)
		