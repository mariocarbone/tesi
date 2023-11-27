import paho.mqtt.client as mqtt
import json
import time

class MQTTConnection:

	def __init__(self, broker_address, port, topic_alert, topic_auto, topic_rsu, rsu_id):
		self.broker = broker_address
		self.port = port
		self.topic_alert = topic_alert
		self.topic_auto = topic_auto
		self.topic_rsu = topic_rsu
		self.rsu_id = rsu_id
		self.client = mqtt.Client(rsu_id)
		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message
		self.client.connect(broker_address, port)
		self.client.loop_start()

	def on_connect(self, client, userdata, flags, rc):
		print("<MQTT> Connesso al broker MQTT: <code: " + str(rc) + ">")
		client.subscribe(self.topic_alert + '/+')

	def on_message(self, client, userdata, message):
		if message.topic.startswith("/alert"):
			payload = json.loads(message.payload)
			if payload["creator_id"] == self.rsu_id:
				pass 
			else:
				creator = payload["creator_id"]
				t_arrival = time.time()*1000 
				t_trasm = payload["t_creation"]*1000
				t_total_ms = round(t_arrival - t_trasm)
				print("<Ricevuto Alert> da", creator, " - Tempo impiegato:", t_total_ms , " ms")
				payload["t_travel"]= t_total_ms
				self.manage_alert(payload)
			
			#print("<Alert> Ricevuto Alert")
			#payload = json.loads(message.payload)
			#print(payload)
			#self.manage_alert(payload)
			# alert_id = payload["id"]
			# alert[alert_id] = payload

	def handle_message(self, topic, message):
		if message.topic.startswith("/smartcar"):
			payload = json.loads(message.payload)
			vehicle_id = payload["id"] 
			if payload["rsu_id"] == self.rsu_id:
				veicoli_connessi[vehicle_plate] = payload

	def send_vehicle_status(self,vehicle_info):
		vehicle_info_json = json.dumps(vehicle_info)
		self.client.publish(self.topic_auto + "/info", vehicle_info_json)

	def send_alert(self, alert):
		alert_json = json.dumps(alert)
		self.client.publish(self.topic_alert + "/" + self.rsu_id , alert_json)

	def manage_alert(self, payload):
		if self.on_alert_callback:
			self.on_alert_callback(payload)