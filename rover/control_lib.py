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
			"last_command": "STATUS",
			"braking" : False,
			"moving" : False,

		}

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
	
	def get_steer(self):
		return int(self.status['steer_angle'])
	
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

	def get_side_by_steer(steer_angle):
		if steer_angle < 50:
			return "LEFT"
		elif steer_angle == 50:
			return "CENTER"
		else :
			return "RIGHT"
		
	def get_active_ir(self):
		if self.get_ir_left > 35:
			return "LEFT"
		elif self.get_ir_right > 35:
			return "RIGHT"
		elif self.get_ir_center > 35:
			return "CENTER"
	
	def start(self):
		while not self.stop:
			if self.distance > 10:
				if self.get_active_ir() == "CENTER":  #Sto sulla linea centrale
					self.on_track = True

					if not self.moving:
						self.arduino.speed(50)
						self.moving = True
				else:
					if self.get_active_ir() == "LEFT": #Sto sulla linea da sinistra

						self.on_track = False
						line_found = self.find_line("LEFT")
						if line_found:
							self.on_track = True

					elif self.get_active_ir() == "RIGHT": #Sto sulla linea da destra

						self.on_track = False
						line_found = self.find_line("RIGHT")
						if line_found:
							self.on_track = True

			else: #Distanza di sicurezza
				self.on_track = False
				self.arduino.stop()

			time.sleep(0.5)

			
	def find_line(self,side):
		if side == "LEFT":
			if self.get_steer() < self.turn_max:
				self.arduino.steer(self.steer_value+self.turn_step)
				time.sleep(0.2)
				if self.get_active_ir() == "CENTER":
					return True
				else:
					self.find_line("LEFT")

		elif side == "RIGHT":
			if self.get_steer() > self.turn_min:
				self.arduino.steer(self.steer_value+self.turn_step)
				time.sleep(0.2)
				if self.get_active_ir() == "CENTER":
					return True
				else:
					self.find_line("RIGHT")
