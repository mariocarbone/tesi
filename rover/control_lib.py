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

	def update_dis(self):
		distance_thread = threading.Thread(target=update_distance)
		distance_thread.start()
		distance_thread.join()

	def update_distance(self):
		while not self.stop:
			self.distance = self.rpi.measure_distance()
			print("Ho misurato la distanza",self.distance)

	def update_status(self):
		if self.arduino.ser.is_open:
			response = self.arduino.get_status()
			if isinstance(response, dict):
				self.status.update(response)
			else:
				print("Lo stato di Arduino non è un dizionario valido.")

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
		if self.get_ir_left() > 35:
			return "LEFT"
		elif self.get_ir_right() > 35:
			return "RIGHT"
		elif self.get_ir_center() > 35:
			return "CENTER"
	
	def start(self):
		while not self.stop:
			if self.distance > 20:
				if self.get_active_ir() == "CENTER":  #Sto sulla linea centrale
					self.on_track = True
					if not self.get_steer() == 50: 
						self.arduino.steer(50)

					if not self.moving:
						self.arduino.speed(80)
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
				if (self.moving):
					self.arduino.stop()
					self.moving = False


			
	def find_line(self,side):
		if side == "LEFT":
			if self.get_steer() < self.turn_max:
				if self.get_active_ir() == "CENTER":
					self.arduino.steer(50)
					return True
				else:
					self.arduino.steer(self.get_steer()+self.turn_step)
					self.find_line("LEFT")

		elif side == "RIGHT":
			if self.get_steer() > self.turn_min:
				if self.get_active_ir() == "CENTER":
					self.arduino.steer(50)
					return True
				else:
					self.arduino.steer(self.get_steer()-self.turn_step)
					self.find_line("RIGHT")
