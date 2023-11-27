from threading import Lock
import threading
import time
import json
from rpi_lib import Raspberry
from arduino_lib import Arduino

class Vehicle_Control():

	def __init__(self, raspberry_istance):
		print("Vehicle Control avviato")
		self.arduino = Arduino("/dev/ttyACM0", 9600, 1, 1)
		self.rpi = raspberry_istance
		self.status_lock = Lock()
		self.object_in_front_callback=None
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
				if self.status.get("object_in_front") and callable(self.object_in_front_callback):
					if(self.status["object_in_front"]) == 1:
						self.object_in_front_callback()
			else:
				print("Lo stato di Arduino non è un dizionario valido.")

	def alert_to_controls(self,alert):
		type = alert['type']
		if(type == "person"):
			if "connected_RSU" in alert:
				rsu_alert = alert["connected_RSU"]
			else:
				rsu_alert = alert["creator_id"]
			
			rsu = self.rpi.system_status["ap_connected"]
			t_creation = alert["t_creation"]
			t_travel_s = alert["t_travel"]/1000

			if(rsu_alert == rsu):
				distance = self.rpi.system_status["ap_distance"]

			else:
				rsu_distance = self.rpi.system_status["other_aps"].get(rsu_alert)
				if rsu_distance is not None:
					distance = rsu_distance
				else:
					distance = 0

			speed_ms = self.status.get('speed',0)*0.003
			t_remain = self.calc_time_to_reach(t_creation, speed_ms, distance)
			
			if(t_remain == -1):
				print("<Vehicle Control> continuo a marciare, rover fermo o distanza superiore a 10")
			elif(t_remain > 1):
				print("<Vehicle Control> raggiungo l'obiettivo e fermo il rover in ", t_remain, "secondi")
				wait_and_stop_thread = threading.Thread(target=self.wait_then_brake, args=(t_remain,))
				wait_and_stop_thread.start()
			else:
				print("<Vehicle Control> faccio rallentare il rover alla velocità minima")
				self.arduino.speed(70) #Imposto la velocità minima per far marciare il rover			
				
		elif(type == "undefined"):
			print("<Vehicle Control> faccio rallentare il rover alla velocità minima")
			self.arduino.speed(70) #Imposto la velocità minima per far marciare il rover

		elif(type == "vehicle_stopped"):
			print("<Vehicle Control> faccio rallentare il rover alla velocità minima")
			self.arduino.speed(70) #Imposto la velocità minima per far marciare il rover	


	def calc_time_to_reach(self, t_creation, speed, distance):
		t_now = time.time()
		t_elapsed_since_creation = t_now - t_creation

		distance_travelled = speed * t_elapsed_since_creation
		
		remaining_distance = max(distance - distance_travelled, 0)

		t_remain = remaining_distance / speed if speed > 0 else -1
		#Se il veicolo è fermo allora non considero di raggiungere l'oggetto

		if(distance == 0 or distance > 10):
			t_remain = -1

		return t_remain

	def wait_then_brake(self, time_to_wait):
		time.sleep(time_to_wait)
		print("<Rover> ho aspettato", time_to_wait, "secondi e ora mi fermo")
		self.arduino.stop()

	def start_self_driving(self, speed):
		self.arduino.start_self_driving(speed)

	def stop_self_driving(self):
		self.arduino.stop_self_driving()
		